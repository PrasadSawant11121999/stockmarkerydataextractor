from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime
from google.oauth2.service_account import Credentials

def upload_to_drive(file_path, file_name):
    SERVICE_ACCOUNT_FILE ='credentials.json'
    FOLDER_ID = '1AT9oGlI3cB-BJANi_d3r2SfpqpRtSSsv'
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    file_metadata = {
        'name': file_name,
        'parents': [FOLDER_ID] if FOLDER_ID else []
    }
    media = MediaFileUpload(file_path, resumable=True)
    request = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    )
    response = request.execute()
    print(f'File ID: {response.get("id")}')


def append_to_specific_sheet_in_folder(folder_id, file_name, content):
    # Define the scope
    SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

    # Authenticate and build the services
    SERVICE_ACCOUNT_FILE = 'credentials.json'
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)

    # Step 1: List all files in the folder
    results = drive_service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet'",
        pageSize=100,  # Adjust page size as needed
        fields="files(id, name)"
    ).execute()
    items = results.get('files', [])

    # Step 2: Search for the file by name
    sheet_id = None
    for item in items:
        if item['name'] == file_name:
            sheet_id = item['id']
            break

    if not sheet_id:
        print(f'No Google Sheet named "{file_name}" found in the specified folder.')
        return

    print(f'Found Google Sheet: {file_name} with ID: {sheet_id}')

    # Step 3: Append content to the Google Sheet
    sheet = sheets_service.spreadsheets()

    # Example: Append the current datetime and the provided content
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = [[current_datetime, content]]
    body = {
        'values': new_row
    }

    # Append the new row to the first sheet in the spreadsheet
    sheet.values().append(
        spreadsheetId=sheet_id,
        range='Sheet1!A1',  # Assuming you want to append to the first sheet
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()

    print(f"Appended to {file_name}: {new_row}")

# Example usage:
folder_id = '1AT9oGlI3cB-BJANi_d3r2SfpqpRtSSsv'
file_name = 'in'
append_to_specific_sheet_in_folder(folder_id, file_name, "This is some sample content")

