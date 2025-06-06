from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import aiosqlite
import asyncio

BOT_TOKEN = "7591465695:AAFMdgh2tCD7nNvLG2DrODjy7wg8MvEWVoA"  # Your Bot Token

# Initialize the database
async def init_db():
    async with aiosqlite.connect("tonjam.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                tj_points INTEGER DEFAULT 0
            )
        """)
        await db.commit()

# Start command
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

# Upload command
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚧 Upload coming soon. Soon, you’ll mint your music as NFTs on TON!"
    )

# Listen command
async def listen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎧 Streaming coming soon. You’ll