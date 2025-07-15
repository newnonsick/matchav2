from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from io import BytesIO
from datetime import datetime


class StandupReportGenerator:
    def generate_report(self, user_name: str, month: str, standups: list) -> BytesIO:
        document = Document()
        document.add_heading(f"Stand-Up Report for {user_name} - {month}", level=1)

        if not standups:
            document.add_paragraph("No stand-up entries found for this period.")
        else:
            for standup in standups:
                date_obj = datetime.fromisoformat(
                    standup["timestamp"].replace("Z", "+00:00")
                )
                date_formatted = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                p = document.add_paragraph()
                p.add_run(f"Date: {date_formatted}\n").bold = True
                p.add_run(standup["content"])
                document.add_paragraph()

        buffer = BytesIO()
        document.save(buffer)
        buffer.seek(0)
        return buffer
