from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)

from telegram_bot.main import main

if __name__ == "__main__":
    main()