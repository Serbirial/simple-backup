import importlib.machinery

moddable_funcs = [
    "compress",
    "decompress"
]

from dataclasses import dataclass

@dataclass
class Addon:
    name: str
    path: str
    to_replace: dict

def load(paths: list[str], data: dict):
    global _addons
    _addons = []
    for file in paths:
        name = file.split("/")[-1].split(".")[0]
        _raw = importlib.machinery.SourceFileLoader(name, file).load_module()
        if not hasattr(_raw, "init"):
            print("ADDON HAS NO INIT")
            exit(0)
        addon = _raw.init(data)
        if not hasattr(addon, "exports"):
            print("ADDON HAS NO EXPORTS")
            exit(0)
        exports = addon.exports
        if not "replaces" in exports:
            print("Addon export doesnt replace any functions")
            exit(0)
        for name in exports["replaces"].keys():
            if name not in moddable_funcs:
                print("Addon is trying to replace a function that is not replacable.")
                exit(0)
        _addons.append(Addon(name=exports["name"], path=file, to_replace=exports["replaces"]))

def get_addons():
    return _addons
