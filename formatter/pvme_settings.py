import requests


def github_json_request(url: str) -> dict:
    # todo: retry in case site some times fails to build
    return requests.get(url).json()


class PVMESpreadsheetData(dict):
    def __init__(self, url="https://raw.githubusercontent.com/pvme/pvme-settings/settings/pvme-spreadsheet/pvme_spreadsheet.json"):
        super().__init__(github_json_request(url))

    def cell_data(self, worksheet: str, col: str, row: int) -> str:
        rows = self.get(worksheet, {}).get(col, [])
        return rows[row] if row < len(rows) else 'N/A'
