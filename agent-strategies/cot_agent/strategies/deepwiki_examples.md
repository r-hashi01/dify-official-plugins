# DeepWiki Agent Strategy - Usage Examples

This document provides practical examples of how to use the DeepWiki agent strategy in different scenarios.

## Example 1: Analyzing a Public Repository

### Configuration
```yaml
strategy: deepwiki
parameters:
  repository_url: "https://github.com/microsoft/autogen"
  analysis_depth: "standard"
  include_diagrams: true
  maximum_iterations: 5
  instruction: "Generate comprehensive documentation for this multi-agent conversation framework"
```

### Expected Output
The agent will generate documentation including:
- Project overview and multi-agent capabilities
- Installation and setup instructions
- Usage examples for different agent types
- Architecture diagrams showing agent interactions
- API documentation for key classes

## Example 2: Private Repository Analysis

### Configuration
```yaml
strategy: deepwiki
parameters:
  repository_url: "https://github.com/company/private-repo"
  access_token: "ghp_xxxxxxxxxxxxxxxxxxxx"
  analysis_depth: "comprehensive"
  include_diagrams: true
  maximum_iterations: 8
  instruction: "Create detailed internal documentation focusing on API endpoints and database schema"
```

### Use Case
Perfect for internal company repositories where you need:
- Detailed API documentation
- Database schema documentation
- Internal code architecture explanation
- Developer onboarding guides

## Example 3: Quick Documentation for Small Projects

### Configuration
```yaml
strategy: deepwiki
parameters:
  repository_url: "https://gitlab.com/user/small-project"
  analysis_depth: "basic"
  include_diagrams: false
  maximum_iterations: 2
  instruction: "Create a simple README and basic usage guide"
```

### Use Case
Ideal for:
- Small utility projects
- Quick documentation needs
- Projects that need basic setup instructions
- Open source projects needing contribution guidelines

## Example 4: Academic/Research Repository

### Configuration
```yaml
strategy: deepwiki
parameters:
  repository_url: "https://github.com/research-lab/algorithm-implementation"
  analysis_depth: "comprehensive"
  include_diagrams: true
  maximum_iterations: 6
  instruction: "Generate academic-style documentation explaining the algorithms, their complexity, and experimental setup"
```

### Expected Features
- Algorithm explanation with complexity analysis
- Mathematical notation and formulas
- Experimental setup and results interpretation
- Citation and reference information
- Research methodology documentation

## Example 5: Multi-language Project

### Configuration
```yaml
strategy: deepwiki
parameters:
  repository_url: "https://bitbucket.org/team/polyglot-project"
  analysis_depth: "standard"
  include_diagrams: true
  maximum_iterations: 7
  instruction: "Document this multi-language project, explaining the interaction between Python backend, React frontend, and Go microservices"
```

### Special Considerations
- Explains interactions between different language components
- Provides setup instructions for each technology stack
- Documents API contracts between services
- Creates architecture diagrams showing service relationships

## Required Tools

To use the DeepWiki strategy effectively, ensure your agent has access to these types of tools:

### Essential Tools
- **Repository Access Tools**: For cloning/fetching repository content
- **File Reading Tools**: For analyzing code files and documentation
- **Web Scraping Tools**: For gathering additional context from project pages

### Recommended Tools
- **Code Analysis Tools**: For understanding code structure and dependencies
- **Documentation Generation Tools**: For formatting and structuring output
- **Diagram Generation Tools**: For creating visual representations

### Optional Tools
- **API Testing Tools**: For validating API endpoints mentioned in code
- **Package Manager Tools**: For understanding dependencies
- **CI/CD Integration Tools**: For analyzing build and deployment processes

## Best Practices

### 1. Choose Appropriate Analysis Depth
- **Basic**: For simple projects or quick documentation needs
- **Standard**: For most professional projects
- **Comprehensive**: For complex projects or when creating detailed technical documentation

### 2. Set Reasonable Iteration Limits
- **2-3 iterations**: Basic analysis and documentation
- **4-5 iterations**: Standard comprehensive analysis
- **6-8 iterations**: Deep analysis for complex projects
- **8+ iterations**: Only for very large or complex systems

### 3. Customize Instructions
Provide specific instructions based on your needs:
- Target audience (developers, users, stakeholders)
- Documentation style (technical, user-friendly, academic)
- Specific areas to focus on
- Required sections or formats

### 4. Access Token Management
For private repositories:
- Use personal access tokens with minimal required permissions
- Ensure tokens have read access to repositories
- Consider using organization tokens for team repositories
- Regularly rotate access tokens for security

## Troubleshooting

### Common Issues

**Repository Access Denied**
- Verify the repository URL is correct
- Check if repository is public or if access token is provided
- Ensure access token has correct permissions

**Analysis Too Shallow**
- Increase the analysis depth setting
- Add more iterations
- Provide more specific instructions
- Ensure adequate tools are available

**Diagram Generation Fails**
- Check if include_diagrams is set to true
- Verify the agent has access to diagram generation tools
- Simplify the repository structure if too complex

**Incomplete Documentation**
- Increase maximum iterations
- Provide more detailed instructions
- Ensure all necessary tools are available
- Check if repository has sufficient documentation to analyze

### Performance Tips

1. **Start with Standard Analysis**: Begin with standard depth and adjust based on results
2. **Use Appropriate Tools**: Ensure your agent has the right tools for the repository type
3. **Batch Similar Repositories**: Use consistent settings for similar projects
4. **Monitor Token Usage**: Keep track of API usage for cost management