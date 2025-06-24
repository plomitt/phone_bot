# Telegram AI Phone Number Checker Bot
<img width="1361" alt="Screenshot 2025-06-25 at 1 22 10 AM" src="https://github.com/user-attachments/assets/bda63c10-e0b8-4c19-9fee-6b9120fbbed9" />
This project contains a Telegram bot designed to periodically check for a specific phone number on a webpage. It utilizes Selenium for web automation and the Google Gemini API for CAPTCHA solving.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Files](#files)
- [Setup](#setup)
- [Usage](#usage)
- [How it works](#how-it-works)

## Project Overview

The core of this project is a Telegram bot that automates checking for the presence of a user-defined phone number on the website of the mobile phone operator MegaFon. This is needed if a customer wants to reserve and purchase a specific phone number. 
The bot is built to handle common web scraping challenges like CAPTCHAs, ensuring continuous operation.

## Features

- **Set Target Phone Number**: Configure the phone number the bot should look for.
- **Get Current Target Phone Number**: Retrieve the currently set target phone number.
- **Start/Stop Checking**: Manually start and stop the periodic checks.
- **Adjust Notification Settings**:
    - `set_notif_amount`: Control how many notifications are sent when a match is found.
    - `set_notif_step`: Set the interval for sending "no-result" notifications.
- **CAPTCHA Solving**: Integrates with Google Gemini to automatically solve CAPTCHAs encountered during web scraping.

## Files

- `tel_bot.py`: The main Telegram bot application. It handles user commands, manages the checking process, and sends notifications.
- `bot.py`: Contains the core logic for web scraping using Selenium, including setting up the browser, handling CAPTCHAs, entering phone numbers, expanding sections, and extracting numbers from the webpage.
- `gemini.py`: Provides functions for interacting with the Google Gemini API, specifically for uploading CAPTCHA images and getting text responses.
- `helpers.py`: A utility file containing helper functions such as phone number format validation, number shortening, ASCII art generation for console messages, and managing notification settings.
- `constants.py`: This file holds constants like `PAGE_LINK` for the target website URL.
- `shared.py`: This file contains shared objects for inter-thread communication.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (You will need to create a `requirements.txt` file if it doesn't exist, including `python-telegram-bot`, `selenium`, `google-generativeai`, `python-dotenv`, and `pyfiglet`).

3.  **Environment Variables:**
    Create a `.env` file in the project root and add the following:
    ```
    TEL_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```
    * **Telegram Bot Token**: Obtain this from BotFather on Telegram.
    * **Gemini API Key**: Get this from the Google AI Studio.

4.  **ChromeDriver**: Ensure you have ChromeDriver installed and its path is accessible to your system. You can download it from the official ChromeDriver website.

## Usage

1.  **Run the bot:**
    ```bash
    python tel_bot.py
    ```

2.  **Interact with the bot on Telegram:**

    * `/start`: Initializes the bot.
    * `/set_num`: Prompts you to enter the phone number to be checked (format: `+7 123 456 7890`).
    * `/get_num`: Displays the current target phone number.
    * `/start_check`: Begins the periodic checking process.
    * `/stop_check`: Halts the checking process.
    * `/set_notif_amount`: Cycles through different notification amounts for successful matches.
    * `/set_notif_step`: Cycles through different intervals for "no-result" notifications.

## How it works

The `tel_bot.py` script sets up the Telegram bot with various command handlers. When `/start_check` is invoked, a new thread is spawned to run `run_periodically` from `bot.py`.

`run_periodically` continuously calls `check_phone_num` at regular intervals. `check_phone_num` uses Selenium to:
1.  Navigate to the `PAGE_LINK`.
2.  Check for and solve CAPTCHAs using the `gemini.py` module.
3.  Enter the target phone number.
4.  Expand all relevant sections on the page to reveal hidden numbers.
5.  Extract all displayed phone numbers.
6.  Compare the extracted numbers with the target number.

The results of each check (match found, no match, or error) are put into an asynchronous queue (`msg_queue`), which is then picked up by the `send_check_result` function in `tel_bot.py` to send notifications back to the user on Telegram.
