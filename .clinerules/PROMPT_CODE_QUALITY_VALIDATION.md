---
description: "Guides AI to validate Python code quality including naming conventions and logging statements"
author: "Production Technology Group"
version: "1.0"
category: "Code Quality"
tags: ["python", "pep8", "code-review", "logging", "type-hints"]
globs: ["*.py"]
---

# Validate Code Quality

Review and validate Python code for readability, consistency, and accuracy following PEP 8 style guide and Python 3.10+ best practices.

## Validation Approach

1. **Analyze Before Suggesting** — Examine the code thoroughly before suggesting changes. Understand:
   - The purpose and context of functions and classes
   - Data flow and variable relationships
   - Business logic and domain rules
   - How logging messages are used in the application

2. **Focus on Clarity** — Prioritize changes that improve code understanding:
   - Make variable names self-documenting
   - Ensure logging messages are clear and grammatically correct
   - Use modern Python syntax where appropriate
   - Maintain consistency across the codebase

3. **Accuracy Over Style** — Suggest fewer meaningful improvements than many superficial changes. Never suggest changes that might introduce bugs.

4. **Safe Command Execution** — Follow AGENT.md guidelines for all git and file operations:
   - Use `timeout 10` to prevent hanging processes
   - Use `--no-pager --no-color` for git commands
   - Prefer `read_file` tool over command output
   - Save large outputs to `/tmp/` files and limit with `head`

## Validation Criteria

### 1. Python 3.10+ Syntax and Type Hints

Ensure code leverages modern Python features and proper type annotations.

**Modern Syntax:**
- Use `match-case` statements instead of complex if-elif chains
- Use `|` union syntax instead of `typing.Union`
- Use `typing.Self` for self-referential type hints
- Use parametrized generics (e.g., `list[str]` instead of `List[str]`)

**Type Hints:**
- All function parameters must have type hints
- All return values must have type hints
- Use `Optional[T]` or `T | None` for nullable types
- Be specific (avoid `Any` when possible)

✅ **Good:**
```python
from typing import Self

def get_user(user_id: int) -> User | None:
    """Retrieve user by ID or return None if not found."""
    if user_id <= 0:
        return None
    return User(id=user_id)

def process_data(data: dict[str, int]) -> list[int]:
    """Extract and return values from data dictionary."""
    return list(data.values())
```

❌ **Bad:**
```python
# Missing type hints
def get_user(user_id):
    return User(id=user_id)

# Using old Union syntax
from typing import Union
def get_user(user_id: int) -> Union[User, None]:
    pass
```

---

### 2. Naming Conventions (PEP 8)

Follow PEP 8 naming conventions strictly.

**Variables, Functions, Methods:** `snake_case`
```python
user_name = "John"
get_user_data()
calculate_total()
```

**Classes:** `PascalCase` (UpperCamelCase)
```python
class UserDataProcessor:
    class AuthenticationManager:
```

**Constants:** `UPPER_SNAKE_CASE`
```python
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
```

✅ **Good:**
```python
class DataProcessor:
    def process_data(self, input_data: dict) -> dict:
        result = {}
        for key, value in input_data.items():
            result[key] = value * 2
        return result
```

❌ **Bad:**
```python
class dataProcessor:  # Wrong: should be PascalCase
    def ProcessData(self, inputData):  # Wrong: should be snake_case
        Result = {}  # Wrong: variables should be snake_case
        pass
```

---

### 3. Name Clarity

Use descriptive names that clearly indicate purpose and meaning.

**Guidelines:**
- Avoid abbreviations unless widely understood (e.g., `id`, `url`, `http`)
- Avoid generic names like `data`, `temp`, `result`, `obj`
- Use verbs for function names (e.g., `calculate_total` instead of `total`)
- Use nouns for class names
- Be specific about data state or type

✅ **Good:**
```python
# Clear and descriptive
processed_user_data = validate_and_clean(raw_user_input)
failed_login_attempts = count_consecutive_failures(user_id)
authentication_token = generate_jwt_token(user_credentials)

# Meaningful loop variables
for user_record in user_records:
    process_user(user_record)

for index, item in enumerate(items):
    process_item(index, item)
```

❌ **Bad:**
```python
# Too generic or abbreviated
data = validate_and_clean(input)
proc = count_consecutive_failures(uid)
token = gen_jwt(creds)

# Unclear loop variables
for x in list1:
    do_something(x)

for i in range(len(items)):
    process(items[i])
```

---

### 4. Logging Statement Validation

