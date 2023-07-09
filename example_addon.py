class SomeAddon:
    def __init__(self, data):
        self.data = data # The data you will be provided with outside of folder names and their containing files

        # NOTE: This is needed, you will need to define any functions you wish to 'replace' here.
        self.exports = {
            "name": "Test Addon", # The name of your addon.
            "replaces": {"compress": self.compress}, # The function it replaces, check backup/addons.py for a list of replacable functions and explanations
        }

    def compress(self, parent, files):
        print(f"Given {parent}: {'  *'.join(files)}")
        return len(files)


# NOTE: THIS IS ALSO NEEDED, DO NOT MODIFY THE NAME.
def init(data: dict) -> SomeAddon:
    return SomeAddon(data)

