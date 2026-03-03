# birthday-card-bot
Telegram Bot to automate monthly birthday wishes collection and PDF card generation.

### System Requirements

### Setting up in Virtual Environment

 1. Setup Virtual Environment
    ```
    $ python -m venv venv
    ```

 2. Activate Virtual Environment
    ```
    $ source venv/bin/activate
    ```

 3. Update pip to latest version
    ```
    $ python -m pip install --upgrade pip
    ```

 4. Repeat the above steps to set up the project in the virtual environment
    Run the following code to deactivate the virtual environment
    ```
    $ deactivate
    ```

 Note: Run all future commands after activating virtual environment to ensure consistencies

### Getting Started

 1. Install Python Dependencies

    ```
    $ pip install -r requirements.txt
    ```

 2. Create the environment file (make a copy of `env.sample` and rename it to `.env`).
    Add the details for each environment variable.

    ```
    TELEGRAM_BOT_TOKEN=<put_your_telegram_bot_token_here>
    ADMIN_TELE_HANDLE=<put_your_handle_without_at_here>
    ```

 3. Create the birthdays csv file (make a copy of `birthdays_sample.csv` and rename it to `birthdays.csv`).
    ```
    Name,Tele Handle,Birthday
    Alice,alice_telehandle,5 Dec
    Bob,bob_telehandle,4 May
    Charlie,charlie_telehandle,11 Jan
    ```

 4. Run the python telegram server
    ```
    $ python main.py
    ```

### Commands
- `/blast`: (Admin Only) Looks at next month and opens collection.
- `/write`: Users run this to submit their wishes.
- `/export`: (Admin Only) Generates PDFs and sends them to you.

### Data Maintenance
The bot saves data in `persistence_data/`. Do not delete this folder unless you want to wipe all unsaved wishes.