Ensure all logging messages are in English, grammatically correct, and clear.

**Requirements:**
- All log messages must be in English
- Check for grammar and spelling errors
- Use proper capitalization (sentence case)
- Include relevant context (IDs, values, etc.)
- Be consistent in message format
- Use appropriate log levels

**Best Practices:**
- Include what happened (action or event)
- Include why it matters (context)
- Include actionable information if error
- Use placeholders for dynamic values: `"User {} logged in successfully"`

✅ **Good:**
```python
logger.info("User authentication successful. User ID: {}")
logger.warning("Rate limit exceeded for IP: {}. Max requests: {}")
logger.error("Database connection failed. Error: {}")
logger.debug("Processing batch. Items: {}, Offset: {}")
```

❌ **Bad:**
```python
logger.info("User login success. user_id: {}")  # Grammar: capitalize first letter
logger.warning("Rate limit exceed")  # Missing context
logger.error("Database error")  # Too vague, no details
logger.debug("Processing...")  # No useful information
```

**Common Issues to Fix:**

| Issue | Bad | Good |
|-------|-----|------|
| Capitalization | "process complete" | "Processing complete" |
| Articles | "Failed to connect" | "Failed to connect to database" |
| Subject-verb agreement | "The files was processed" | "The files were processed" |
| Typos | "Procesing complete" | "Processing complete" |
| Missing context | "Error occurred" | "Error occurred while uploading file: {}" |

---

## Analysis Workflow

### 1. Identify Files to Analyze

Check git status to identify modified Python files:
```bash
timeout 10 git status --short
```

This command uses timeout protection to prevent hanging.

### 2. Read and Understand Code

**Priority:**
1. Use `read_file` tool to examine file contents directly (preferred for stability)
2. Only use `git diff` when absolutely necessary
3. Exclude artifact files from analysis (uv.lock, pyproject.toml, package-lock.json)
4. Focus on source files (*.py, *.js, *.ts, *.java, etc.)
5. For config/data files (*.yaml, *.csv, *.json), note changes only

**Git Command Rules (when needed):**
- Always use `timeout 10` to prevent hanging
- Add `--no-pager` to prevent pager issues
- Add `--no-color` to remove ANSI codes
- Save diff to file: `timeout 10 git --no-pager --no-color diff <file> > /tmp/diff.txt 2>&1`
- Read saved diff: `read_file /tmp/diff.txt`
- Limit output for large diffs: `head -100 /tmp/diff.txt`

**Recommended Command Sequence:**
```bash
# 1. Check status (with timeout)
timeout 10 git status --short

# 2. Read files directly (preferred approach)
read_file path/to/file.py

# 3. Use git diff only when necessary (with all safeguards)
timeout 10 git --no-pager --no-color diff <file> > /tmp/diff.txt 2>&1 && head -100 /tmp/diff.txt
read_file /tmp/diff.txt
```

Focus on:
- Function and class definitions
- Variable naming patterns
- Logging statements throughout the file
- Type hint usage

### 2. Identify Issues by Category

Check each validation criterion systematically:

**Python 3.10+ & Type Hints:**
- [ ] Functions missing return type hints
- [ ] Parameters missing type hints
- [ ] Old Union syntax (`Union[X, Y]` vs `X | Y`)
- [ ] Opportunities for modern syntax (match-case, etc.)

**Naming Conventions:**
- [ ] Classes not using PascalCase
- [ ] Functions/variables not using snake_case
- [ ] Constants not using UPPER_SNAKE_CASE
- [ ] Inconsistent naming patterns

**Name Clarity:**
- [ ] Generic names (data, temp, result)
- [ ] Excessive abbreviations
- [ ] Unclear purpose or intent
- [ ] Loop variables with vague names

**Logging Statements:**
- [ ] Non-English log messages
- [ ] Grammar or spelling errors
- [ ] Missing context or details
- [ ] Inconsistent formatting

### 3. Prioritize Suggestions

Rank issues by impact:
1. **Critical**: Type hints, naming convention violations
2. **Important**: Unclear names affecting readability
3. **Minor**: Logging message grammar improvements

### 4. Generate Suggested Improvements

Provide clear, actionable suggestions with:
- Line number reference
- Current code snippet
- Suggested improvement
- Rationale for the change

## Output Format

Present validation results in this structured format:

