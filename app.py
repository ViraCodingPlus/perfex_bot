import os
import logging
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, Dispatcher
from dotenv import load_dotenv
from database import get_connection, backup_database
from reports import (
    get_sales_report, 
    get_payments_report, 
    get_invoices_report, 
    get_estimates_report, 
    get_proposals_report
)

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Telegram bot
TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_USER_IDS = [int(id) for id in os.getenv('ADMIN_USER_IDS', '').split(',') if id]
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

def is_authorized(user_id):
    """Check if user is authorized to use the bot"""
    return user_id in ADMIN_USER_IDS

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    if not is_authorized(user.id):
        update.message.reply_text(f"متاسفم {user.first_name}، شما مجاز به استفاده از این ربات نیستید.")
        return

    keyboard = [
        ['📊 گزارش فروش', '💰 گزارش پرداخت‌ها'],
        ['📝 گزارش فاکتورها', '📄 گزارش پیش فاکتورها'],
        ['📋 گزارش پروپوزال‌ها', '💾 پشتیبان‌گیری پایگاه داده']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        f'سلام {user.first_name}! من دستیار Perfex CRM شما هستم.\n'
        'یکی از گزینه‌های زیر را انتخاب کنید:',
        reply_markup=reply_markup
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    if not is_authorized(update.effective_user.id):
        return
        
    update.message.reply_text(
        'دستورات موجود:\n'
        '/start - شروع ربات\n'
        '/help - نمایش این پیام راهنما\n'
        '/backup - ایجاد پشتیبان از پایگاه داده\n'
        '/sales - دریافت گزارش فروش\n'
        '/payments - دریافت گزارش پرداخت‌ها\n'
        '/invoices - دریافت گزارش فاکتورها\n'
        '/estimates - دریافت گزارش پیش فاکتورها\n'
        '/proposals - دریافت گزارش پروپوزال‌ها'
    )

def backup_command(update: Update, context: CallbackContext) -> None:
    """Create a database backup."""
    if not is_authorized(update.effective_user.id):
        return
        
    update.message.reply_text('در حال ایجاد پشتیبان از پایگاه داده...')
    try:
        backup_file = backup_database()
        with open(backup_file, 'rb') as file:
            update.message.reply_document(
                document=file,
                filename=os.path.basename(backup_file),
                caption='پشتیبان‌گیری از پایگاه داده با موفقیت انجام شد!'
            )
    except Exception as e:
        logger.error(f"Backup error: {e}")
        update.message.reply_text(f'خطا در ایجاد پشتیبان: {e}')

def sales_report(update: Update, context: CallbackContext) -> None:
    """Get sales report."""
    if not is_authorized(update.effective_user.id):
        return
        
    update.message.reply_text('در حال تولید گزارش فروش...')
    try:
        report_file = get_sales_report()
        with open(report_file, 'rb') as file:
            update.message.reply_document(
                document=file,
                filename=os.path.basename(report_file),
                caption='گزارش فروش آماده شد!'
            )
    except Exception as e:
        logger.error(f"Sales report error: {e}")
        update.message.reply_text(f'خطا در تولید گزارش فروش: {e}')

def payments_report(update: Update, context: CallbackContext) -> None:
    """Get payments report."""
    if not is_authorized(update.effective_user.id):
        return
        
    update.message.reply_text('در حال تولید گزارش پرداخت‌ها...')
    try:
        report_file = get_payments_report()
        with open(report_file, 'rb') as file:
            update.message.reply_document(
                document=file,
                filename=os.path.basename(report_file),
                caption='گزارش پرداخت‌ها آماده شد!'
            )
    except Exception as e:
        logger.error(f"Payments report error: {e}")
        update.message.reply_text(f'خطا در تولید گزارش پرداخت‌ها: {e}')

def invoices_report(update: Update, context: CallbackContext) -> None:
    """Get invoices report."""
    if not is_authorized(update.effective_user.id):
        return
        
    update.message.reply_text('در حال تولید گزارش فاکتورها...')
    try:
        report_file = get_invoices_report()
        with open(report_file, 'rb') as file:
            update.message.reply_document(
                document=file,
                filename=os.path.basename(report_file),
                caption='گزارش فاکتورها آماده شد!'
            )
    except Exception as e:
        logger.error(f"Invoices report error: {e}")
        update.message.reply_text(f'خطا در تولید گزارش فاکتورها: {e}')

def estimates_report(update: Update, context: CallbackContext) -> None:
    """Get estimates report."""
    if not is_authorized(update.effective_user.id):
        return
        
    update.message.reply_text('در حال تولید گزارش پیش فاکتورها...')
    try:
        report_file = get_estimates_report()
        with open(report_file, 'rb') as file:
            update.message.reply_document(
                document=file,
                filename=os.path.basename(report_file),
                caption='گزارش پیش فاکتورها آماده شد!'
            )
    except Exception as e:
        logger.error(f"Estimates report error: {e}")
        update.message.reply_text(f'خطا در تولید گزارش پیش فاکتورها: {e}')

def proposals_report(update: Update, context: CallbackContext) -> None:
    """Get proposals report."""
    if not is_authorized(update.effective_user.id):
        return
        
    update.message.reply_text('در حال تولید گزارش پروپوزال‌ها...')
    try:
        report_file = get_proposals_report()
        with open(report_file, 'rb') as file:
            update.message.reply_document(
                document=file,
                filename=os.path.basename(report_file),
                caption='گزارش پروپوزال‌ها آماده شد!'
            )
    except Exception as e:
        logger.error(f"Proposals report error: {e}")
        update.message.reply_text(f'خطا در تولید گزارش پروپوزال‌ها: {e}')

def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle incoming messages."""
    if not is_authorized(update.effective_user.id):
        return
        
    text = update.message.text
    
    if text == '💾 پشتیبان‌گیری پایگاه داده':
        backup_command(update, context)
    elif text == '📊 گزارش فروش':
        sales_report(update, context)
    elif text == '💰 گزارش پرداخت‌ها':
        payments_report(update, context)
    elif text == '📝 گزارش فاکتورها':
        invoices_report(update, context)
    elif text == '📄 گزارش پیش فاکتورها':
        estimates_report(update, context)
    elif text == '📋 گزارش پروپوزال‌ها':
        proposals_report(update, context)
    else:
        update.message.reply_text('لطفا یکی از گزینه‌های منو را انتخاب کنید.')

def setup_bot():
    """Setup the bot with all handlers"""
    # Create updater
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("backup", backup_command))
    dispatcher.add_handler(MessageHandler(Filters.regex('^📊 گزارش فروش$'), sales_report))
    dispatcher.add_handler(MessageHandler(Filters.regex('^💰 گزارش پرداخت‌ها$'), payments_report))
    dispatcher.add_handler(MessageHandler(Filters.regex('^📝 گزارش فاکتورها$'), invoices_report))
    dispatcher.add_handler(MessageHandler(Filters.regex('^📄 گزارش پیش فاکتورها$'), estimates_report))
    dispatcher.add_handler(MessageHandler(Filters.regex('^📋 گزارش پروپوزال‌ها$'), proposals_report))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Always use webhook if URL is provided
    if WEBHOOK_URL:
        updater.start_webhook(
            listen='0.0.0.0',
            port=int(os.getenv('PORT', 5000)),
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
        )
    else:
        logger.warning("WEBHOOK_URL not set. Bot will not start.")
        return None

    return updater

def webhook(request):
    """Process webhook updates"""
    dispatcher: Dispatcher = request.app.config['DISPATCHER']
    update = Update.de_json(request.get_json(force=True), dispatcher.bot)
    dispatcher.process_update(update)
    return 'ok'

@app.route('/webhook', methods=['POST'])
def process_webhook():
    return webhook(request)

@app.route('/')
def index():
    return 'ربات تلگرام Perfex CRM در حال اجراست!'

if __name__ == '__main__':
    # Setup bot
    updater = setup_bot()
    
    # Store dispatcher in Flask app config
    app.config['DISPATCHER'] = updater.dispatcher
    
    # Start the Bot in webhook mode
    if WEBHOOK_URL:
        updater.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        # Start the Flask server
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    else:
        # Use polling instead if webhook is not configured
        updater.start_polling()
        updater.idle() 