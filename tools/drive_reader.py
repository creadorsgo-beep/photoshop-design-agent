"""
Google Drive + Docs integration.
First run triggers an OAuth browser flow and saves a token file for future use.

Setup:
  1. Google Cloud Console → create project → enable Drive API + Docs API
  2. Credentials → OAuth 2.0 Client ID (Desktop app) → download JSON
  3. Save as credentials/credentials.json (or path in GOOGLE_CREDENTIALS_FILE)
"""

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def _get_credentials() -> Credentials:
    creds = None
    token_file = os.getenv("GOOGLE_TOKEN_FILE", "credentials/token.json")
    creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials/credentials.json")

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_file):
                raise FileNotFoundError(
                    f"Google credentials not found at '{creds_file}'. "
                    "Download credentials.json from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)

        os.makedirs(os.path.dirname(token_file), exist_ok=True)
        with open(token_file, "w") as f:
            f.write(creds.to_json())

    return creds


def list_files(folder_id: str | None = None, file_type: str = "all") -> list[dict]:
    """
    List files in a Drive folder.
    file_type: 'all' | 'docs' | 'sheets'
    Returns list of {id, name, mimeType, modifiedTime}.
    """
    creds = _get_credentials()
    service = build("drive", "v3", credentials=creds)

    folder_id = folder_id or os.getenv("DRIVE_FOLDER_ID", "")
    query_parts = ["trashed = false"]

    if folder_id:
        query_parts.append(f"'{folder_id}' in parents")

    mime_filters = {
        "docs": "mimeType='application/vnd.google-apps.document'",
        "sheets": "mimeType='application/vnd.google-apps.spreadsheet'",
    }
    if file_type in mime_filters:
        query_parts.append(mime_filters[file_type])

    results = (
        service.files()
        .list(
            q=" and ".join(query_parts),
            pageSize=50,
            fields="files(id, name, mimeType, modifiedTime)",
            orderBy="modifiedTime desc",
        )
        .execute()
    )
    return results.get("files", [])


def read_sheet(sheet_id: str, range_: str = "") -> str:
    """
    Read a Google Spreadsheet and return its content as a formatted text table.
    Detects all sheets automatically if no range is specified.
    """
    creds = _get_credentials()
    service = build("sheets", "v4", credentials=creds)

    # Get sheet metadata
    meta = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    title = meta.get("properties", {}).get("title", "")
    sheets = meta.get("sheets", [])

    lines = [f"# {title}\n"]

    for sheet in sheets:
        sheet_name = sheet["properties"]["title"]
        lines.append(f"\n## Hoja: {sheet_name}\n")

        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=sheet_name)
            .execute()
        )
        rows = result.get("values", [])
        if not rows:
            lines.append("(vacía)")
            continue

        # Header separator
        max_cols = max(len(r) for r in rows)
        for i, row in enumerate(rows):
            # Pad short rows
            padded = row + [""] * (max_cols - len(row))
            lines.append(" | ".join(padded))
            if i == 0:
                lines.append("-" * (sum(max(len(str(c)) for c in col) for col in zip(*rows)) + max_cols * 3))

    return "\n".join(lines)


def read_document(doc_id: str) -> str:
    """
    Read a Google Document or Spreadsheet — auto-detects the file type.
    Returns plain-text content.
    """
    creds = _get_credentials()
    # Detect file type via Drive API
    drive_service = build("drive", "v3", credentials=creds)
    meta = drive_service.files().get(fileId=doc_id, fields="mimeType,name").execute()
    mime = meta.get("mimeType", "")

    if "spreadsheet" in mime:
        return read_sheet(doc_id)

    # Google Doc
    docs_service = build("docs", "v1", credentials=creds)

    doc = docs_service.documents().get(documentId=doc_id).execute()
    title = doc.get("title", "")
    lines = [f"# {title}\n"]

    for element in doc.get("body", {}).get("content", []):
        if "paragraph" in element:
            para = element["paragraph"]
            para_style = para.get("paragraphStyle", {}).get("namedStyleType", "")
            text = ""
            for pe in para.get("elements", []):
                if "textRun" in pe:
                    text += pe["textRun"].get("content", "")
            text = text.rstrip("\n")
            if text:
                prefix = ""
                if "HEADING_1" in para_style:
                    prefix = "## "
                elif "HEADING_2" in para_style:
                    prefix = "### "
                lines.append(prefix + text)

        elif "table" in element:
            # Flatten table cells
            for row in element["table"].get("tableRows", []):
                row_texts = []
                for cell in row.get("tableCells", []):
                    cell_text = ""
                    for cp in cell.get("content", []):
                        if "paragraph" in cp:
                            for pe in cp["paragraph"].get("elements", []):
                                if "textRun" in pe:
                                    cell_text += pe["textRun"].get("content", "")
                    row_texts.append(cell_text.strip())
                lines.append(" | ".join(row_texts))

    return "\n".join(lines)
