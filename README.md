# RSSFunBot

**Subscribe to the fun corners of the internet — memes, clips, pics, and oddities — and get them delivered straight to your Telegram channel or group.**

RSSFunBot watches RSS feeds from sites like Reddit, blogs, and forums, picks up new posts, and forwards the good stuff to Telegram with media intact. Built for channels that curate **funny, interesting, and shareable content** — not generic news dumps.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![GitHub](https://img.shields.io/badge/GitHub-mathewskdaniel%2FRSSFunBot-181717?logo=github)](https://github.com/mathewskdaniel/RSSFunBot)

---

## What it does

Point the bot at RSS links (e.g. `https://www.reddit.com/r/funny.rss`) and it:

- **Monitors** feeds on a schedule you control
- **Posts** new items to your Telegram channel or group
- **Keeps media** — videos, images, and link previews — so posts look good in-chat
- **Lets you manage everything** from Telegram with buttons — no config files for day-to-day use

Ideal for meme pages, “best of Reddit” channels, hobby feeds, and anything where **entertainment and discovery** matter more than plain text headlines.

---

## Why RSSFunBot (not just another RSS bot)

RSSFunBot is tuned for **media-heavy, social-style content**:

### Reddit done right

| Feature | Why it matters |
|---------|----------------|
| **Real `v.redd.it` video** | Downloads and sends actual Reddit videos — not low-res thumbnails |
| **Full-size images** | Upgrades `preview.redd.it` → `i.redd.it` for sharp pictures |
| **`/reddit_video` settings** | Manager can set max quality, file size, and timeout without restarting |

### Third-party videos (YouTube, Vimeo, etc.)

Reddit posts that link out to YouTube, Vimeo, Twitch, TikTok, and similar are sent as **clean link previews** — Telegram shows the native embed instead of a blurry Reddit preview image. Per-subscription toggle: **link preview** or **skip post**.

### Easy management in Telegram

| Command | What you get |
|---------|----------------|
| **`/list`** | Every subscription as a button — see ✅ active / ⏸ paused, tap to toggle, ⚙️ to open settings |
| **`/set`** | Per-feed formatting: hashtags, custom title, media-only mode, flowerss style, intervals |
| **`/set_default`** | Defaults for new subscriptions (media-only, link previews, etc.) |
| **`/sub` / `/unsub`** | Add or remove feeds in bulk |
| **`/test`** | Try a feed before going live |

No SSH required for routine changes — subscribe, tune, and pause feeds from chat.

### Post layout for channels

- **flowerss**-style posts tuned for visual feeds
- **Custom title** below hashtags (e.g. your channel @mention) without renaming feeds in menus
- **Media-only** mode — skip empty text posts, send the pic or clip
- **Hashtags** per subscription for consistent channel branding

---

## Quick start

**Requirements:** Python 3.9+, **ffmpeg**, **yt-dlp** (for Reddit video)

```bash
git clone https://github.com/mathewskdaniel/RSSFunBot.git
cd RSSFunBot
cp .env.sample .env
# Edit .env: TOKEN (from @BotFather), MANAGER (your Telegram user id)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python rssfunbot.py
```

1. Create a bot with [@BotFather](https://t.me/BotFather) and enable **inline mode** (`/setinline`).
2. Add the bot to your channel as admin (post messages).
3. Subscribe: `/sub https://www.reddit.com/r/funny.rss` (or target a channel: `/sub @YourChannel https://…`).
4. Tune with `/set` or `/list`.

---

## Commands

| Command | Description |
|---------|-------------|
| `/sub` | Subscribe to RSS feeds |
| `/unsub` | Unsubscribe |
| `/list` | View and manage subscriptions (active/paused + settings) |
| `/set` | Customize a subscription |
| `/set_default` | Default settings for new subscriptions |
| `/import` / `/export` | OPML backup |
| `/help` | Help |

**Manager:** `/test`, `/reddit_video`, `/user_info`

---

## Reddit video settings (`.env` or `/reddit_video`)

| Variable | Default | Description |
|----------|---------|-------------|
| `REDDIT_VIDEO_DOWNLOAD` | `1` | Download `v.redd.it` videos |
| `REDDIT_VIDEO_MAX_HEIGHT` | `480` | Max quality (220–720p) |
| `REDDIT_VIDEO_MAX_BYTES` | `20971520` | Max file size (20 MB) |
| `REDDIT_VIDEO_DOWNLOAD_TIMEOUT` | `120` | Download timeout (seconds) |
| `MEDIA_TEMP_DIR` | auto | Temp folder for downloads |

---

## Also included

Multi-user support, channels & groups, i18n, OPML, Telegraph long-post mode, proxies, and rich formatting options — everything needed to run a serious curation channel at scale.

---

## License

RSSFunBot is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0).

---

## Credits

Inspired by [RSS to Telegram Bot](https://github.com/Rongronggg9/RSS-to-Telegram-Bot).
