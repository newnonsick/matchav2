import asyncio
from io import BytesIO
import zipfile
from typing import List, Tuple


async def compress_files_to_zip(
    files: List[Tuple[str, BytesIO]], file_name: str
) -> BytesIO:
    def _compress():
        zip_buffer = BytesIO()
        zip_buffer.name = file_name
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for f_name, f_content in files:
                zip_file.writestr(f_name, f_content.getvalue())
        zip_buffer.seek(0)
        return zip_buffer

    return await asyncio.to_thread(_compress)
