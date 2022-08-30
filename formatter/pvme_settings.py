import requests


def github_json_request(url: str) -> dict:
    # todo: retry in case site some times fails to build
    return requests.get(url).json()


class PVMESpreadsheetData(dict):
    """PVME Spreadsheet LUT:
    {
        'prices': {
            'A': ['10', '20', '30'],
            'B': ['30', '-1', '20,3']
        },
        'Perks': {}
    }
    """
    def __init__(self, url="https://raw.githubusercontent.com/pvme/pvme-settings/settings/pvme-spreadsheet/pvme_spreadsheet.json"):
        super().__init__(github_json_request(url))

    def cell_data(self, worksheet: str, col: str, row: int) -> str:
        rows = self.get(worksheet, {}).get(col, [])
        return rows[row] if row < len(rows) else 'N/A'


class PVMEUserData(dict):
    """PVME User LUT:
    {
        '1234': 'Pleb',
        '1111': 'User2'
    }
    """
    def __init__(self, url="https://raw.githubusercontent.com/pvme/pvme-settings/settings/users/users.json"):
        users = {user['id']: user['name'] for user in github_json_request(url)}
        super().__init__(users)


class PVMEChannelData(dict):
    pass


if __name__ == '__main__':
    PVMESpreadsheetData()
    PVMEUserData()
    PVMEChannelData()
