import PyPDF2
import mimetypes
from PIL import Image
from io import BytesIO
from datetime import datetime


def remove_pdf_metadata(pdf_file):
    """Remove metadata from a PDF file using PyPDF2."""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        if reader.metadata:
            writer = PyPDF2.PdfWriter()

            for page_num in range(len(reader.pages)):
                writer.add_page(reader.pages[page_num])

            output = BytesIO()
            writer.write(output)
            output.seek(0)

            return output
        else:
            return pdf_file

    except Exception as e:
        return pdf_file


def remove_exif(image_file):
    """Remove EXIF metadata from an image file"""
    try:
        image = Image.open(image_file)
        data = list(image.getdata())
        new_image = Image.new(image.mode, image.size)
        new_image.putdata(data)

        output = BytesIO()
        new_image.save(output, format=image.format)
        output.seek(0)
        return output
    except Exception as e:
        print(f"Error removing EXIF: {e}")
        return image_file


def get_file_metadata(file):
    content_type, _ = mimetypes.guess_type(file.name)
    metadata = {}
    metadata["owner"] = "Unknown"
    metadata["file_name"] = file.name
    metadata["file_size"] = file.size
    metadata["file_extension"] = file.name.split(".")[-1]
    metadata["content_type"] = content_type or "application/octet-stream"
    metadata["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metadata["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    metadata["writable"] = True
    metadata["readable"] = True
    metadata["executable"] = False

    if content_type:

        if content_type.startswith("image") or content_type in [
            "application/pdf",
            "text/plain",
        ]:
            metadata["writable"] = False
            metadata["executable"] = False
        else:
            metadata["writable"] = False
            metadata["executable"] = False
    else:
        metadata["writable"] = False
        metadata["executable"] = False

    return metadata
