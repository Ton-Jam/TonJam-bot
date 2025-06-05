import os
import asyncio
import aiosqlite
from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("7591465695:AAFMdgh2tCD7nNvLG2DrODjy7wg8MvEWVoA")

DB_PATH = "users.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                points INTEGER DEFAULT 0
            )
        ''')
        await db.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (user.id, user.username))
        await db.commit()
    await update.message.reply_text(f"Welcome {user.first_name}! You've been registered for TonJam.")

async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT points FROM users WHERE id = ?", (user.id,)) as cursor:
            row = await cursor.fetchone()
            points = row[0] if row else 0
    await update.message.reply_text(f"You have {points} points.")

async def earn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    points_earned = 10
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET points = points + ? WHERE id = ?", (points_earned, user.id))
        await db.commit()
    await update.message.reply_text(f"You've earned {points_earned} points!")

if __name__ == '__main__':
    asyncio.run(init_db())
    app = ApplicationBuilder().token(7591465695:AAFMdgh2tCD7nNvLG2DrODjy7wg8MvEWVoA).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("points", points))
    app.add_handler(CommandHandler("earn", earn))
    app.run_polling()