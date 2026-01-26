# DeepWiki Agent Strategy

![DeepWiki Strategy](../_assets/deepwiki_banner.png)

## Overview

The DeepWiki Agent Strategy is an AI-powered documentation generator that automatically creates comprehensive wikis for GitHub, GitLab, and Bitbucket repositories. This strategy enables agents to analyze repository structure, understand code relationships, and generate professional documentation with visual diagrams.

## Features

- **Repository Analysis**: Automatically clones and analyzes repository structure
- **Multi-Platform Support**: Works with GitHub, GitLab, and Bitbucket repositories
- **Private Repository Access**: Supports personal access tokens for private repositories
- **Intelligent Documentation**: Generates comprehensive documentation including:
  - Project overview and purpose
  - Installation and setup instructions
  - Usage examples and API documentation
  - Code architecture explanation
  - Contributing guidelines
- **Visual Diagrams**: Optional Mermaid diagram generation for code relationships
- **Configurable Analysis Depth**: Choose between basic, standard, or comprehensive analysis
- **Iterative Processing**: Multi-iteration analysis for thorough understanding

## Configuration

### Required Parameters

- **Model**: LLM model for analysis and generation
- **Tools**: List of available tools for repository analysis
- **Instruction**: Base instruction for documentation generation
- **Repository URL**: GitHub/GitLab/Bitbucket repository URL to analyze
- **Maximum Iterations**: Number of analysis iterations (1-10, default: 5)

### Optional Parameters

- **Access Token**: Personal access token for private repositories
- **Analysis Depth**: Level of analysis depth
  - `basic`: README enhancement and basic structure
  - `standard`: Detailed API docs, setup guides, basic diagrams
  - `comprehensive`: Deep analysis, detailed diagrams, extensive docs
- **Include Diagrams**: Enable/disable Mermaid diagram generation

## Usage

1. **Configure the Strategy**: Set up the DeepWiki strategy in your agent
2. **Provide Repository URL**: Enter the repository URL you want to analyze
3. **Set Analysis Parameters**: Choose your desired analysis depth and options
4. **Add Tools**: Ensure your agent has access to necessary tools for repository analysis
5. **Run Analysis**: The agent will iteratively analyze and generate documentation

## Example Use Cases

### Public Repository Analysis
```
Repository URL: https://github.com/microsoft/autogen
Analysis Depth: standard
Include Diagrams: true
```

### Private Repository with Token
```
Repository URL: https://github.com/company/private-repo
Access Token: ghp_xxxxxxxxxxxxxxxxxxxx
Analysis Depth: comprehensive
Include Diagrams: true
```

### Quick Basic Documentation
```
Repository URL: https://gitlab.com/project/example
Analysis Depth: basic
Include Diagrams: false
Maximum Iterations: 2
```

## Output

The DeepWiki strategy generates structured documentation that includes:

- **Project Overview**: Purpose, features, and key information
- **Technical Documentation**: Installation, usage, and API details
- **Architecture Diagrams**: Visual representation of code structure (if enabled)
- **Setup Instructions**: Step-by-step installation and configuration
- **Contributing Guidelines**: Information for contributors
- **Code Examples**: Practical usage examples

## Tips for Best Results

1. **Choose Appropriate Tools**: Ensure your agent has tools for:
   - Repository cloning/fetching
   - Code analysis
   - File reading
   - Web scraping (for additional context)

2. **Set Reasonable Iterations**: 
   - Use 2-3 iterations for basic documentation
   - Use 4-5 iterations for standard analysis
   - Use 5-8 iterations for comprehensive analysis

3. **Customize Instructions**: Provide specific instructions for:
   - Documentation style preferences
   - Target audience (developers, users, etc.)
   - Specific areas to focus on

4. **Access Tokens**: For private repositories, ensure the token has appropriate read permissions

## Supported Repository Platforms

- **GitHub**: github.com repositories (public and private)
- **GitLab**: gitlab.com repositories (public and private)  
- **Bitbucket**: bitbucket.org repositories (public and private)

## Integration with Dify

The DeepWiki strategy integrates seamlessly with Dify's agent system, providing:

- Real-time streaming output
- Tool integration capabilities
- Usage tracking and logging
- Error handling and validation
- Conversation history management

This strategy is perfect for developers, technical writers, and teams who need to quickly generate comprehensive documentation for their code repositories.