import json
import time
from collections.abc import Generator
from copy import deepcopy
from typing import Any, Optional
from urllib.parse import urlparse

from dify_plugin.entities.agent import AgentInvokeMessage
from dify_plugin.entities.model import ModelFeature
from dify_plugin.entities.model.llm import (
    LLMModelConfig,
    LLMResult,
    LLMResultChunk,
    LLMUsage,
)
from dify_plugin.entities.model.message import (
    AssistantPromptMessage,
    PromptMessage,
    PromptMessageContentType,
    SystemPromptMessage,
    UserPromptMessage,
)
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.interfaces.agent import (
    AgentModelConfig,
    AgentStrategy,
    ToolEntity,
)
from pydantic import BaseModel


class LogMetadata:
    """Metadata keys for logging"""
    STARTED_AT = "started_at"
    PROVIDER = "provider"
    FINISHED_AT = "finished_at"
    ELAPSED_TIME = "elapsed_time"
    TOTAL_PRICE = "total_price"
    CURRENCY = "currency"
    TOTAL_TOKENS = "total_tokens"


class ContextItem(BaseModel):
    content: str
    title: str
    metadata: dict[str, Any]


class DeepWikiParams(BaseModel):
    repository_url: str
    instruction: str | None
    model: AgentModelConfig
    tools: list[ToolEntity] | None
    access_token: str | None = None
    analysis_depth: str = "standard"
    include_diagrams: bool = True
    maximum_iterations: int = 5


