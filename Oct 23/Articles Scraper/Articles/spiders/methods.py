import csv
import glob


def get_key_values_from_file():
    # self.gsheet_config = self.get_key_values_from_file('input/googlesheet_keys.txt')
    file_path = glob.glob('input/googlesheet_keys.txt')
    # self.google_sheet_csv_download_url_t = 'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&id={spreadsheet_id}&gid={tab_id}'

    """
    Get the Google sheet keys and Search URLs keys  from input text file
    """

    with open(file_path, mode='r', encoding='utf-8') as input_file:
        data = {}

        for row in input_file.readlines():
            if not row.strip():
                continue

            try:
                key, value = row.strip().split('==')
                data.setdefault(key.strip(), value.strip())
            except ValueError:
                pass

        return data


def read_output_files():
    output_files = glob.glob('output/*.csv')
    rows = []

    for output_file in output_files:
        with open(output_file, mode='r', encoding='utf8') as input_file:
            csv_reader = csv.DictReader(input_file)
            for row in csv_reader:
                rows.append(row)

    return rows


def update_google_sheet(data):
    # if not self.current_scraped_items:
    #     self.logger.debug('\n\nThere is no new article found...!!!\n\n')
    #     return

    columns = [[col for col in row.keys()] for row in data][:1]
    rows_values = [[value for value in row.values()] for row in data]

    if not data:
        rows_values = columns + [[value for value in row.values()] for row in data]

    spreadsheet_id = self.gsheet_config.get('googlesheet_id')
    tab_sheet_name = self.gsheet_config.get(f'tab_name')

    service = build('sheets', 'v4', credentials=self.creds)
    sheet_range = tab_sheet_name  # Sheet name and range of the cells7

    # append data
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=sheet_range,
        body={
            "majorDimension": "ROWS",
            "values": rows_values  # representing each row values as list. So it contains as list of lists
        },
        valueInputOption="USER_ENTERED"
    ).execute()

    self.logger.debug(f'\n\nNew Articles Found: "{len(self.current_scraped_items)}"')
    self.logger.debug(f'Google Sheet "{tab_sheet_name}" has been updated\n\n')
