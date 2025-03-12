import logging
import pandas as pd
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# 🔹 Replace this with your actual Telegram bot token from BotFather
BOT_TOKEN = "8063357607:AAEdHFNoSr7EcfodfmexZJxoHbtJTbjR_Ds"

# Excel file name
EXCEL_FILE = "fuel_data.xlsx"

# Conversation states
RTG_NUMBER, FUEL_PERCENTAGE = range(2)

# Dictionary to store user inputs temporarily
user_data = {}

# Logging (to debug issues)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks for RTG number."""
    user_id = update.message.chat_id  # Collect User ID automatically
    await update.message.reply_text("✅ Welcome! Please enter the **RTG number** (1, 2, 3, etc.):")

    # Store user ID
    user_data[user_id] = {}
    
    return RTG_NUMBER

async def get_rtg_number(update: Update, context: CallbackContext) -> int:
    """Receives RTG number and asks for fuel percentage."""
    user_id = update.message.chat_id
    rtg_number = update.message.text

    # Validate RTG input (must be a number)
    if not rtg_number.isdigit():
        await update.message.reply_text("❌ Please enter a valid RTG number (1, 2, 3, etc.).")
        return RTG_NUMBER
    
    user_data[user_id]["rtg_number"] = rtg_number
    await update.message.reply_text(f"✅ RTG {rtg_number} registered. Now enter the **fuel percentage**:")
    
    return FUEL_PERCENTAGE

async def get_fuel_percentage(update: Update, context: CallbackContext) -> int:
    """Receives fuel percentage and saves data."""
    user_id = update.message.chat_id
    fuel_percentage = update.message.text

    # Validate fuel percentage (must be a number between 0-100)
    if not fuel_percentage.isdigit() or not (0 <= int(fuel_percentage) <= 100):
        await update.message.reply_text("❌ Please enter a valid fuel percentage (0-100).")
        return FUEL_PERCENTAGE

    if user_id in user_data:
        user_data[user_id]["fuel_percentage"] = fuel_percentage

    rtg_number = user_data[user_id]["rtg_number"]

    # Save data to Excel
    save_to_excel(user_id, rtg_number, fuel_percentage)

    # Confirm data entry
    await update.message.reply_text(f"✅ Data saved:\n📅 **Date:** {datetime.today().strftime('%Y-%m-%d')}\n📌 **User ID:** {user_id}\n🔹 **RTG {rtg_number}** → ⛽ **Fuel: {fuel_percentage}%**")
    
    return ConversationHandler.END

def save_to_excel(user_id, rtg_number, fuel_percentage):
    """Save RTG fuel data to an Excel file with the current date."""
    
    # Get today's date in YYYY-MM-DD format
    today_date = datetime.today().strftime('%Y-%m-%d')

    # Create a dictionary with the data
    data = {
        "Date": [today_date],
        "User ID": [user_id],
        "RTG Number": [rtg_number],
        "Fuel Percentage": [fuel_percentage]
    }

    df = pd.DataFrame(data)

    # If file exists, append without overwriting
    if os.path.exists(EXCEL_FILE):
        existing_df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([existing_df, df], ignore_index=True)

    # Save to Excel
    df.to_excel(EXCEL_FILE, index=False)

async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels the conversation."""
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END

def main():
    """Start the bot."""
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            RTG_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_rtg_number)],
            FUEL_PERCENTAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fuel_percentage)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == '__main__':
    main()
