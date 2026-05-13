---
description: "Guides AI to generate conventional commit messages from code changes"
author: "Production Technology Group"
version: "1.0"
category: "Git Workflow"
tags: ["git", "commit", "conventional-commits", "changelog"]
globs: ["*.*"]
---

# Generate Git Commit Messages

Generate clear, consistent, and meaningful git commit messages following the Conventional Commits specification.

## Commit Message Approach

1. **Analyze Before Writing** — Examine code changes thoroughly before writing commit messages. Understand:
   - The core intent of changes (new features, bug fixes, refactoring, etc.)
   - Which files and modules were affected
   - The impact on the codebase functionality
   - Any breaking changes or deprecations

2. **Context Awareness** — Incorporate additional context provided by the user:
   - Issue tracker references (e.g., GitHub issue numbers)
   - Pull request descriptions or requirements
   - Specific emphasis on certain changes
   - Business or technical rationale

3. **Accuracy Over Brevity** — A clear, descriptive commit message is better than a vague one. If the intent is unclear, ask for clarification.

4. **Safe Command Execution** — Follow AGENT.md guidelines for all git and file operations to avoid pending issues:
   - Use `timeout 10` to prevent hanging processes
   - Use `--no-pager --no-color` for git commands
   - Prefer `read_file` tool over command output for code analysis
   - Save large outputs to `/tmp/` files and limit with `head`
   - Execute commands one at a time and wait for confirmation

## Commit Message Format

Follow Conventional Commits specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Components

#### Header (Required)

**Type:**
Select the most appropriate type based on change analysis:

- `feat`: New feature addition (e.g., new function, new endpoint, new capability)
- `fix`: Bug fix (e.g., condition change, null handling, edge case fix)
- `docs`: Documentation changes (e.g., .md files, docstring updates, comments)
- `style`: Code style changes (formatting, whitespace, semicolons - no logic change)
- `refactor`: Code refactoring (structural improvement without functionality change)
- `test`: Test code changes (e.g., test files, test utilities)
- `perf`: Performance improvements
- `chore`: Build process, tooling, or dependency changes

**Scope (Optional):**
Specify the module, component, or file path affected:
- Examples: `api`, `login`, `utils.parser`, `app.analyzer`, `config`

**Description:**
Single-sentence summary of changes:
- Use imperative mood ("add" not "added")
- Start with lowercase
- No period at the end
- Keep under 72 characters

#### Body (Optional)

Additional context about the changes:
- Leave a blank line after header
- Explain **why** the change was made
- Describe **what** was changed
- Mention any alternative approaches considered
- Reference related issues or discussions

#### Footer (Optional)

Breaking changes or issue references:
- Leave a blank line after body
- Breaking changes: `BREAKING CHANGE: <description>`
- Issue references: `Closes #123`, `Fixes #456`, `Refs #789`

## Analysis Workflow

### 1. Check Git Status

```bash
timeout 10 git status --short
```

Identify changed files with minimal output.

### 2. Analyze Code Changes

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
# 1. Check status
timeout 10 git status --short

# 2. Read files directly (preferred)
read_file path/to/file.py

# 3. Use git diff only when necessary
timeout 10 git --no-pager --no-color diff --staged <file> > /tmp/diff.txt 2>&1 && head -50 /tmp/diff.txt
read_file /tmp/diff.txt
```

### 3. Identify Change Intent

Analyze the diff to determine:
- **New functions/classes**: `feat` type
- **Bug fixes**: `fix` type
- **Logic improvements**: `refactor` type
- **Documentation updates**: `docs` type
- **Formatting changes**: `style` type
- **Test additions**: `test` type
- **Performance optimizations**: `perf` type
- **Build/config changes**: `chore` type

### 4. Determine Scope

Based on changed files:
- Single module: Use module name (e.g., `analyzer`, `config`)
- Multiple modules: Use parent package (e.g., `app`, `util`)
- Cross-cutting changes: Omit scope or use broad term (e.g., `core`)

### 5. Incorporate User Context

Apply additional context provided:
- Issue numbers for footer
- Specific emphasis for description
- Breaking change warnings
- Technical rationale for body

### 6. Generate Commit Message and Commands

Follow the commit message format and writing rules, then generate git commit commands.

Generate git commit commands in this format:

```bash
# Step 1: Add modified files to staging area
git add <file1> <file2> <file3>

# Step 2: Commit with the proposed message
git commit -m "<commit message>"
```

Or provide a single command alternative:

```bash
git commit -am "<commit message>"
```

### 7. Present for User Approval and Execute

Present the following to the user:
1. The proposed commit message following Conventional Commits format
2. The git commands to execute the commit
3. A workflow summary showing all completed phases

After user confirmation, execute the git commit commands automatically.

## Writing Rules

### Header Rules

✅ **Good:**
```
feat(auth): add JWT token validation

fix(data-loader): handle missing S3 objects gracefully

docs(readme): update installation instructions
```

❌ **Bad:**
```
added JWT validation (wrong type format)

