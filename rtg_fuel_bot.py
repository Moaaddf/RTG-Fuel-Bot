import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from airtable import Airtable
import os

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Airtable API Setup
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")  # Using environment variable for security
BASE_ID = 'appg4nfJBQvlay1rc'  # Replace with your Base ID
TABLE_NAME = 'Fuel Log'  # Replace with your Table Name
airtable = Airtable(BASE_ID, TABLE_NAME, AIRTABLE_API_KEY)

# Command to start the bot
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Please provide your RTG number.")

# Function to save the data into Airtable
def save_to_airtable(rtg_number, fuel_percentage, user_id):
    data = {
        'User ID': user_id,
        'RTG Number': rtg_number,
        'Fuel Percentage': fuel_percentage,
        'Date': '2025-03-15'  # Example static date, you can replace it with actual date if needed
    }
    airtable.insert(data)
    print(f"Record saved: {data}")

# Function to collect RTG number
def get_rtg(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    update.message.reply_text("Please enter the RTG number.")

    # Capture RTG number from user input
    rtg_number = update.message.text
    context.user_data['rtg_number'] = rtg_number

    update.message.reply_text(f"RTG number {rtg_number} received. Now, please enter the fuel percentage.")

# Function to collect fuel percentage and save both RTG and fuel data
def get_fuel_percentage(update: Update, context: CallbackContext):
    fuel_percentage = update.message.text
    rtg_number = context.user_data['rtg_number']
    user_id = update.message.from_user.id

    # Save data to Airtable
    save_to_airtable(rtg_number, fuel_percentage, user_id)

    update.message.reply_text(f"Fuel percentage {fuel_percentage}% for RTG {rtg_number} saved.")

# Function to handle errors
def error(update: Update, context: CallbackContext):
    logger.warning(f'Update {update} caused error {context.error}')

def main():
    # Set up the Updater
    BOT_TOKEN = os.getenv("BOT_TOKEN")  # Your Telegram Bot Token
    updater = Updater(BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register commands
    dp.add_handler(CommandHandler("start", start))

    # Register message handlers for RTG number and fuel percentage
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, get_rtg))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, get_fuel_percentage))

    # Register error handler
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
