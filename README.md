# Perfex CRM Telegram Bot

A Telegram bot for Perfex CRM that provides the following functionalities:
- Database backups
- Sales reports
- Payment reports
- Invoice reports
- Estimate reports
- Proposal reports

## Requirements

- Python 3.7+
- Perfex CRM with MySQL database
- Telegram Bot API token
- MySQL client (for mysqldump)

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/perfex-crm-telegram-bot.git
cd perfex-crm-telegram-bot
```

2. Create a virtual environment and activate it:
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Copy the `.env.example` file to `.env` and set your environment variables:
```
cp .env.example .env
```

5. Edit the `.env` file with your configuration:
   - `TELEGRAM_TOKEN`: Your Telegram bot token from @BotFather
   - `ADMIN_USER_IDS`: Comma-separated list of Telegram user IDs that can access the bot
   - `WEBHOOK_URL`: URL for webhook (if using webhook mode)
   - `DB_HOST`: Your Perfex CRM database host
   - `DB_USER`: Database username
   - `DB_PASSWORD`: Database password
   - `DB_NAME`: Database name

## Usage

### Running the bot in polling mode (development)

```
python app.py
```

### Running the bot with webhook (production)

1. Set the `WEBHOOK_URL` in your `.env` file
2. Deploy the application to your server
3. Run the Flask application:
```
python app.py
```

Alternatively, you can use a production WSGI server like Gunicorn:
```
gunicorn app:app
```

### Using the bot

1. Start a chat with your bot on Telegram
2. Send `/start` to see the main menu
3. Choose any of the options to generate reports or create a database backup

## Security Considerations

- Only authorized users (defined in `ADMIN_USER_IDS`) can access the bot
- Database credentials are stored in the `.env` file and not committed to version control
- The bot requires access to your Perfex CRM database, so make sure it runs in a secure environment

## Directory Structure

- `app.py`: Main application file with Flask and Telegram bot setup
- `database.py`: Database connection and backup functions
- `reports.py`: Functions for generating various reports
- `backups/`: Directory where database backups are stored
- `reports/`: Directory where generated reports are stored

## License

MIT 