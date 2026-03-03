import os
import io
import logging
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from fpdf import FPDF
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    ContextTypes, ConversationHandler, PicklePersistence
)

# Load configuration
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN = os.getenv('ADMIN_TELE_HANDLE')

# State constants
CHOOSING_RECIPIENT, TYPING_WISH = range(2)

# Logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def clean_text(text):
    """Removes emojis and non-Latin characters to prevent PDF export errors."""
    if not text:
        return ""
    # 1. Replace common 'smart' punctuation with standard versions
    text = text.replace('\u201c', '"').replace('\u201d', '"').replace('\u2019', "'").replace('\u2014', '-')
    # 2. Keep only printable ASCII characters (32-126)
    cleaned = "".join(i for i in text if 31 < ord(i) < 127)
    return cleaned.strip()

# --- PDF GENERATOR ---
def create_card_buffer(name, wishes):
    """Generates a PDF in memory and returns a BytesIO object."""
    pdf = FPDF()
    # Using standard Helvetica (no extra .ttf needed since we clean everything)
    font_name = "Helvetica"

    # Front Page
    pdf.add_page()
    pdf.set_font(font_name, 'B', size=40)
    pdf.ln(80)
    pdf.cell(0, 20, "Happy Birthday,", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, 'B', size=50)
    pdf.cell(0, 20, f"{name}!", align='C', new_x="LMARGIN", new_y="NEXT")
    
    # Wishes Page
    pdf.add_page()
    pdf.set_font(font_name, 'B', size=18)
    pdf.cell(0, 10, "Messages from your friends:", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    pdf.set_font(font_name, size=12)
    for sender, msg in wishes.items():
        pdf.set_font(font_name, 'I', size=12)
        # multi_cell for the wish
        pdf.multi_cell(0, 8, f"\"{msg}\"")
        pdf.set_font(font_name, 'B', size=10)
        # Replaced long dash with standard hyphen '-' to prevent encoding errors
        pdf.cell(0, 8, f"- {sender}", align='R', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

    pdf_bytes = pdf.output() 
    buffer = io.BytesIO(pdf_bytes)
    buffer.name = f"{name}_Birthday_Card.pdf"
    buffer.seek(0) 
    return buffer

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🎂 *Welcome to the Birthday Bot!* 🎂\n\n"
        "I help collect birthday wishes and turn them into PDF cards.\n\n"
        "Type /help to see what I can do!"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = update.message.from_user.username == ADMIN
    
    help_text = (
        "📜 *Available Commands*\n\n"
        "👤 *For Everyone:*\n"
        "/write - Start writing a birthday wish for a friend.\n"
        "/help  - Show this menu.\n\n"
        "⚠️ *Note:* Please avoid using emojis, stickers, or special characters as they cannot be printed."
    )
    
    if is_admin:
        help_text += (
            "\n\n🛠 *Admin Only:*\n"
            "/blast  - Identify next month's babies and start collection.\n"
            "/export - Generate and receive all PDF cards.\n"
            "/clear  - Manually wipe all current wishes."
        )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def blast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.username != ADMIN: return
    
    try:
        df = pd.read_csv('birthdays.csv')
        next_month_idx = (datetime.now().month % 12) + 1
        month_name = datetime(2000, next_month_idx, 1).strftime('%b')

        df['Month'] = df['Birthday'].str.split(' ').str[1]
        babies = df[df['Month'] == month_name]['Name'].tolist()

        if not babies:
            await update.message.reply_text(f"No birthdays found for {month_name}.")
            return

        context.bot_data['current_babies'] = babies
        context.bot_data['wishes'] = {baby: {} for baby in babies}
        
        await update.message.reply_text(f"🎉 Collection started for {month_name}: {', '.join(babies)}")
    except Exception as e:
        await update.message.reply_text(f"Error reading CSV: {e}")

async def start_writing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    babies = context.bot_data.get('current_babies', [])
    if not babies:
        await update.message.reply_text("No active collections. Wait for the admin to /blast!")
        return ConversationHandler.END

    keyboard = [[name] for name in babies]
    await update.message.reply_text(
        "Who would you like to write a wish for?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )
    return CHOOSING_RECIPIENT

async def recipient_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['writing_to'] = update.message.text
    await update.message.reply_text(f"Type your message for {update.message.text} (text only, no emojis/stickers):", reply_markup=ReplyKeyboardRemove())
    return TYPING_WISH

async def save_wish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient = context.user_data['writing_to']
    sender = update.message.from_user.first_name or update.message.from_user.username
    
    # Handle non-text messages (stickers, photos, etc)
    if not update.message.text:
        await update.message.reply_text("⚠️ That wasn't a text message! Please type your wish using only letters and numbers.")
        return TYPING_WISH

    text = clean_text(update.message.text)
    
    if not text:
        await update.message.reply_text("⚠️ Your message was empty or contained only emojis/unsupported symbols. Please type a message using standard text!")
        return TYPING_WISH

    if 'wishes' not in context.bot_data: context.bot_data['wishes'] = {}
    if recipient not in context.bot_data['wishes']: context.bot_data['wishes'][recipient] = {}

    context.bot_data['wishes'][recipient][sender] = text
    await update.message.reply_text(f"✅ Wish for {recipient} saved!")
    return ConversationHandler.END

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.username != ADMIN: return
    wishes_data = context.bot_data.get('wishes', {})
    
    if not any(wishes_data.values()):
        await update.message.reply_text("No wishes have been collected yet.")
        return

    await update.message.reply_text("📤 Generating and sending cards...")
    for name, wishes in wishes_data.items():
        if wishes:
            try:
                pdf_buffer = create_card_buffer(name, wishes)
                await update.message.reply_document(document=pdf_buffer, filename=f"{name}_Card.pdf")
            except Exception as e:
                logging.error(f"Failed to generate card for {name}: {e}")
                await update.message.reply_text(f"❌ Could not generate card for {name} due to an encoding error.")

async def clear_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.username != ADMIN: return
    context.bot_data['wishes'] = {}
    context.bot_data['current_babies'] = []
    await update.message.reply_text("🧹 All current wishes and baby lists have been cleared.")

def main():
    if not os.path.exists("persistence_data"): os.makedirs("persistence_data")
    persistence = PicklePersistence(filepath="persistence_data/bot_state")
    
    app = Application.builder().token(TOKEN).persistence(persistence).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("write", start_writing)],
        states={
            CHOOSING_RECIPIENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, recipient_selected)],
            TYPING_WISH: [MessageHandler(filters.ALL & ~filters.COMMAND, save_wish)], # Changed to filters.ALL to catch stickers
        },
        fallbacks=[CommandHandler("help", help_command)],
        name="birthday_conv",
        persistent=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("blast", blast))
    app.add_handler(CommandHandler("export", export))
    app.add_handler(CommandHandler("clear", clear_data))
    app.add_handler(conv)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()