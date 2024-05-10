# app.py
import sys
from bot.client import run
print("initializing Discord Bot...")
if __name__ == "__main__":
    run(sys.argv[1:])