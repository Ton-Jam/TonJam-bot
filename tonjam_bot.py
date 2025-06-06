from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)
import aiosqlite
import asyncio

BOT_TOKEN = "7591465695:AAFMdgh2tCD7nNvLG2DrODjy7wg8MvEWVoA"

# Initialize database
async def init_db():
    async with aiosqlite.connect("tonjam.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                tj_points INTEGER DEFAULT 0
            )
        """)
        await db.commit()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    async with aiosqlite.connect("tonjam.db") as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (telegram_id, username)
            VALUES (?, ?)
        """, (user.id, user.username))
        await db.execute("UPDATE users SET tj_points = tj_points + 10 WHERE telegram_id = ?", (user.id,))
        await db.commit()

    await update.message.reply_text(
        "🎶 Welcome to Tonjam — your Web3 music experience!\n"
        "Use /upload to submit tracks or /listen to explore.\n"
        "You've earned +10 TJ Points for signing up!"
    )

# /upload command
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚧 The upload feature is under development. Soon, you'll be able to mint your music as NFTs on TON!"
    )

# /listen command
async def listen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎧 Streaming feature coming soon. You’ll be able to jam to Web3 tracks straight from Tonjam!"
    )

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 Available commands:\n"
        "/start - Welcome message\n"
        "/upload - Upload your music\n"
        "/listen - Explore music\n"
        "/points - Check your TJ Points\n"
        "/play - Simulate music play\n"
        "/help - Show this help message"
    )

# /points command
async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    async with aiosqlite.connect("tonjam.db") as db:
        async with db.execute("SELECT tj_points FROM users WHERE telegram_id = ?", (user.id,)) as cursor:
            row = await cursor.fetchone()
            points = row[0] if row else 0
    await update.message.reply_text(f"💰 You have {points} TJ Points.")

# /play command
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_caption = (
        "🎵 Now Playing: *TonJam*\n"
        "Artist: TON\n\n"
        "❤️ Add to Favorites\n"
        "⬇️ Download (coming soon)\n"
        "▶️ Pause | ⏭️ Next\n"
        "🔁 Repeat | 🔀 Shuffle\n\n"
        "💬 Use /comments to share your thoughts!"
    )

    await update.message.reply_photo(
        photo="https://cdn.openai.com/chat-assets/snoop-avatar.png",  # Replace with your own track thumbnail
        caption=track_caption,
        parse_mode="Markdown"
    )

# Main function
async def main():
    await init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("upload", upload))
    app.add_handler(CommandHandler("listen", listen))
    app.add_handler(CommandHandler("points", points))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("play", play))

    print("✅ TonJam Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())