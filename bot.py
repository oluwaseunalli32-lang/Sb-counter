import logging
import os
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
    filters,
    ContextTypes,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# ---------- Helper Function ----------
def count_text(text: str):
    """Return word, character, and line counts."""
    words = len(text.split())
    chars = len(text)
    lines = len(text.splitlines()) if text else 0
    return words, chars, lines

# ---------- Command Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    welcome = (
        "👋 *Word Counter Bot*\n\n"
        "I can count words, characters, and lines in any text.\n\n"
        "*Commands:*\n"
        "/count <text> – Count words, characters, and lines\n"
        "/help – Show this help message\n\n"
        "*Inline Mode:*\n"
        "Type `@YourBotUsername your text` in any chat to get an instant count."
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    await start(update, context)

async def count_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /count <text> command."""
    # Get the text after the command
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text(
            "Please provide some text. Example:\n`/count Hello world`",
            parse_mode="Markdown",
        )
        return

    words, chars, lines = count_text(text)
    reply = (
        f"📊 *Results*\n"
        f"• Words: `{words}`\n"
        f"• Characters: `{chars}`\n"
        f"• Lines: `{lines}`"
    )
    await update.message.reply_text(reply, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Count text from any direct message (no command needed)."""
    text = update.message.text
    if not text:
        return
    words, chars, lines = count_text(text)
    reply = (
        f"📊 *Results*\n"
        f"• Words: `{words}`\n"
        f"• Characters: `{chars}`\n"
        f"• Lines: `{lines}`"
    )
    await update.message.reply_text(reply, parse_mode="Markdown")

# ---------- Inline Mode Handler ----------
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline queries – returns word count as an inline result."""
    query = update.inline_query.query.strip()
    if not query:
        return

    words, chars, lines = count_text(query)
    result_text = (
        f"Words: {words}\n"
        f"Characters: {chars}\n"
        f"Lines: {lines}"
    )

    results = [
        InlineQueryResultArticle(
            id="1",
            title=f"Words: {words} | Chars: {chars} | Lines: {lines}",
            description=f"Tap to send the count for: \"{query[:40]}...\"",
            input_message_content=InputTextMessageContent(
                f"📊 *Word Count*\n```\n{query[:100]}\n```\n"
                f"• Words: `{words}`\n"
                f"• Characters: `{chars}`\n"
                f"• Lines: `{lines}`",
                parse_mode="Markdown",
            ),
        )
    ]

    await update.inline_query.answer(results, cache_time=5)

# ---------- Main ----------
def main():
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("count", count_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(InlineQueryHandler(inline_query))

    # Run the bot (polling mode – perfect for background worker)
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
