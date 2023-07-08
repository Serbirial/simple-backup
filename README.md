# simple-backup
 Simple python backup tool with a low memory footprint for machines with limited memory.
 
 Note: If you run into out of memory errors, please make a issue and list the file sizes of every file being backed up, along with your total memory.

## Usage
 ALWAYS USE FULL FILE PATHS, EVEN IN THE CONFIG
* `python3.10 main.py --config=/full/path/to/config.json` Backs up files given in `config.json`
* `python3.10 main.py --config=/full/path/to/config.json -restore` Restores backed up folders and files into the destination in `config.json`
