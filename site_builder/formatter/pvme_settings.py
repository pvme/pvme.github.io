import requests


def github_json_request(url: str) -> dict:
    # todo: retry in case site some times fails to build
    return requests.get(url).json()


class PVMESpreadsheetData(dict):
    """PVME Spreadsheet LUT:
    {
        "cells": {
            "prices": {
            "A": ["10", "20", "30"],
            "B": ["30", "-1", "20,3"]
            },
            "Perks": {...}
        },
        "cell_aliases": {
            "gptotal_archglacor_200ks": "20",
            ...
        }
    }
    """
    def __init__(self, url="https://raw.githubusercontent.com/pvme/pvme-settings/settings/pvme-spreadsheet/pvme_spreadsheet.json"):
        super().__init__(github_json_request(url))

    def cell(self, worksheet: str, col: str, row: int) -> str:
        rows = self.get('cells', {}).get(worksheet, {}).get(col, [])
        return rows[row] if row < len(rows) else 'N/A'

    def cell_alias(self, alias: str) -> str:
        return self.get('cell_aliases', {}).get(alias, 'N/A')


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
        '534912860711550989': {
            'name': 'dpm-advice-ranged',
            'path': 'dpm-advice/dpm-advice-range.txt'
        },
        '689234925064290323': {...}
    }
    """
    def __init__(self, url="https://raw.githubusercontent.com/pvme/pvme-settings/pvme-discord/channels.json"):
        channels = {channel['id']: {'path': channel['path'], 'name': channel['name']} for channel in
                    github_json_request(url)}

        # remove pvm-help (was used in some testing in #website but gives 404)
        # todo: remove when pvm-help is removed from channels.txt
        pvm_help_id = None
        for id_, settings in channels.items():
            if settings.get('name') == 'pvm-help':
                pvm_help_id = id_
        if pvm_help_id:
            channels.pop(pvm_help_id)

        super().__init__(channels)


if __name__ == '__main__':
    PVMESpreadsheetData()
    PVMEUserData()
    PVMERoleData()
    PVMEChannelData()
