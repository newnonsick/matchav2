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

SMTP_SERVER = os.getenv("SMTP_SERVER", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

LEAVE_TYPE_MAP = {
    "annual_leave": "ลาพักร้อน",
    "sick_leave": "ลาป่วย",
    "personal_leave": "ลากิจ",
    "birthday_leave": "ลาวันเกิด",
}
PARTIAL_LEAVE_MAP = {
    "afternoon": "ครึ่งบ่าย",
    "morning": "ครึ่งเช้า",
}

TTS_NOTION_STANDUP_BOT_ID = 1374302702917517392
CV_TRAINEE_NOTION_STANDUP_BOT_ID = 1374335354907394089
