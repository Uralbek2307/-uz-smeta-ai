# UZ SMETA AI Telegram bot — Render Web Service (free starter)

## Deploy on Render
1. This repository must contain `bot.py`, `requirements.txt`, and `render.yaml` in its root.
2. In Render, create a Blueprint from the repository. The Blueprint creates a free Web Service.
3. Add the secret environment variable `TELEGRAM_BOT_TOKEN` in the Render service settings. Never commit or share the token.
4. Deploy. Render provides `RENDER_EXTERNAL_URL` and `PORT`; the bot registers its Telegram webhook against the Render URL.
5. Open Telegram and send `/start` to the bot.


## Features
- Brick-wall volume and rough brick count using 400 bricks/m³ assumption
- Concrete volume with 5% reserve
- Floor/area calculation
- Plaster material estimate using the consumption rate supplied by the user
- Manual estimate line items and total


## Limits
This starter does not read PDF/DWG drawings and does not contain live construction prices. Estimates are preliminary; verify quantities against drawings, specifications, local practice, and qualified professionals.
