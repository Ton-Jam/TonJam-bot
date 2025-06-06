import os
import asyncio
import asyncpg
from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === CONFIG ===
BOT_TOKEN = "7591465695:AAFMdgh2tCD7nNvLG2DrODjy7wg8MvEWVoA"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/tonjam")  # Replace with actual or set on Render

# === DATABASE SETUP ===
async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            username TEXT,
            tj_points INTEGER DEFAULT 0
        );
    """)
    await conn.close()

# === COMMAND HANDLERS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        INSERT INTO users (telegram_id, username)
        VALUES ($1, $2)
        ON CONFLICT (telegram_id) DO NOTHING
    """, user.id, user.username)

    await conn.execute("""
        UPDATE users SET tj_points = tj_points + 10 WHERE telegram_id = $1
    """, user.id)
    await conn.close()

    await update.message.reply_text(
        "🎶 Welcome to *TonJam* — your Web3 music experience!\n"
        "You've earned +10 TJ Points for signing up!\n\n"
        "Use /upload to submit tracks or /listen to explore."
    )

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 Upload feature coming soon! Mint your tracks as NFTs on TON.")

async def listen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎧 Streaming feature coming soon. Jam to Web3 music right from TonJam!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 Commands:\n"
        "/start - Register and get welcome bonus\n"
        "/upload - Upload your track\n"
        "/listen - Explore music\n"
        "/points - Your TJ Points\n"
        "/play - Simulate a track\n"
        "/help - This message"
    )

async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT tj_points FROM users WHERE telegram_id = $1", user.id)
    points = row['tj_points'] if row else 0
    await conn.close()
    await update.message.reply_text(f"💰 You have {points} TJ Points.")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = (
        "🎵 Now Playing: *TonJam*\n"
        "Artist: TON\n\n"
        "❤️ Favorite\n⬇️ Download (soon)\n▶️ Pause | ⏭️ Next\n🔁 Repeat | 🔀 Shuffle\n\n"
        "💬 Use /comments to share!"
    )
    await update.message.reply_photo(
        photo="https://cdn.openai.com/chat-assets/snoop-avatar.png",  # Replace with real image URL
        caption=caption,
        parse_mode="Markdown"
    )

# === MAIN APP ===
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("upload", upload))
app.add_handler(CommandHandler("listen", listen))
app.add_handler(CommandHandler("points", points))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("play", play))

if __name__ == "__main__":
    asyncio.run(init_db())
    app.run_polling()
