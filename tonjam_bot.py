import logging
import os
import signal
import asyncio
import aiosqlite
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., https://your-app.onrender.com
PORT = int(os.getenv("PORT", 8443))  # Render assigns PORT dynamically

# Initialize DB
async def init_db():
    db_path = "/tmp/tonjam.db"
    logger.info(f"Attempting to connect to database at {db_path}")
    if os.access("/tmp", os.W_OK):
        logger.info("/tmp is writable")
    else:
        logger.error("/tmp is not writable")
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                tj_points INTEGER DEFAULT 0
            )
        """)
        await db.commit()
    logger.info("Database initialized successfully")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    async with aiosqlite.connect("/tmp/tonjam.db") as db:
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

# /upload
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚧 Upload feature coming soon! You'll be able to mint music NFTs on TON."
    )

# /listen
async def listen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎧 Streaming feature coming soon! Jam to Web3 tracks directly from Tonjam."
    )

# /points
async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    async with aiosqlite.connect("/tmp/tonjam.db") as db:
        async with db.execute("SELECT tj_points FROM users WHERE telegram_id = ?", (user.id,)) as cursor:
            row = await cursor.fetchone()
            points = row[0] if row else 0
    await update.message.reply_text(f"💰 You have {points} TJ Points.")

# /play
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo="https://cdn.openai.com/chat-assets/snoop-avatar.png",  # Replace with your own
        caption=(
            "🎵 Now Playing: *TonJam*\n"
            "Artist: TON\n\n"
            "❤️ Add to Favorites\n"
            "⬇️ Download (soon)\n"
            "▶️ Pause | ⏭️ Next\n"
            "🔁 Repeat | 🔀 Shuffle\n\n"
            "💬 Use /comments to share thoughts!"
        ),
        parse_mode="Markdown"
    )

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 Commands:\n"
        "/start - Start & earn points\n"
        "/upload - Upload music (soon)\n"
        "/listen - Explore tracks\n"
        "/play - Simulate track\n"
        "/points - Check TJ Points\n"
        "/help - Show help"
    )

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# Signal handler for graceful shutdown
async def shutdown(application):
    logger.info("Received shutdown signal, stopping application...")
    await application.stop()
    await application.updater.stop()
    logger.info("Application stopped gracefully")

# Entry point
async def main():
    # Initialize application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("upload", upload))
    app.add_handler(CommandHandler("listen", listen))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("points", points))
    app.add_handler(CommandHandler("help", help_command))
    app.add_error_handler(error_handler)

    # Initialize database
    await init_db()

    # Set up signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(shutdown(app))
        )

    logger.info("TonJam bot is starting...")

    # Set up webhook
    await app.initialize()
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="/webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )
    logger.info(f"Bot running on webhook: {WEBHOOK_URL}/webhook")
    await app.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())