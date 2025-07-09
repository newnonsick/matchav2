import os

from dotenv import load_dotenv

load_dotenv(override=True)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ATTENDANCE_TRAINEE_CHANNEL_ID = int(os.getenv("ATTENDANCE_TRAINEE_CHANNEL_ID", ""))
ATTENDANCE_EMPLOYEE_CHANNEL_ID = int(os.getenv("ATTENDANCE_EMPLOYEE_CHANNEL_ID", ""))
LEAVE_SUMMARY_CHANNEL_ID = int(os.getenv("LEAVE_SUMMARY_CHANNEL_ID", ""))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
