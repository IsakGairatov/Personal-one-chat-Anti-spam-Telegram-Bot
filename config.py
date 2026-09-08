import os
from dotenv import load_dotenv


load_dotenv()

CHAT_ID = int(os.getenv("CHAT_ID"))
BOT_TOKEN = os.getenv("BOT_TOKEN")


Reply_to_spam = os.getenv("Reply_to_spam")
Reply_to_link=os.getenv("Reply_to_link")
Ban_notif = os.getenv("Ban_notif")

GEMINI_ANTI_SPAM_API_KEY = os.getenv("GEMINI_ANTI_SPAM_API_KEY")
GEMINI_GOOGLING_API_KEY = os.getenv("GEMINI_GOOGLING_API_KEY")