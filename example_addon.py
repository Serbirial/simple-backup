class SomeAddon:
    def __init__(self, data):
        self.data = data # The data you will be provided with outside of folder names and their containing files

        # NOTE: This is needed, you will need to define any functions you wish to 'replace' here.
        self.exports = {
            "name": "Test Addon", # The name of your addon.
            "replaces": {"compress": self.compress}, # The function it replaces, check backup/addons.py for a list of replacable functions and explanations
        }

    def compress(self, parent, files):
        _files = ''
        for x in files:
            _files += f"\n   * {x}"
        print(f"Given {parent}: {_files}")
        return len(files)



def init(data: dict) -> SomeAddon: # Needed
    return SomeAddon(data)

