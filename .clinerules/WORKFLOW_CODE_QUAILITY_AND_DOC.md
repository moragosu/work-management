---
description: "Orchestrates AI-assisted code quality validation, documentation generation, and commit message creation workflow"
author: "Production Technology Group"
version: "1.0"
category: "Development Workflow"
tags: ["workflow", "automation", "code-quality", "documentation", "git"]
globs: ["*.*"]
---

# Execute Development Workflow

Orchestrate a complete AI-assisted development workflow that validates code quality, generates documentation, and creates conventional commit messages.

## Workflow Overview

This workflow executes a sequence of AI-assisted tasks to improve code quality and maintainability:

1. **Code Quality Validation** - Validate Python code against PEP 8 and modern Python best practices
2. **Documentation Generation** - Generate comprehensive documentation for improved code understanding
3. **Commit Message Generation** - Create conventional commit messages summarizing all changes

## Workflow Steps

### 1. Code Quality Validation

Execute `prompt/PROMPT_CODE_QUALITY_VALIDATION.md` to analyze and validate code quality:

1. Read and understand all modified Python source files
2. Check for Python 3.10+ syntax compliance and proper type hints
3. Validate PEP 8 naming conventions (snake_case, PascalCase, UPPER_SNAKE_CASE)
4. Assess name clarity and descriptiveness
5. Review logging statements for grammar, clarity, and context
6. Generate structured validation report with actionable suggestions

**User Validation Step:**
Present validation findings to user for approval before implementing changes:
- Highlight critical issues requiring immediate attention
- Explain rationale for each suggested improvement
- Allow user to approve/reject specific changes
- Implement only approved changes

### 2. Documentation Generation

Execute `prompt/PROMPT_DOCUMENTATION.md` to generate comprehensive documentation:

1. Analyze codebase architecture and data flow
2. Generate module-level docstrings for all Python files
3. Create function/class docstrings with parameters, return values, and examples
4. Add inline comments explaining business logic and non-obvious implementation details
5. Update or create README.md with project overview and quick start guide
6. Generate API documentation in docs/API_DOCUMENTATION.md if needed

**Documentation Focus Areas:**
- Complex algorithms (refeed detection, retry grouping, alarm classification)
- Configuration management and environment variables
- Data processing pipelines and transformations
- Error handling and edge case management

### 3. Commit Message Generation and Execution

Execute `prompt/PROMPT_COMMIT_MESSAGE_GENERATION.md` to create and execute conventional commit messages:

1. Analyze all code changes using `git status` and `git diff`
2. Identify change intent (feat, fix, docs, refactor, etc.)
3. Determine appropriate scope (module, component, or file path)
4. Generate commit message following Conventional Commits specification:
   - Clear header with type, scope, and description
   - Detailed body explaining what and why changes were made
   - Footer with issue references if applicable
5. Generate git commit commands for the proposed commit message
6. Present commit message and git commands for user review and approval
7. Execute git commit after user approval

## Execution Workflow

### Phase 1: Analysis and Validation

1. Execute code quality validation on all modified files
2. Present validation report to user for review
3. Wait for user approval of suggested changes
4. Implement only approved code improvements

### Phase 2: Documentation Enhancement

1. Generate comprehensive documentation for all files
2. Add docstrings to modules, classes, and functions
3. Include inline comments for complex business logic
4. Update README.md and API documentation
5. Validate documentation accuracy and completeness

### Phase 3: Commit Preparation and Execution

1. Analyze all changes with git status and git diff
2. Generate conventional commit message summarizing all modifications
3. Include both code improvements and new prompt files
4. Generate git commit commands for the proposed message
5. Present commit message and git commands for user review and approval
6. Execute git commit after user confirmation

## Expected Outcomes

### Code Quality Improvements
- Modern Python 3.10+ syntax compliance
- Complete type hint coverage for all functions
- PEP 8 naming convention adherence
- Clear, descriptive variable and function names
- Grammatically correct logging messages with proper context

### Documentation Enhancements
- Comprehensive module and function docstrings
- Clear inline comments explaining business logic
- Updated README with project overview and setup instructions
- API documentation for public interfaces

### Development Workflow Benefits
- Standardized commit messages following Conventional Commits
- Automated code quality checks preventing common issues
- Improved maintainability and developer onboarding experience
- Consistent documentation across the codebase

## Special Considerations

### Change Management
- Only implement code changes approved by the user
- Preserve existing functionality while improving quality
- Maintain backward compatibility unless explicitly intended
- Document any breaking changes in commit messages

### Workflow Customization
- Allow user to skip specific steps if not needed
- Support partial execution for focused improvements
- Enable iterative execution for large codebases
- Provide progress feedback during long operations

## Output

Generate workflow execution as:

1. **Code Quality Report** - Structured validation findings with line-specific suggestions
2. **Documentation Updates** - Enhanced source files with docstrings and inline comments
3. **Commit Message and Commands** - Conventional commit message with git commit commands
4. **Executed Commit** - Git commit executed after user approval

Ensure the workflow:
- Maintains code functionality while improving quality
- Follows established best practices for Python development
- Produces clear, informative documentation
- Generates meaningful, standardized commit messages
- Requires user validation for code modifications