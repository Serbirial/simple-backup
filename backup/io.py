from dataclasses import dataclass

from os import listdir, remove, walk
from os import mkdir as makedir
from shutil import rmtree

@dataclass
class File:
    contents: bytes | bytearray
    fullpath: str
    #hash: bytes # Integrity hash


@dataclass
class CompressedFile:
    compressed_bytes: bytes | bytearray
    fullpath: str
    #hash: str | bytes # Integrity hash


def pre_write_run(dest: str, files: list[str]) -> bool:
    """ Creates all files before writing decompressed files to fs """
    mkdir(dest) # Make sure the dir that is being written to exists
    for file in files:
        try:
            with open(file, 'x') as f:
                pass
        except FileExistsError:
            pass
    return True

def read_in_chunks(file_object, chunk_size=1024):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def find_compressed_files(dest):
    """ Find all compressed extracted files in the given dest """
    _files = []
    for parent, subdirs, files in walk(dest):
        for file in files:
            _files.append(f"{parent}/{file}")
    return _files

def load_compressed_file(self, parent, files): # TODO: change to use read_file_binary
    compressed = []
    for file in files:
        with open(f"{parent}/{file}", 'rb') as f:
            contents = f.read()
            compressed.append(CompressedFile(contents, f"{parent}/{file}"))
            del contents
    return compressed


def write_to_temp(chunks: list[bytes], tempfile: str):
    """ Writes chunks to temp file for loading large files """
    with open(tempfile, "ab+") as f:
        for chunk in chunks: f.write(chunk)

def clear_tmp(dest: str):
    rmtree(dest) # Delete temp folder
    mkdir(dest) # Re-create it   
    
def write_file(file: File):
    with open(file.fullpath, 'w+') as f: # TODO: maybe add threading or use OS commands
        f.write(file.contents)

def bytes_write_files_from_list(files: list[CompressedFile]):
    for file in files: # Write all the files to FS
        with open(file.fullpath, 'wb') as f: # TODO: maybe add threading or use OS commands
            f.write(file.contents)

def bytes_write_file(file: File):
    with open(file.fullpath, 'wb') as f: # TODO: maybe add threading or use OS commands
        f.write(file.contents)

def read_file_bytes(file: str, chunked: bool = True):
    with open(file, 'rb') as f:
        if chunked:
            return read_in_chunks(f)
        return f.read()
    
def mkdir(name: str):
    makedir(name)

def rm(path: str):
    remove(path)