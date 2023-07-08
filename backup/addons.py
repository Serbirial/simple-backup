moddable_funcs = set("test_func")


from dataclasses import dataclass

@dataclass
class Addon:
    name: str
    path: str
    funcs: dict
    to_replace: dict

def load(paths: list[str]):
    global _addons
    _addons = []
    for file in paths:
        _funcs = {}
        _raw = __import__(file)
        if not hasattr(_raw, "export"):
            print("ADDON HAS NO EXPORT")
            exit(0)
        if not all(k in _raw.export for k in ("replaces", "name", "path", "funcs")):
            print("Export is invalid.")
            exit(0)
        exports = _raw.export
        if not "replaces" in exports:
            print("Addon export doesnt replace any functions")
            exit(0)
        for func in exports["funcs"]:
            if "name" not in func:
                print("Func in export funcs doesnt have name.")
                exit(0)
            _funcs[func["name"]] = func["callable"]  
        for modified_func_data in exports["replaces"]:
            if "name" not in modified_func_data:
                print("Addon is trying to replace a function without specifying/giving a name.")
                exit(0)
            elif "name" not in moddable_funcs:
                print("Addon is trying to replace a function that is not replacable.")
                exit(0)
            
        _addons.append(Addon(name=exports["name"], path=exports["path"], funcs=_funcs, to_replace=exports["replaces"]))

def get_addons():
    return _addons