```
---
[Validation Results]

### 1. Python 3.10+ Syntax and Type Hints
- (Line X) `Union[str, int]` -> Suggest using `str | int` for modern Python syntax
- (Line Y) Function `get_data` is missing return type hint -> Add `-> dict[str, Any]`

### 2. Naming Conventions
- (Line X) Class name `my_class` -> Rename to `MyClass` (PascalCase)
- (Line Y) Variable `userID` -> Rename to `user_id` (snake_case)
- (Line Z) Constant `maxRetries` -> Rename to `MAX_RETRIES` (UPPER_SNAKE_CASE)

### 3. Name Clarity
- (Line X) Variable `proc_data` is ambiguous -> Suggest `processed_user_data` or `validated_input`
- (Line Y) Function `calc()` is too abbreviated -> Suggest `calculate_total()` or `compute_metrics()`
- (Line Z) Loop variable `i` has unclear purpose -> Suggest `row_index` or `item_index`

### 4. Logging Statement Validation
- (Line X) "Procesing complete." -> Typo fix: "Processing complete."
- (Line Y) "User login success. user_id: {}" -> Grammar improvement: "User successfully logged in. User ID: {}"
- (Line Z) "Error in database" -> Add context: "Database connection failed. Error: {}"
---
```

## Examples

### Complete Validation Example

**Input Code:**
```python
class dataProc:
    def __init__(self, tmp: Union[str, int]):
        self.tmp = tmp
    
    def proc(self, data):
        result = []
        for i, x in enumerate(data):
            logger.info("Processing item")
            if x > 0:
                result.append(x * 2)
        logger.info("Process complete")
        return result
```

**Validation Output:**
```
---
[Validation Results]

### 1. Python 3.10+ Syntax and Type Hints
- (Line 1) `Union[str, int]` -> Suggest using `str | int` for modern Python syntax
- (Line 4) Method `proc` is missing return type hint -> Add `-> list[int]`
- (Line 4) Parameter `data` is missing type hint -> Add `: list[int]`

### 2. Naming Conventions
- (Line 1) Class `dataProc` -> Rename to `DataProcessor` (PascalCase)
- (Line 2) Attribute `self.tmp` is too abbreviated -> Rename to `self.template` or `self.temp_value`
- (Line 4) Method `proc` -> Rename to `process` (more descriptive)

### 3. Name Clarity
- (Line 5) Variable `result` is generic -> Suggest `processed_items` or `doubled_values`
- (Line 6) Loop variable `i` -> Suggest `index` or `position`
- (Line 6) Loop variable `x` -> Suggest `item` or `value`

### 4. Logging Statement Validation
- (Line 7) "Processing item" -> Add context: "Processing item at index {}"
- (Line 10) "Process complete" -> Grammar: "Processing complete" or "Processing finished successfully"
---
```

### Suggested Refactored Code

```python
class DataProcessor:
    """Processes numeric data by doubling positive values."""
    
    def __init__(self, template: str | int):
        self.template = template
    
    def process(self, data: list[int]) -> list[int]:
        """Double all positive values in the input list."""
        processed_items = []
        for index, value in enumerate(data):
            logger.info(f"Processing item at index {index}")
            if value > 0:
                processed_items.append(value * 2)
        logger.info("Processing complete. Processed {} items".format(len(processed_items)))
        return processed_items
```

## Validation Checklist

Before completing the validation:

- [ ] All function signatures have complete type hints
- [ ] All variable names follow snake_case convention
- [ ] All class names follow PascalCase convention
- [ ] All constant names follow UPPER_SNAKE_CASE convention
- [ ] No ambiguous or overly abbreviated variable names
- [ ] All logging messages are in English
- [ ] All logging messages have proper grammar and spelling
- [ ] Logging messages include relevant context
- [ ] Modern Python 3.10+ syntax is used where applicable
- [ ] Suggestions are clear and actionable

## Special Considerations

- **Legacy Code**: Be respectful of existing conventions when refactoring
- **Third-party Libraries**: Don't suggest changes to external library code
- **Performance**: Consider if naming changes affect performance (unlikely but possible)
- **Test Files**: Be less strict with test code variable names (e.g., `assert result == expected`)
- **Configuration Files**: Validate logic, not configuration values
- **Documentation Strings**: Also check docstrings for grammar and clarity

## Output

Generate validation report as structured output with:
1. Categorized issue list by validation criterion
2. Line number references for each issue
3. Clear before/after comparisons
4. Rationale for each suggestion
5. Prioritized suggestions (critical, important, minor)

Ensure the validation is:
- Constructive and educational
- Focused on clarity and maintainability
- Consistent with PEP 8 and modern Python best practices
- Helpful for improving code quality