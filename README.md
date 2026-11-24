# UZ SMETA AI Telegram bot (starter)

## Features
- Brick wall volume and approximate brick quantity (400 bricks/m³ assumption; validate by brick size and mortar joints)
- Concrete volume with optional 5% allowance
- Floor/area calculation
- Plaster/finish material estimate by area, thickness, labeled consumption, and unit price
- Manual estimate line items with total

## Deploy to Render
1. Upload this folder's contents to a GitHub repository (repository root must contain `bot.py`, `requirements.txt`, and `render.yaml`).
2. In Render, choose **New → Blueprint** and connect the GitHub repository.
3. Render reads `render.yaml` and creates a background worker.
4. In the Render environment prompt, set `TELEGRAM_BOT_TOKEN` to the token from BotFather. Never put the token in GitHub or share it in chat.
5. Deploy and inspect the worker logs. On success, open Telegram and send `/start` to your bot.


## Run locally
1. Install Python 3.11+.
2. `python -m venv .venv` then activate it.
3. `pip install -r requirements.txt`
4. Set `TELEGRAM_BOT_TOKEN` as an environment variable (do not commit token files).
5. Run `python bot.py`.


## Important
Calculations are preliminary estimates. Structural quantities (foundation, reinforcement, structural concrete) must be checked against drawings, engineering specifications, local norms, and a qualified professional. This MVP does not parse PDF/DWG drawings or fetch live market prices.\nEOF
cd /mnt/data/uz_smeta_ai_deploy && zip -qr /mnt/data/uz_smeta_ai_render_ready.zip uz_smeta_ai && ls -lh /mnt/data/uz_smeta_ai_render_ready.zip
