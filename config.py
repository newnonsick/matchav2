import os

from dotenv import load_dotenv

load_dotenv(override=True)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ATTENDANCE_TRAINEE_CHANNEL_ID = int(os.getenv("ATTENDANCE_TRAINEE_CHANNEL_ID", ""))
ATTENDANCE_EMPLOYEE_CHANNEL_ID = int(os.getenv("ATTENDANCE_EMPLOYEE_CHANNEL_ID", ""))
OFFICE_ENTRY_SUMMARY_CHANNEL_ID = int(os.getenv("OFFICE_ENTRY_SUMMARY_CHANNEL_ID", ""))
LEAVE_SUMMARY_CHANNEL_ID = int(os.getenv("LEAVE_SUMMARY_CHANNEL_ID", ""))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

SMTP_SERVER = os.getenv("SMTP_SERVER", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
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
PKOB_UXUI_BOT_ID = 1372043337472806943

IGNORED_BOT_IDS = [
    TTS_NOTION_STANDUP_BOT_ID,
    CV_TRAINEE_NOTION_STANDUP_BOT_ID,
    PKOB_UXUI_BOT_ID,
]

PMHEE_USER_ID = 1029245548307419146
RECEIVED_STANDUP_REMOVAL_NOTIFICATION_USERIDS = [PMHEE_USER_ID]

MATCHA_HELP_IMG_URL = "https://qyjhozvrdsghqxjbaldu.supabase.co/storage/v1/object/public/matcha-image//matchaxbotnoi-n.png"

ENTRY_OFFICE_KEYWORDS = ["เข้าออฟฟิศ", "เข้าบริษัท", "เข้า office", "office", "onsite ออฟฟิศ"] # Only lowercase keywords
