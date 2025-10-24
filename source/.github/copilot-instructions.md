This repository is a small Discord bot built with discord.py. Keep guidance concise and focused on how this project is structured and the patterns contributors must follow.

Repository overview
- Entry point: `main.py` — creates the Bot (prefix `!`), sets up Intents and dynamically loads every `*.py` under `comandos/` as an extension (module path `comandos.<path>`).
- Commands are implemented as Cogs inside `comandos/` subfolders. Each module must expose an `async def setup(bot)` that calls `await bot.add_cog(...)`.
- Status is driven by `status.json` (type/text). Environment variables (loaded with `python-dotenv`) are required: `DISCORD_BOT_TOKEN` (bot token) and `LOCAL_URL` (local AI endpoint used by the AI cog).

Key patterns and examples
- Loading extensions: `main.py` walks `./comandos` and calls `await bot.load_extension(f"comandos.{module_path}")`. Examples:
  - `comandos/ai/ai.py` is imported as `comandos.ai.ai` and must provide `async def setup(bot)`.
  - When adding a new command file, place it under `comandos/<feature>/your_command.py` and implement a Cog + `setup` function.
- Command authoring:
  - Use `class X(commands.Cog): ...` and register commands with `@commands.command(...)` or listeners with `@commands.Cog.listener()`.
  - Provide `help=` text in the decorator — `comandos/ajuda/ajuda.py` uses the `help` field to display descriptions.
- Intents and permissions: `main.py` enables `message_content`, `reactions`, `guilds`, and `members`. Follow the same intent usage for any features that need member or message content access.

AI integration
- The AI cog at `comandos/ai/ai.py` loads `prompt.json` for model/config values and posts to `LOCAL_URL` (an internal/localhost AI service) using `requests.post`.
- The cog expects `LOCAL_URL` present in the environment; otherwise it raises at import time. Keep the `prompt.json` keys (`model`, `system`, `temperature`, etc.) when modifying the AI cog.

Running and debugging locally
- Use a `.env` at the repository root (dotenv is already used):
  DISCORD_BOT_TOKEN=your_token
  LOCAL_URL=http://localhost:11434/api
- Run the bot from the repository root with the same Python used for development:
  python main.py
- If the bot fails to start, check for:
  - Missing `DISCORD_BOT_TOKEN` or `LOCAL_URL`.
  - JSON parsing errors in `status.json` or `comandos/ai/prompt.json`.

Project-specific gotchas
- Module loading relies on the relative path under `comandos/`. Ensure file names and folder names are valid Python identifiers (no spaces, hyphens). The loader transforms the path into `comandos.<subdirs>.<module>`.
- The AI cog loads `prompt.json` at import time; avoid long-running network calls or blocking operations during module import.
- `status.json` must contain `type` (playing/listening/watching/competing) and `text`. If `type` is unknown, the bot will skip setting presence.

What to do when adding a new feature
1. Add `comandos/<feature>/` folder and a `<name>.py` file that defines a Cog and `async def setup(bot)`.
2. Keep commands' `help` strings concise. `comandos/ajuda/ajuda.py` builds a help embed from `command.help` values.
3. Avoid heavy initialization at import time — prefer lazy setup inside `setup(bot)` or the Cog constructor.

Assumptions made
- This file lives at the repository root (repo top-level `main.py` seen in this workspace). If your repo root differs, adjust paths accordingly.

If any section is unclear or you want more detail (examples for tests, CI, or adding type hints), tell me which area to expand.
