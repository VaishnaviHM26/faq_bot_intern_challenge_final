import os
import io
from typing import Union

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False


def extract_text_from_file(file_source: Union[str, bytes, io.BytesIO], filename: str):
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        return _extract_txt(file_source)

    elif ext == ".pdf":
        return _extract_pdf(file_source)

    else:
        raise ValueError(
            f"Unsupported file format '{ext}'. Only .pdf and .txt files are supported."
        )


def _extract_txt(file_source):
    if isinstance(file_source, str):
        with open(file_source, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

    elif isinstance(file_source, bytes):
        content = file_source.decode("utf-8", errors="replace")

    else:
        file_source.seek(0)
        data = file_source.read()

        if isinstance(data, bytes):
            content = data.decode("utf-8", errors="replace")
        else:
            content = str(data)

    content = content.strip()

    if not content:
        raise ValueError("The uploaded TXT document is empty.")

    return {
        "text": content,
        "pages": [
            {
                "page": 1,
                "text": content
            }
        ]
    }


def _extract_pdf(file_source):

    if isinstance(file_source, str):
        stream = file_source

    elif isinstance(file_source, bytes):
        stream = io.BytesIO(file_source)

    else:
        stream = file_source

    pages = []

    # ---------- pdfplumber ----------
    if HAS_PDFPLUMBER:
        try:
            if hasattr(stream, "seek"):
                stream.seek(0)

            with pdfplumber.open(stream) as pdf:

                for page_num, page in enumerate(pdf.pages, start=1):
                    extracted = page.extract_text()

                    if extracted:
                        pages.append({
                            "page": page_num,
                            "text": extracted.strip()
                        })

        except Exception:
            pages = []

    # ---------- pypdf fallback ----------
    if not pages and HAS_PYPDF:

        try:

            if hasattr(stream, "seek"):
                stream.seek(0)

            reader = pypdf.PdfReader(stream)

            for page_num, page in enumerate(reader.pages, start=1):

                extracted = page.extract_text()

                if extracted:
                    pages.append({
                        "page": page_num,
                        "text": extracted.strip()
                    })

        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}")

    if not pages:
        raise ValueError(
            "Could not extract readable text from PDF."
        )

    full_text = "\n\n".join(page["text"] for page in pages)

    return {
        "text": full_text,
        "pages": pages
    }