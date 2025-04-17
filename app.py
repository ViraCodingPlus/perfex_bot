import os
import logging
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from dotenv import load_dotenv
from database import get_connection, backup_database
from reports import (
    get_sales_report, 
    get_payments_report, 
    get_invoices_report, 
    get_estimates_report, 
    get_proposals_report
)
import time
from io import BytesIO

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Telegram Bot Token
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Authorized users
AUTHORIZED_USERS = [int(user_id) for user_id in os.getenv('AUTHORIZED_USERS', '').split(',') if user_id]

def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text('You are not authorized to use this bot.')
        return

    keyboard = [
        ['/sales_report', '/payments_report'],
        ['/invoices_report', '/estimates_report'],
        ['/proposals_report', '/backup']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        'Welcome to Perfex CRM Bot! Please select an option:',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text('You are not authorized to use this bot.')
        return

    help_text = """
Available commands:
/sales_report - Get sales report
/payments_report - Get payments report
/invoices_report - Get invoices report
/estimates_report - Get estimates report
/proposals_report - Get proposals report
/backup - Create database backup
/help - Show this help message
"""
    await update.message.reply_text(help_text)

async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create a database backup."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text('You are not authorized to use this bot.')
        return

    try:
        backup_data = backup_database()
        if backup_data:
            # Create a temporary file in memory
            backup_file = BytesIO(backup_data)
            backup_file.name = f"{DB_NAME}-{time.strftime('%Y%m%d-%H%M%S')}.sql"
            
            await update.message.reply_document(
                document=backup_file,
                caption='Database backup created successfully!'
            )
        else:
            await update.message.reply_text('Failed to create backup.')
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        await update.message.reply_text('An error occurred while creating the backup.')

async def sales_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate and send sales report."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text('You are not authorized to use this bot.')
        return

    try:
        report_file = get_sales_report()
        if report_file:
            report_file.name = f"sales_report_{time.strftime('%Y%m%d-%H%M%S')}.xlsx"
            await update.message.reply_document(
                document=report_file,
                caption='Sales report generated successfully!'
            )
        else:
            await update.message.reply_text('Failed to generate sales report.')
    except Exception as e:
        logger.error(f"Error generating sales report: {e}")
        await update.message.reply_text('An error occurred while generating the sales report.')

async def payments_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate and send payments report."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text('You are not authorized to use this bot.')
        return

    try:
        report_file = get_payments_report()
        if report_file:
            report_file.name = f"payments_report_{time.strftime('%Y%m%d-%H%M%S')}.xlsx"
            await update.message.reply_document(
                document=report_file,
                caption='Payments report generated successfully!'
            )
        else:
            await update.message.reply_text('Failed to generate payments report.')
    except Exception as e:
        logger.error(f"Error generating payments report: {e}")
        await update.message.reply_text('An error occurred while generating the payments report.')

async def invoices_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate and send invoices report."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text('You are not authorized to use this bot.')
        return

    try:
        report_file = get_invoices_report()
        if report_file:
            report_file.name = f"invoices_report_{time.strftime('%Y%m%d-%H%M%S')}.xlsx"
            await update.message.reply_document(
                document=report_file,
                caption='Invoices report generated successfully!'
            )
        else:
            await update.message.reply_text('Failed to generate invoices report.')
    except Exception as e:
        logger.error(f"Error generating invoices report: {e}")
        await update.message.reply_text('An error occurred while generating the invoices report.')

async def estimates_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate and send estimates report."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text('You are not authorized to use this bot.')
        return

    try:
        report_file = get_estimates_report()
        if report_file:
            report_file.name = f"estimates_report_{time.strftime('%Y%m%d-%H%M%S')}.xlsx"
            await update.message.reply_document(
                document=report_file,
                caption='Estimates report generated successfully!'
            )
        else:
            await update.message.reply_text('Failed to generate estimates report.')
    except Exception as e:
        logger.error(f"Error generating estimates report: {e}")
        await update.message.reply_text('An error occurred while generating the estimates report.')

async def proposals_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate and send proposals report."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text('You are not authorized to use this bot.')
        return

    try:
        report_file = get_proposals_report()
        if report_file:
            report_file.name = f"proposals_report_{time.strftime('%Y%m%d-%H%M%S')}.xlsx"
            await update.message.reply_document(
                document=report_file,
                caption='Proposals report generated successfully!'
            )
        else:
            await update.message.reply_text('Failed to generate proposals report.')
    except Exception as e:
        logger.error(f"Error generating proposals report: {e}")
        await update.message.reply_text('An error occurred while generating the proposals report.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text('You are not authorized to use this bot.')
        return

    await update.message.reply_text(
        'Please use the commands from the keyboard or type /help for available commands.'
    )

def setup_bot():
    """Set up the bot with all handlers."""
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("backup", backup_command))
    application.add_handler(CommandHandler("sales_report", sales_report))
    application.add_handler(CommandHandler("payments_report", payments_report))
    application.add_handler(CommandHandler("invoices_report", invoices_report))
    application.add_handler(CommandHandler("estimates_report", estimates_report))
    application.add_handler(CommandHandler("proposals_report", proposals_report))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return application

# Initialize bot
bot = setup_bot()

@app.route('/webhook', methods=['POST'])
async def process_webhook():
    """Process incoming webhook updates."""
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot.bot)
        await bot.process_update(update)
    return "ok"

@app.route('/')
def index():
    """Root endpoint."""
    return "Bot is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 