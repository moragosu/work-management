## Brief overview
Python-based batch processing system for RF path loss analysis. uv and PEP8 STRICT required.

## Package Management
- Use uv: `uv add`, `uv init`, `uv venv`
- Do NOT use pip
- ALWAYS `uv run xxx`, NEVER `python3 xxx`

## Git Command Safety
- Use timeout with `--no-pager --no-color` flags
- Save large outputs to `/tmp/` files

## File Reading Strategy
- Prefer `read_file` tool over `cat`, `less`, `grep`

## Code Style: PEP8 STRICT
- Simpler is better
- Comments only when necessary
- Type hints REQUIRED
- Avoid overly defensive programming; avoid isinstance checks; manage exceptions only when necessary

## Configuration
- Do NOT modify configuration files directly
- Use environment variables

## Common Mistakes to Avoid
- Using pip or python3 instead of uv
- Missing timeout in git commands
- Using `cat` to read files
- Missing type hints

## Quick Reference
| Task | Command |
|------|---------|
| Git status | `timeout 10 git status --short` |
| Git diff | `timeout 10 git --no-pager --no-color diff` |
| Read file | `read_file path/to/file` |
| Install package | `uv add <package>` |
| Run script | `uv run <script.py>` |

## Language
- Code/documentation: English
- Agent responses: Korean