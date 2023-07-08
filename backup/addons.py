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
    funcs: dict
    to_replace: dict
    insert_imports: callable

def load(paths: list[str]):
    global _addons
    _addons = []
    for file in paths:
        _funcs = {}
        name = file.split("/")[-1].split(".")[0]
        _raw = importlib.machinery.SourceFileLoader(name, file).load_module()
        if not hasattr(_raw, "exports"):
            print("ADDON HAS NO EXPORTS")
            exit(0)
        if not all(k in _raw.exports for k in ("replaces", "name")):
            print("Export is invalid.")
            exit(0)
        exports = _raw.exports
        if not "replaces" in exports:
            print("Addon export doesnt replace any functions")
            exit(0)
        for name, _callable in exports["replaces"].items():
            if name not in moddable_funcs:
                print("Addon is trying to replace a function that is not replacable.")
                exit(0)
        if not "insert_imports" in dir(_raw):
            print("Addon is missing function to insert imports")
            exit(0)
        _addons.append(Addon(name=exports["name"], path=file, funcs=_funcs, to_replace=exports["replaces"], insert_imports=_raw.insert_imports))

def get_addons():
    return _addons
