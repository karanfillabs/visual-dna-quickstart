import io
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
KARANFIL_API_KEY = os.environ["KARANFIL_API_KEY"]
IDENTIFY_URL = "https://api.karanfillabs.com/v1/identify"


def format_matches(data: dict) -> str:
    matches = data.get("matches") or []
    if not matches:
        return f"No confident match found ({data.get('latency_ms', '-')} ms)."
    lines = [f"Visual DNA Matches ({data.get('latency_ms', '-')} ms):"]
    for i, m in enumerate(matches[:3], start=1):
        title = m.get("title") or m.get("clean_title") or m.get("movie_name") or "Unknown"
        score = m.get("confidence") if m.get("confidence") is not None else m.get("score")
        score_txt = f"{score * 100:.1f}%" if isinstance(score, (int, float)) else "-"
        lines.append(f"{i}. {title} ({score_txt})")
    rem = (data.get("quota") or {}).get("remaining_quota")
    if rem is not None:
        lines.append(f"\nRemaining quota: {rem}")
    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send any movie or TV scene screenshot to identify it via Karanfil Labs Visual DNA API.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    buf = io.BytesIO()
    await photo_file.download_to_memory(buf)
    buf.seek(0)

    r = requests.post(
        IDENTIFY_URL,
        headers={"X-API-Key": KARANFIL_API_KEY},
        params={"top_k": 3, "min_score": 0.70},
        files={"file": ("frame.jpg", buf, "image/jpeg")},
        timeout=20,
    )
    if not r.ok:
        await update.message.reply_text(f"API error ({r.status_code}): {r.text[:200]}")
        return
    await update.message.reply_text(format_matches(r.json()))


app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.run_polling()
