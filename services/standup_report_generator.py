import pandas as pd
import pytz
from io import BytesIO
from datetime import datetime


class StandupReportGenerator:
    def generate_report(self, user_name: str, month: str, standups: list) -> BytesIO:
        data = []
        bangkok_tz = pytz.timezone("Asia/Bangkok")

        for standup in standups:
            date_obj_utc = datetime.fromisoformat(
                standup["timestamp"].replace("Z", "+00:00")
            )
            date_obj_bkk = date_obj_utc.astimezone(bangkok_tz)
            date_formatted = date_obj_bkk.strftime("%Y-%m-%d %H:%M:%S")
            data.append({"Date": date_formatted, "Content": standup["content"]})

        df = pd.DataFrame(data)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=f"{user_name}_Standup_{month}")

        buffer.seek(0)
        return buffer
