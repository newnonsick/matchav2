from io import BytesIO
import zipfile


def compress_files_to_zip(files: list[tuple[str, BytesIO]], file_name: str) -> BytesIO:
    zip_buffer = BytesIO()
    zip_buffer.name = file_name
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_name, file_content in files:
            zip_file.writestr(file_name, file_content.getvalue())

    zip_buffer.seek(0)
    return zip_buffer
