---
description: "Guides AI to generate comprehensive, well-structured documentation for existing code"
author: "Production Technology Group"
version: "2.0"
category: "Documentation"
tags: ["documentation", "readme", "api-docs", "comments"]
globs: ["*.*"]
---

# Create Documentation

Generate clear, accurate, and useful documentation that helps developers understand the codebase quickly.

## Documentation Approach

1. **Read Before Writing** — Analyze the code thoroughly before documenting. Understand:
   - Overall architecture and design patterns
   - Data flow and component interactions
   - Key business logic and domain rules
   - Configuration and dependency management

2. **Audience Awareness** — Write for developers who will maintain or use this codebase. Assume they're competent but unfamiliar with this specific codebase.

3. **Accuracy Over Completeness** — Document fewer things correctly than everything superficially. Never guess — if something is unclear, say so.

## README Generation

When creating or updating a README, include:

- **Project Title & Description** — What it does in 1-2 sentences
- **Quick Start** — Minimal steps to get running (install, configure, run)
- **Architecture Overview** — High-level description of how the system is organized, with a diagram if it would help
- **Key Concepts** — Domain terms or abstractions a new developer needs to understand
- **Configuration** — Environment variables, config files, and their options
- **Development** — How to set up a dev environment, run tests, and contribute

Keep it scannable. Use headings, code blocks, and bullet points.

## API Documentation

For functions, classes, and modules:

- **Purpose** — What it does and when to use it
- **Parameters** — Name, type, description, and whether required or optional
- **Return Value** — Type and description
- **Errors** — What can go wrong and how errors are communicated
- **Example** — A minimal, working usage example

## Inline Comments

Add comments that explain **why**, not **what**:

**✅ Good comments:**
```python
# Retry up to 3 times because the upstream API is flaky during deploys
max_retries = 3

# Use connection pooling because creating new connections is expensive
pool = ConnectionPool(max_connections=10)

# Filter to production lines only to exclude test/dev data
lines = df[df.line_type == 'PRODUCTION']
```

**❌ Bad comments:**
```python
# Set max retries to 3
# Create connection pool
# Filter data
```

Focus comments on:
- Non-obvious business logic or domain rules
- Workarounds with context on why they're needed
- Performance-critical sections explaining the optimization
- Complex algorithms with a brief explanation of the approach
- Conciseness for simple implementations (30 lines or less)

## Docstring Guidelines

**For simple functions (≤10 lines):**
Keep docstrings concise (1-3 lines). Focus on purpose only.

Example:
```python
def clear_data() -> int:
    """
    Clear existing data from the API before uploading new data.
    
    Returns:
        int: HTTP status code from the clear operation
    """
```

**For complex functions (>10 lines):**
Include comprehensive docstrings with:
- Purpose and behavior
- All parameters with descriptions
- Return value details
- Exceptions raised
- Usage examples
- Implementation notes for non-obvious logic

Example:
```python
def process_data(data: DataFrame) -> DataFrame:
    """
    Main pipeline for processing data.
    
    Orchestrates the complete workflow through multiple stages:
    1. Clean and normalize raw data
    2. Filter to production-quality records
    3. Transform and enrich features
    4. Aggregate metrics
    
    Args:
        data: Raw DataFrame with columns including field1, field2, field3
    
    Returns:
        DataFrame: Processed metrics with columns:
            - id: Unique identifier
            - metric1: Aggregated metric value
            - metric2: Another aggregated value
    
    Example:
        >>> results = process_data(raw_data)
        >>> print(results.head())
    """
```

## Language Consistency

Ensure all documentation is in a single language:
- Docstrings should be consistent (all English or all project language)
- Comments should match the chosen language
- Variable/function descriptions in docstrings should match
- If translating, translate everything consistently

## Documentation Consistency Checklist

Verify consistency across all documentation:

- [ ] Module-level docstrings exist and are accurate
- [ ] Function/class docstrings follow consistent format
- [ ] Parameter descriptions are complete and clear
- [ ] Return value descriptions are accurate
- [ ] Example code is runnable and tested
- [ ] Inline comments explain "why" not "what"
- [ ] Configuration is properly documented

## Documentation Files

Create/update these files:

1. **README.md** - Main project documentation
2. **docs/API_DOCUMENTATION.md** - Comprehensive API reference (optional for larger projects)

## Code Quality Checks

After documentation:
- [ ] All docstrings match implementation
- [ ] No misleading or inaccurate documentation
- [ ] Short functions have concise docstrings
- [ ] Complex functions have comprehensive docstrings
- [ ] Comments explain "why" not "what"
- [ ] Examples are accurate and runnable
- [ ] Consistent formatting across all files

## Special Considerations

- **Async/concurrent operations**: Document async behavior and concurrency control
- **Configuration classes**: Document validation rules and default values
- **Database/storage operations**: Document connection handling and error cases
- **Date/time calculations**: Document timezone handling and edge cases
- **External API calls**: Document retry logic, timeouts, and error handling

## Output

Generate documentation as:
1. Updated source files with consistent docstrings and comments
2. Comprehensive `README.md` with project overview
3. `docs/API_DOCUMENTATION.md` with API reference (if needed for larger projects)

Ensure all documentation is:
- Production-ready and accurate
- Helps new developers understand the codebase quickly
- Matches the actual implementation
- Appropriate for the function's complexity