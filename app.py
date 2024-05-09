# app.py
import sys
from bot.client import run

if __name__ == "__main__":
    run(sys.argv[1:])  # Pass command line to run
c