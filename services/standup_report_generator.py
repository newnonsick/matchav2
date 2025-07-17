from datetime import datetime
from io import BytesIO

import pandas as pd
import pytz
from openpyxl.styles import Alignment

from utils.standup_utils import extract_bullet_points


class StandupReportGenerator:
    def generate_report(self, user_name: str, month: str, standups: list) -> BytesIO:
        data = []
        bangkok_tz = pytz.timezone("Asia/Bangkok")

        for standup in standups:
            date_obj_utc = datetime.fromisoformat(
                standup["timestamp"].replace("Z", "+00:00")
            )
            date_obj_bkk = date_obj_utc.astimezone(bangkok_tz)
            datetime_formatted = date_obj_bkk.strftime("%d/%m/%Y %H:%M:%S")
            month_formatted = date_obj_bkk.strftime("%Y-%m")
            data.append(
                {
                    f"Report {month_formatted}: {user_name}": datetime_formatted,
                    " ": extract_bullet_points(standup["content"]),
                }
            )

        df = pd.DataFrame(data)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            sheet_name = f"{user_name}_standup_{month}"
            df.to_excel(writer, index=False, sheet_name=sheet_name)

            worksheet = writer.sheets[sheet_name]
            worksheet.column_dimensions["A"].width = 40
            worksheet.column_dimensions["B"].width = 80

            alignment_top = Alignment(vertical="top", wrap_text=True)
            for row in worksheet.iter_rows(
                min_row=2, max_row=worksheet.max_row, min_col=1, max_col=2
            ):
                for cell in row:
                    cell.alignment = alignment_top

        buffer.seek(0)
        return buffer
