# 🎂 Birthday Card Bot
A lightweight Telegram bot designed to automate the collection of monthly birthday wishes and generate elegant PDF cards. Built with Python, `python-telegram-bot`, and `fpdf2`.

### 📋 THINGS TO IMPROVE / DO:

- Support emojis

- Error handling for unknown commands

- Improve card design

### ✨ Key Features

- **Memory-Only PDF Generation**: PDFs are generated in RAM and sent directly to Telegram. No files are ever saved on your server/disk.

- **Stability First**: Automatically strips emojis and non-standard characters to prevent PDF generation crashes.

- **Persistent Memory**: Even if the bot restarts, it remembers current wishes and conversation states.

- **Admin Privac**y: Only the designated Admin can trigger monthly collections and export cards.

### 🛠️ Installation & Setup

1. **System Requirements**

   - Python 3.10+

   - A Telegram Bot Token (Get it from [@BotFather](https://t.me/botfather))

2. **Virtual Environment Setup**
   ```bash
   # Create the environment
   python -m venv venv

   # Activate it (Mac/Linux)
   source venv/bin/activate

   # Activate it (Windows)
   venv\Scripts\activate

   # Install dependencies
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. **Configuration**
   Create a `.env` file in the root directory (copy from `.env.sample`):
   ```
   TELEGRAM_BOT_TOKEN=<put_your_telegram_bot_token_here>
   ADMIN_TELE_HANDLE=<put_your_handle_without_at_here>
   ```

4. **Prepare Birthday Data**
   Create a birthdays.csv file in the root directory:
   ```
   Name,Tele Handle,Birthday
   Alice,alice_tele,15 Jan
   ob,bob_tele,22 Jan
   Charlie,charlie_tele,05 Feb
   ```
   Note: Ensure the month is a 3-letter abbreviation (Jan, Feb, Mar, etc.).

5. **Run the Bot**
   ```bash
   python bot.py
   ```

6. **Deactivate virtual environment**
   ```bash
   deactivate
   ```

### 🕹️ How to Use
| Command | Who | Description |
| --- | --- | --- |
| `/start` | Everyone | Initializes the bot and grants permission to message. |
| `/help` | Everyone | Displays available commands based on user permissions. |
| `/write` | Friends | Opens a menu to select a "birthday baby" and submit a wish. |
| `/blast` | **Admin** | Identifies next month's birthdays and opens collection. |
| `/export` | **Admin** | Generates all PDF cards and sends them to the Admin. |
| `/clear` | **Admin** | Wipes the current collection memory for a fresh start. |

### 🔧 Maintenance & Handover

- **Persistence Folder**: The `persistence_data/` folder contains the bot's memory. If you are handing this bot over to someone else, delete the `bot_state` file inside this folder to wipe old wishes.

- **Emoji Handling**: The bot is configured to strip emojis from messages. This ensures the PDF generator never crashes. Users are notified of this in the `/help` menu.

- **CSV Updates**: You can update `birthdays.csv` at any time. Run `/blast` again to refresh the list of "birthday babies" for the upcoming month.

### 📄 License
This project is open-source and free to use for personal birthday celebrations!
