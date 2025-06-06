import asyncpg from telegram import Update, InputMediaPhoto from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes import asyncio import os

BOT_TOKEN = os.getenv("BOT_TOKEN") DB_URL = os.getenv("DATABASE_URL")  # Example: postgres://user:pass@host:port/dbname

Database helper

async def connect_db(): return await asyncpg.connect(dsn=DB_URL)

Initialize database

async def init_db(): conn = await connect_db() await conn.execute(""" CREATE TABLE IF NOT EXISTS users ( id SERIAL PRIMARY KEY, telegram_id BIGINT UNIQUE, username TEXT, tj_points INTEGER DEFAULT 0 ) """) await conn.close()

Start command

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.message.from_user conn = await connect_db() await conn.execute(""" INSERT INTO users (telegram_id, username) VALUES ($1, $2) ON CONFLICT (telegram_id) DO NOTHING """, user.id, user.username) await conn.execute(""" UPDATE users SET tj_points = tj_points + 10 WHERE telegram_id = $1 """, user.id) await conn.close()

await update.message.reply_text(
    "🎶 Welcome to Tonjam — your Web3 music experience!\n"
    "Use /upload to submit tracks or /listen to explore.\n"
    "You've earned +10 TJ Points for signing up!"
)

Upload command

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "🚧 The upload feature is under development. Soon, you'll be able to mint your music as NFTs on TON!" )

Listen command

async def listen(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "🎧 Streaming feature coming soon. You’ll be able to jam to Web3 tracks straight from Tonjam!" )

Help command

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "📜 Available commands:\n" "/start - Welcome message\n" "/upload - Upload your music\n" "/listen - Explore music\n" "/points - Check your TJ Points\n" "/play - Simulate music play\n" "/help - Show this help message" )

Points command

async def points(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.message.from_user conn = await connect_db() row = await conn.fetchrow("SELECT tj_points FROM users WHERE telegram_id = $1", user.id) await conn.close() points = row["tj_points"] if row else 0 await update.message.reply_text(f"💰 You have {points} TJ Points.")

Play command - mock track preview

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE): track_caption = ( "🎵 Now Playing: TonJam\n" "Artist: TON\n\n" "❤️ Add to Favorites\n" "⬇️ Download (coming soon)\n" "▶️ Pause | ⏭️ Next\n" "🔁 Repeat | 🔀 Shuffle\n\n" "💬 Use /comments to share your thoughts!" )

await update.message.reply_photo(
    photo="https://cdn.openai.com/chat-assets/snoop-avatar.png",
    caption=track_caption,
    parse_mode="Markdown"
)

Initialize the bot app

app = ApplicationBuilder().token(BOT_TOKEN).build()

Add command handlers

app.add_handler(CommandHandler("start", start)) app.add_handler(CommandHandler("upload", upload)) app.add_handler(CommandHandler("listen", listen)) app.add_handler(CommandHandler("points", points)) app.add_handler(CommandHandler("help", help_command)) app.add_handler(CommandHandler("play", play))

Run the bot

if name == 'main': asyncio.run(init_db()) app.run_polling()

