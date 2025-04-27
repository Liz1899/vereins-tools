import csv
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
except ImportError:
    gspread = None
    ServiceAccountCredentials = None

def load_csv(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        return list(reader)

def load_google_sheet(service_account_json, spreadsheet_id):
    if not gspread or not ServiceAccountCredentials:
        raise ImportError("gspread and oauth2client are required for Google Sheets access.")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_json, scope)
    gs_client = gspread.authorize(creds)
    sheet = gs_client.open_by_key(spreadsheet_id).sheet1
    return sheet.get_all_records()