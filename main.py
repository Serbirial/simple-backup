import sys, json, os

import time


from backup import zip # fuk ya builtins

_default_path = os.path.expanduser("~/simple-backup/config.json")

ARGS = {
    "config": {
        "data": _default_path,
        "help": "Specifies a config file to load, defaults to the one provided next to main.py",
        "usage": "--config=/path/to/config.json"
    },
    "comp-level": { # TODO: implement
        "data": 1,
        "help": "Sets the compression level, defaults to 1",
        "usage": "--comp-level=5"
    }

}
FLAGS = {
    "debug": False,
    "restore": False
}



class Config:
    def __init__(self, path):
        self.load_config(path)

    def load_config(self, path):
        if os.path.isfile(path):
            print("Loaded given config")
            temp = json.loads(open(path, 'r').read())
        elif os.path.isfile(_default_path):
            print("Couldnt find given config, fallback to default")
            temp = json.loads(open(_default_path, 'r').read())
        else:
            print("Cant find config file, exiting...")
            exit(0) # TODO: dont exit
        if not all(k in temp for k in ("sleep", "dirs", "dest", "tmpfile_location", "plugins")):
            print("Malformed JSON config.")
            exit(0)
        elif type(temp["sleep"]) != int or type(temp["dirs"]) != list:
            print("Malformed JSON keys.")
            exit(0)
        self.sleep = temp["sleep"]
        self.tmpdir = temp["tmpfile_location"]
        self.dirs = [x for x in temp["dirs"]]
        self.dest = temp["dest"]
        self.plugins = temp["plugins"]
        del temp
        dirprint = ""
        for path in self.dirs:
            dirprint += f"   * {path}\n"
        print(f"Loaded directories:\n{dirprint}")

def parse_args():
    raw_args = sys.argv
    real_args = []
    for arg in raw_args:
        if arg.startswith("--"):
            if "=" not in arg:
                print("invalid argument use, usage: --arg=var")
                exit(0)
            key,value = arg.split("--", 1)[1].split("=", 1)
            real_args.append((key, value))
        elif arg.startswith("-"):
            key, value = arg.split("-", 1)
            real_args.append(value)
    return real_args

if __name__ == "__main__":
    args = parse_args()

    for arg in args:
        if type(arg) == tuple: # Actual arg
            if arg[0] in ARGS:
                ARGS[arg[0]]["data"] = arg[1]
        else: # Flag
            if arg in FLAGS:
                if FLAGS[arg] == False:
                    FLAGS[arg] = True
                elif FLAGS[arg] == True:
                    FLAGS[arg] = True
    if FLAGS["debug"]:
        print(FLAGS)
        print(ARGS)
    config = Config(ARGS["config"]["data"]) # TODO: custom config location support

  #  start = time.time()
    addons = config.plugins
    for _dir in config.dirs:
        name = _dir.split("/")[-1] # TODO: improve this
        if FLAGS["restore"]:
            zenv = zip.Zip(name, directory=_dir, temp_path=config.tmpdir, addons=addons, dest=config.dest, read_mode=True)
            print(f"Unzipping and decompressing {name} ({_dir})")
            _, total = zenv.decompress()
            print(f"Restored {total} files")
        elif not FLAGS["restore"]:
            zenv = zip.Zip(name, directory=_dir, temp_path=config.tmpdir, addons=addons, dest=config.dest)
            print(f"Compressing and zipping {name} ({_dir})")
            _, total = zenv.compress()
            print(f"Compressed {total} files.\n")

        #print(f"Unzipping and decompressing {_dir}")
        #zenv.unzip()
        #zenv.load_compressed()
        #zenv.decompress(restore=True)
        #print("Restored.")

 #   end = time.time()

#    print(end - start)
