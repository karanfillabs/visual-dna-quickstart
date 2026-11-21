import io
import os
import discord
import requests

DISCORD_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
KARANFIL_API_KEY = os.environ["KARANFIL_API_KEY"]
IDENTIFY_URL = "https://api.karanfillabs.com/v1/identify"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.content.startswith("!identify"):
        return
    if not message.attachments:
        await message.reply("Attach a movie or TV scene screenshot with `!identify`.")
        return

    img_bytes = await message.attachments[0].read()
    r = requests.post(
        IDENTIFY_URL,
        headers={"X-API-Key": KARANFIL_API_KEY},
        params={"top_k": 3, "min_score": 0.70},
        files={"file": (message.attachments[0].filename, io.BytesIO(img_bytes), "image/jpeg")},
        timeout=20,
    )
    if not r.ok:
        await message.reply(f"API error ({r.status_code}).")
        return

    data = r.json()
    matches = data.get("matches") or []
    embed = discord.Embed(
        title="Karanfil Labs — Visual DNA Result",
        color=0x8B1528,
    )
    embed.set_footer(text=f"Latency: {data.get('latency_ms', '-')} ms • Processed in Volatile RAM")
    if not matches:
        embed.description = "No confident match found above threshold."
    else:
        for i, m in enumerate(matches[:3], start=1):
            title = m.get("title") or m.get("clean_title") or m.get("movie_name") or "Unknown"
            score = m.get("score")
            val = f"Confidence: `{score * 100:.1f}%`" if isinstance(score, (int, float)) else "-"
            embed.add_field(name=f"{i}. {title}", value=val, inline=False)

    await message.reply(embed=embed)


client.run(DISCORD_TOKEN)
