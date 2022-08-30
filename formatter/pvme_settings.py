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
        'Perks': {...}
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
        '1111': ...
    }
    """
    def __init__(self, url="https://raw.githubusercontent.com/pvme/pvme-settings/settings/users/users.json"):
        users = {user['id']: user['name'] for user in github_json_request(url)}
        super().__init__(users)


class PVMERoleData(dict):
    """PVME Role LUT:
    {
        '785434303353454593': ('Raksha Master', 1234),
        '536406236988702750': (...)
    }
    """
    def __init__(self, url="https://raw.githubusercontent.com/pvme/pvme-settings/pvme-discord/roles.json"):
        roles = {role['id']: (role['name'], role['color']) for role in github_json_request(url)}
        super().__init__(roles)


class PVMEChannelData(dict):
    """PVME Channel LUT:
    {
        '553632787639435284': 'getting-started/perks.txt',
        '689234925064290323': ...
    }
    """
    def __init__(self, url="https://raw.githubusercontent.com/pvme/pvme-settings/pvme-discord/channels.json"):
        channels = {channel['id']: channel['path'] for channel in github_json_request(url)}
        super().__init__(channels)


if __name__ == '__main__':
    PVMESpreadsheetData()
    PVMEUserData()
    PVMERoleData()
    PVMEChannelData()