class DeepWikiAgentStrategy(AgentStrategy):
    """
    DeepWiki Agent Strategy for automatically generating comprehensive
    documentation for GitHub/GitLab/Bitbucket repositories.
    """
    
    repository_url: str = ""
    instruction: str | None = ""
    
    def _validate_repository_url(self, url: str) -> bool:
        """Validate if the provided URL is a valid repository URL"""
        try:
            parsed = urlparse(url)
            valid_hosts = ['github.com', 'gitlab.com', 'bitbucket.org']
            return (
                parsed.scheme in ['http', 'https'] and
                any(host in parsed.netloc for host in valid_hosts) and
                len(parsed.path.strip('/').split('/')) >= 2
            )
        except Exception:
            return False

    def _get_system_prompt(self, params: DeepWikiParams) -> str:
        """Generate system prompt for DeepWiki analysis"""
        base_instruction = params.instruction or "Generate comprehensive wiki documentation for the repository."
        
        system_prompt = f"""You are DeepWiki, an AI-powered documentation generator. Your task is to analyze the provided repository and create comprehensive wiki documentation.

{base_instruction}

## Analysis Configuration:
- Repository URL: {params.repository_url}
- Analysis Depth: {params.analysis_depth}
- Include Diagrams: {params.include_diagrams}

## Your Responsibilities:
1. **Repository Analysis**: Understand the codebase structure, technologies used, and project purpose
2. **Documentation Generation**: Create clear, comprehensive documentation including:
   - Project overview and purpose
   - Installation and setup instructions
   - Usage examples and API documentation
   - Code architecture explanation
   - Contributing guidelines
3. **Visual Diagrams**: {"Generate Mermaid diagrams to illustrate code relationships, data flow, and architecture" if params.include_diagrams else "Focus on text-based documentation"}
4. **Structured Output**: Organize information in a logical, easy-to-navigate format

## Analysis Depth Guidelines:
- **Basic**: Focus on README enhancement and basic structure documentation
- **Standard**: Include detailed API docs, setup guides, and basic architecture diagrams
- **Comprehensive**: Deep code analysis, detailed diagrams, and extensive documentation

Use the available tools to analyze the repository and gather information needed for documentation generation.
"""
        return system_prompt

    def _get_user_prompt(self, params: DeepWikiParams) -> str:
        """Generate user prompt for repository analysis"""
        return f"""Please analyze the repository at {params.repository_url} and generate comprehensive wiki documentation.

Repository Details:
- URL: {params.repository_url}
- Access Token: {"Provided" if params.access_token else "Not provided (public repository)"}
- Analysis Depth: {params.analysis_depth}
- Include Diagrams: {params.include_diagrams}

Please start by examining the repository structure and then proceed with generating the documentation."""

    @property
    def _system_prompt_message(self) -> SystemPromptMessage:
        return SystemPromptMessage(content=self.instruction)

    @property
    def _user_prompt_message(self) -> UserPromptMessage:
        return UserPromptMessage(content=self.repository_url)

    def _invoke(
        self, parameters: dict[str, Any]
    ) -> Generator[AgentInvokeMessage, None, None]:
        """
        Run DeepWiki agent application
        """
        try:
            deepwiki_params = DeepWikiParams(**parameters)
        except Exception as e:
            yield self.create_text_message(f"Error parsing parameters: {str(e)}")
            return

        # Validate repository URL
        if not self._validate_repository_url(deepwiki_params.repository_url):
            yield self.create_text_message(
                f"Invalid repository URL: {deepwiki_params.repository_url}. "
                "Please provide a valid GitHub, GitLab, or Bitbucket repository URL."
            )
            return

        # Set instance variables
        self.repository_url = deepwiki_params.repository_url
        self.instruction = self._get_system_prompt(deepwiki_params)
        
        # Initialize prompt messages
        history_prompt_messages = deepwiki_params.model.history_prompt_messages
        history_prompt_messages.insert(0, self._system_prompt_message)
        
        # Add user prompt with repository details
        user_content = self._get_user_prompt(deepwiki_params)
        history_prompt_messages.append(UserPromptMessage(content=user_content))

        # Convert tool messages
        tools = deepwiki_params.tools
        tool_instances = {tool.identity.name: tool for tool in tools} if tools else {}
        prompt_messages_tools = self._init_prompt_tools(tools)

        # Initialize model parameters
        stream = (
            ModelFeature.STREAM_TOOL_CALL in deepwiki_params.model.entity.features
            if deepwiki_params.model.entity and deepwiki_params.model.entity.features
            else False
        )
        model = deepwiki_params.model
        stop = (
            deepwiki_params.model.completion_params.get("stop", [])
            if deepwiki_params.model.completion_params
            else []
        )

        # Initialize analysis state
        iteration_step = 1
        max_iteration_steps = deepwiki_params.maximum_iterations
        current_thoughts: list[PromptMessage] = []
        analysis_complete = False
        llm_usage: dict[str, Optional[LLMUsage]] = {"usage": None}
        
        yield self.create_text_message(
            f"🔍 Starting DeepWiki analysis for repository: {deepwiki_params.repository_url}\n"
            f"📊 Analysis depth: {deepwiki_params.analysis_depth}\n"
            f"📈 Include diagrams: {deepwiki_params.include_diagrams}\n\n"
        )

        while not analysis_complete and iteration_step <= max_iteration_steps:
            # Start a new analysis round
            round_started_at = time.perf_counter()
            round_log = self.create_log_message(
                label=f"DeepWiki Analysis Round {iteration_step}",
                data={
                    "repository_url": deepwiki_params.repository_url,
                    "analysis_depth": deepwiki_params.analysis_depth,
                    "iteration": iteration_step,
                },
                metadata={
                    LogMetadata.STARTED_AT: round_started_at,
                },
                status=ToolInvokeMessage.LogMessage.LogStatus.START,
            )
            yield round_log

            yield self.create_text_message(f"\n🔄 **Analysis Round {iteration_step}**\n")

            # Organize prompt messages
            prompt_messages = self._organize_prompt_messages(
                history_prompt_messages=history_prompt_messages,
                current_thoughts=current_thoughts,
            )
            
            # Recalculate LLM max tokens if needed
            if model.entity and model.completion_params:
                self.recalc_llm_max_tokens(
                    model.entity, prompt_messages, model.completion_params
                )

            # Invoke model
            model_started_at = time.perf_counter()
            model_log = self.create_log_message(
                label=f"{model.model} Generation",
                data={},
                metadata={
                    LogMetadata.STARTED_AT: model_started_at,
                    LogMetadata.PROVIDER: model.provider,
                },
                parent=round_log,
                status=ToolInvokeMessage.LogMessage.LogStatus.START,
            )
            yield model_log

            model_config = LLMModelConfig(**model.model_dump(mode="json"))
            chunks: Generator[LLMResultChunk, None, None] | LLMResult = (
                self.session.model.llm.invoke(
                    model_config=model_config,
                    prompt_messages=prompt_messages,
                    stop=stop,
                    stream=stream,
                    tools=prompt_messages_tools,
                )
            )

            tool_calls: list[tuple[str, str, dict[str, Any]]] = []
            response = ""
            tool_call_names = ""
            current_llm_usage = None
            has_tool_calls = False

            if isinstance(chunks, Generator):
                for chunk in chunks:
                    # Check for tool calls
                    if self.check_tool_calls(chunk):
                        has_tool_calls = True
                        tool_calls.extend(self.extract_tool_calls(chunk) or [])
                        tool_call_names = ";".join(
                            [tool_call[1] for tool_call in tool_calls]
                        )

                    # Process content
                    if chunk.delta.message and chunk.delta.message.content:
                        if isinstance(chunk.delta.message.content, list):
                            for content in chunk.delta.message.content:
                                response += content.data
                                yield self.create_text_message(content.data)
                        else:
                            response += str(chunk.delta.message.content)
                            yield self.create_text_message(str(chunk.delta.message.content))

                    # Track usage
                    if chunk.delta.usage:
                        current_llm_usage = chunk.delta.usage

            else:
                # Handle non-streaming response
                if chunks.message and chunks.message.content:
                    if isinstance(chunks.message.content, list):
                        for content in chunks.message.content:
                            response += content.data
                            yield self.create_text_message(content.data)
                    else:
                        response += str(chunks.message.content)
                        yield self.create_text_message(str(chunks.message.content))

                # Check for tool calls in non-streaming mode
                if chunks.message and chunks.message.tool_calls:
                    has_tool_calls = True
                    for tool_call in chunks.message.tool_calls:
                        tool_calls.append((
                            tool_call.id,
                            tool_call.function.name,
                            json.loads(tool_call.function.arguments)
                        ))
                
                current_llm_usage = chunks.usage

            # Update usage tracking
            if current_llm_usage:
                llm_usage["usage"] = current_llm_usage

            # Add response to conversation history
            if response:
                current_thoughts.append(AssistantPromptMessage(content=response))

            # Finish model log
            yield self.finish_log_message(
                log=model_log,
                data={"content": response, "tool_calls": tool_call_names},
                metadata={
                    LogMetadata.STARTED_AT: model_started_at,
                    LogMetadata.FINISHED_AT: time.perf_counter(),
                    LogMetadata.ELAPSED_TIME: time.perf_counter() - model_started_at,
                    LogMetadata.PROVIDER: model.provider,
                    LogMetadata.TOTAL_PRICE: current_llm_usage.total_price if current_llm_usage else 0,
                    LogMetadata.CURRENCY: current_llm_usage.currency if current_llm_usage else "",
                    LogMetadata.TOTAL_TOKENS: current_llm_usage.total_tokens if current_llm_usage else 0,
                },
            )

            # Execute tool calls if any
            if tool_calls and tool_instances:
                for tool_call_id, tool_name, tool_call_args in tool_calls:
                    if tool_name not in tool_instances:
                        continue

                    # Execute tool call
                    tool_call_log = self.create_log_message(
                        label=f"Tool: {tool_name}",
                        data={
                            "tool_name": tool_name,
                            "arguments": tool_call_args,
                        },
                        metadata={
                            LogMetadata.STARTED_AT: time.perf_counter(),
                        },
                        parent=round_log,
                        status=ToolInvokeMessage.LogMessage.LogStatus.START,
                    )
                    yield tool_call_log

                    try:
                        tool_result = self.session.tool.invoke(
                            provider_type=tool_instances[tool_name].provider_type,
                            provider=tool_instances[tool_name].identity.provider,
                            tool_name=tool_name,
                            parameters=tool_call_args,
                        )

                        if tool_result:
                            tool_response = ""
                            for result_chunk in tool_result:
                                if result_chunk.type == ToolInvokeMessage.MessageType.TEXT:
                                    tool_response += result_chunk.message
                                elif result_chunk.type == ToolInvokeMessage.MessageType.JSON:
                                    tool_response += json.dumps(result_chunk.message, ensure_ascii=False)

                            # Add tool result to conversation
                            current_thoughts.append(
                                AssistantPromptMessage(
                                    content=f"Tool {tool_name} result: {tool_response}"
                                )
                            )

                            yield self.finish_log_message(
                                log=tool_call_log,
                                data={
                                    "tool_name": tool_name,
                                    "result": tool_response[:500] + "..." if len(tool_response) > 500 else tool_response,
                                },
                                metadata={
                                    LogMetadata.FINISHED_AT: time.perf_counter(),
                                    LogMetadata.ELAPSED_TIME: time.perf_counter() - tool_call_log.metadata.get(LogMetadata.STARTED_AT, 0),
                                },
                            )

                    except Exception as e:
                        yield self.finish_log_message(
                            log=tool_call_log,
                            data={
                                "tool_name": tool_name,
                                "error": str(e),
                            },
                            metadata={
                                LogMetadata.FINISHED_AT: time.perf_counter(),
                                LogMetadata.ELAPSED_TIME: time.perf_counter() - tool_call_log.metadata.get(LogMetadata.STARTED_AT, 0),
                            },
                        )

            # Finish round log
            yield self.finish_log_message(
                log=round_log,
                data={
                    "iteration": iteration_step,
                    "tool_calls": len(tool_calls),
                    "has_response": bool(response),
                },
                metadata={
                    LogMetadata.FINISHED_AT: time.perf_counter(),
                    LogMetadata.ELAPSED_TIME: time.perf_counter() - round_started_at,
                },
            )

            # Check if analysis is complete
            if not has_tool_calls or iteration_step == max_iteration_steps:
                analysis_complete = True
                if iteration_step == max_iteration_steps and not analysis_complete:
                    yield self.create_text_message(
                        f"\n⚠️ Reached maximum iterations ({max_iteration_steps}). "
                        "Analysis completed with available information.\n"
                    )
            
            iteration_step += 1

        # Final summary
        yield self.create_text_message(
            f"\n✅ **DeepWiki Analysis Complete**\n"
            f"📊 Total iterations: {iteration_step - 1}\n"
            f"🎯 Repository: {deepwiki_params.repository_url}\n"
        )

        # Return execution metadata
        yield self.create_json_message(
            {
                "execution_metadata": {
                    LogMetadata.TOTAL_PRICE: llm_usage["usage"].total_price
                    if llm_usage["usage"] is not None
                    else 0,
                    LogMetadata.CURRENCY: llm_usage["usage"].currency
                    if llm_usage["usage"] is not None
                    else "",
                    LogMetadata.TOTAL_TOKENS: llm_usage["usage"].total_tokens
                    if llm_usage["usage"] is not None
                    else 0,
                }
            }
        )

    def _clear_user_prompt_image_messages(
        self, prompt_messages: list[PromptMessage]
    ) -> list[PromptMessage]:
        """
        As for now, gpt supports both fc and vision at the first iteration.
        We need to remove the image messages from the prompt messages at the first iteration.
        """
        prompt_messages = deepcopy(prompt_messages)

        for prompt_message in prompt_messages:
            if isinstance(prompt_message, UserPromptMessage) and isinstance(
                prompt_message.content, list
            ):
                prompt_message.content = "\n".join(
                    [
                        content.data
                        if content.type == PromptMessageContentType.TEXT
                        else "[image]"
                        if content.type == PromptMessageContentType.IMAGE
                        else "[file]"
                        for content in prompt_message.content
                    ]
                )

        return prompt_messages

    def _organize_prompt_messages(
        self,
        history_prompt_messages: list[PromptMessage],
        current_thoughts: list[PromptMessage],
    ) -> list[PromptMessage]:
        """
        Organize prompt messages for DeepWiki analysis.
        Combines history messages with current thoughts and clears image messages after first iteration.
        """
        prompt_messages = [
            *history_prompt_messages,
            *current_thoughts,
        ]
        if len(current_thoughts) != 0:
            # clear messages after the first iteration
            prompt_messages = self._clear_user_prompt_image_messages(prompt_messages)
        return prompt_messages