Fix bug in data-loader (capitalized, missing scope)

Update README.md (missing type, unclear scope)
```

### Body Rules

✅ **Good:**
```
Refactored the authentication module to improve maintainability.

Previously, authentication logic was scattered across multiple files.
This change consolidates all auth-related functions into a single
module with clear separation of concerns.

The new structure makes it easier to:
- Add new authentication providers
- Unit test auth logic
- Maintain authentication rules
```

❌ **Bad:**
```
Changed some functions around. Moved code to different files.
```

### Footer Rules

✅ **Good:**
```
BREAKING CHANGE: The API endpoint /api/v1/users has been removed.
Use /api/v2/users instead.

Closes #123
Fixes #456
Refs #789
```

### Breaking Changes

Must include:
- `BREAKING CHANGE:` prefix in footer
- Clear description of what broke
- Migration instructions or alternatives

Example:
```
feat(api): migrate to v2 endpoints

BREAKING CHANGE: Removed support for v1 API endpoints.
All clients must migrate to v2 endpoints by 2024-01-01.
See migration guide: docs/migration-v1-to-v2.md

Closes #123
```

## Examples

### Feature Addition

```
feat(analyzer): add reproducibility rate calculation

Implement new pipeline for calculating defect reproducibility rates.
This helps identify false positives in inspection data and improves
test efficiency.

The algorithm analyzes retest patterns and classifies them as:
- pass: All test results were PASS (no actual defect)
- true: All test results were FAIL (actual defect)
- false: Mixed PASS/FAIL results (intermittent issue)

Reproducibility rate is calculated as: true / (pass + true + false)

Closes #42
```

### Bug Fix

```
fix(s3): handle connection timeout gracefully

Previously, S3 connection timeouts caused the entire job to fail.
Now retries up to 3 times with exponential backoff before giving up.

This improves reliability when S3 is temporarily unavailable or
experiencing high load.

Fixes #156
```

### Documentation Update

```
docs(readme): add API documentation reference

Link to comprehensive API documentation in docs/API_DOCUMENTATION.md.
This provides detailed function signatures, parameters, and examples
for all modules.

Users can now quickly find detailed API information without navigating
the source code directly.
```

### Refactoring

```
refactor(config): centralize configuration loading

Migrate configuration loading to use Pydantic Settings with custom
sources. This provides better type safety and validation.

Previously, config loading was scattered across multiple files with
inconsistent validation. Now all configuration goes through a single
AppSetting class with clear priority order:
1. CLI arguments
2. Environment variables
3. .env file
4. YAML config files
```

### Breaking Change

```
feat(spark): upgrade to Spark 4.0

Update Spark version from 3.5 to 4.0 for improved performance and
new features.

BREAKING CHANGE: Removed support for Python 3.9. Minimum Python version
is now 3.10. Update your runtime environment before upgrading.

Also, the deprecated DataFrame API methods have been removed:
- .persist() is replaced with .cache()
- .unpersist() is replaced with .unpersist()

See upgrade guide: docs/spark4-upgrade.md

Refs #89
```

## Commit Message Consistency Checklist

Before finalizing the commit message:

- [ ] Header follows <type>(<scope>): <description> format
- [ ] Type is one of: feat, fix, docs, style, refactor, test, perf, chore
- [ ] Scope is concise and relevant to changes
- [ ] Description is imperative, lowercase, no period, under 72 chars
- [ ] Body explains **why** and **what** (not just code changes)
- [ ] Breaking changes are clearly documented in footer
- [ ] Issue references use proper format: Closes #, Fixes #, Refs #
- [ ] Message is clear to someone not familiar with the code
- [ ] No technical jargon without explanation

## Special Considerations

- **Multiple unrelated changes**: If changes are unrelated, consider splitting into separate commits
- **WIP/work in progress**: Use `WIP: ` prefix for incomplete changes
- **Revert commits**: Use `revert: <original commit hash>` format
- **Merge commits**: Keep merge commit messages minimal
- **Large refactors**: Provide context and migration instructions
- **Deprecation**: Document deprecation timeline and alternatives

## Output Format

Generate commit message and execution commands as:

```
## Proposed Commit Message

<type>(<scope>): <description>

<body if needed>

<footer if needed>

---

## Git Commit Commands

```bash
git add <file1> <file2>
git commit -m "<commit message>"
```

---

## Workflow Summary

**✅ Completed Steps:**
1. Code Quality Validation
2. Code Quality Improvements
3. Documentation Review
4. Commit Message Generation

**📝 Changes to Commit:**
- List of modified files

**🎯 Commit Message:** Follows Conventional Commits specification

Execute the git commands above to commit your changes.
```

Ensure the output:
- Follows Conventional Commits specification
- Provides executable git commands
- Is clear and informative for maintainers
- Includes necessary context and reasoning
- References relevant issues or PRs
- Documents breaking changes explicitly
- Includes workflow summary for transparency
