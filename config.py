import os
from dotenv import load_dotenv


load_dotenv()

CHAT_ID = int(os.getenv("Test_chat_id"))
BOT_TOKEN = os.getenv("BOT_TOKEN")
Reply_to_spam = os.getenv("Reply_to_spam")