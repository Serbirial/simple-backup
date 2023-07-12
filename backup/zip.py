#from hashlib import md5
import zipfile
from os import walk, remove
from os.path import basename
from sys import getsizeof, path

from . import io, compression, addons


class Zip: # Object for easy handling
    def __init__(self, name: str, directory: str, temp_path: str, addons: list, dest: str = "~/simple-backup", compression_level: int = 1, read_mode: bool = False):
        if compression_level > 9 or compression_level < 1:
            raise Exception("Invalid compression level")
            exit(0)

        self.directory = directory # Parent directory to be compressing

        self.compression_level = compression_level

        self.temp_path = temp_path
        self.dest = dest # Dest location

        if read_mode:
            self.create_zip(name, True)

        else:
            self.create_zip(name, False)
        self.name = name

        self.funcs = {
            "compress": self._compress,
            "decompress": self._decompress
        }

        self.load_addons(addons)


    def load_addons(self, to_load):
        if len(to_load) != 0:
            imports = { # TODO: review how to do this without casting
                "directory": f"{self.directory}",
                "compression_level": int(f"{self.compression_level}"),
                "temp_path": f"{self.temp_path}",
                "dest": f"{self.dest}",
                "name": f"{self.name}"
                }
            addons.load(to_load, imports)
            for addon in addons.get_addons():
                for name, _callable in addon.to_replace.items():
                    self.funcs[name] = _callable



    def create_zip(self, name, reading):
        path = f"{self.dest}/{name}.zip"
        try:
            if reading:
                self.zf = zipfile.ZipFile(path, "r")
            else:
                self.zf = zipfile.ZipFile(path, "x", compression=zipfile.ZIP_STORED)
        except FileNotFoundError:
            raise FileNotFoundError("Given destination directory does not exist.")
        except FileExistsError:
            print(f"Removing existing backup ({path})")
            remove(path)
            self.create_zip(name, False)

    # Loading / Etc #

    def unzip(self):
        """ Unzips Backup. """
        self.zf.extractall(self.temp_path)
        print("Extracted")

    # Decompressing #

    def integrity_check(self, decompressed_files: list[io.File]):
        """ Checks integrity """
        pass
        #errors = []
        #for ucfile, dcfile in self.uncompressed_files, decompressed_files:
        #    if not compare_digest(ucfile.hash, dcfile.hash):
        #        errors.append((ucfile, dcfile))
        #if len(errors) == 0:
        #    return True
        #else:
        #    return False, errors

    def _decompress(self):
        """ Decompress all files in `self.compressed_files`"""
        io.clear_tmp(self.temp_path)
        self.unzip()
        to_decomp = io.find_compressed_files(self.temp_path)


        for file in to_decomp: # Decompress and write all the files to fs
            decompressed = io.File(contents=compression.chunked_decompression(io.read_in_chunks(open(file, "rb"), 104857600)), fullpath=f"{self.temp_path}/{file}")

            filename = basename(file)

            decompressed_parent = decompressed.fullpath.split(self.temp_path)[2].split(filename)[0]
            if decompressed_parent.startswith("/"):
                decompressed_parent = f"{self.dest}/restored/{self.name}/{decompressed_parent.split('/', 1)[1]}"
            io.mkdir(decompressed_parent)


            # {self.dest}/{self.name}
            decompressed_path = f"{decompressed_parent}{filename}"
            # This needs to be the location the decompressed file is written to

            decompressed.fullpath = decompressed_path # TODO: improve this
            io.bytes_write_file(decompressed)
        io.clear_tmp(self.temp_path)
        return True, len(to_decomp)

    def decompress(self):
        return self.funcs["decompress"]()


    # Compressing #

    def _check_chunks_size(self, chunks: list[bytes]):
        total = 0
        for byteschunk in chunks:
            total += getsizeof(byteschunk)
        return round(total / 1024 / 1024)


    def _compress(self, parent: str, files: list):
        total = 0
        for file in files: # TODO: figure out way of loading massive files into ram and not shitting the bed
                            # I think i have figured it out with chunking, temp files and part files
            # Load the file in chunks
            tempfile = None
            chunks = []
            interation = 0
            fullpath = f"{parent}/{file}"
            warned = False
            with open(fullpath, 'rb') as f:
                for chunk in io.read_in_chunks(f, 52428800): # 50mb chunks
                    chunks.append(chunk)
                    if interation >= 4: # After 4 chunks, check mem usage
                        interation = 0
                        mem = self._check_chunks_size(chunks)
                        if mem >= 650: # If mem usage exceeds a normal ammount, start writing to a tmp file and clear the chunks
                            if not tempfile:
                                tempfile = f"{self.temp_path}/{file}.tmp"
                            if not warned:
                                print(f"File too large to load into memory, writing to tmp file. ({mem}Mb, {len(chunks)} chunks)")
                                warned = True
                            io.write_to_temp(chunks, tempfile)
                            chunks.clear()
                    else:
                        interation += 1

                if tempfile:
                    if len(chunks) != 0:
                        print(f"Writing {len(chunks)} remaining chunks to tmp...")
                        io.write_to_temp(chunks, tempfile) # Write left over chunks
                    del chunks # Free up memory
                    self.write_tmp_to_zip(fullpath ,tempfile)
                    io.clear_tmp(self.temp_path) # Clear temp folder for next large file
                else:
                    data = compression.compress_raw_chunks(chunks, self.compression_level)
                    del chunks
                    # Write to fs
                    self.insert_to_zip(io.CompressedFile(data, fullpath))
                    del data
            total += 1
        return total


    def compress(self):
        total = 0
        for parent, subdirs, files in walk(self.directory):
            total += self.funcs["compress"](parent, files)

        io.clear_tmp(self.temp_path)
        return True, total


    def insert_to_zip(self, file: io.CompressedFile):
        """ Writes a file to the zip """
        path = file.fullpath.split(self.directory, 1)[1].replace("\\", "/") # BUG: windows being stupid
        if path.startswith("/"):
            path = path.split("/", 1)[1] # Remove leading /
        self.zf.writestr(path, data=file.compressed_bytes, compresslevel=None)
        return True


    def write_tmp_to_zip(self, fullpath, tmpfile):
        """ Writes a tmp file to the zip """
        # TODO: move compression code to another function
        chunks = []
        part_files = []
        print("Loading tmp file...")
        with open(tmpfile, 'r') as f:
            has_started_splitting = False
            for chunk in io.read_in_chunks(f, 104857600): # 100mb chunks
                chunks.append(chunk)
                mem = self._check_chunks_size(chunks)
                if mem >= 400: # 400mb, allowing for the inevitable overhead with pythons pre-allocation and how big the file is when its written.
                    if not has_started_splitting:
                        print(f"Splitting tmp file into parts...")
                        has_started_splitting = True
                        continue
                    current_part = f"{self.temp_path}/part{len(part_files)+1}"
                    with open(current_part, "a+") as p:
                        # BUG: opening in write and joining the chunks uses too much memory
                        #p.write(''.join([chunk for chunk in chunks]))
                        for chunk in chunks:
                            p.write(chunk)
                        chunks.clear() # Free up the memory
                        part_files.append(current_part)
        del mem
        io.rm(tmpfile)
        main = open(tmpfile, "ab+")
        main.seek(0,0)
        main.truncate()
        comp = compression.create_compression_stream()
        if len(part_files) > 0: # File was too big to load into memory, so it was put into parts
            if len(chunks) > 0:
                # Put any remaining data into the last part file
                print(f"Adding {len(chunks)} remaining chunks to new part file")
                current_part = f"{self.temp_path}/part{len(part_files)+1}"
                with open(current_part, "a+") as lt:
                    for chunk in chunks:
                        lt.write(chunk)
                del chunks # Free up memory
                part_files.append(current_part)

            print("Writing part files to tmp (may take a while for compression)")
            for partfile in part_files:
                with open(partfile, "rb") as p: # Compress and write part files to main tmp
                    for chunk in io.read_in_chunks(p, 104857600*2): # 200mb chunks
                        compressed = comp.compress(chunk)
                        main.write(compressed) # TODO: review a better way of doing this
                        del compressed
                    p.close()
                io.rm(partfile)

            print("Successfully wrote part files to tmp")

        elif len(part_files) == 0: # This should not happen, but it can (maybe, idk)
            print("There are no part files, this shouldnt happen. To be put in a tmp a file has to be over 750mb, yet the received file is under 450/500mb.")

        main.write(comp.flush())
        main.close()
        print("Writing temp file to zip...")
        path = fullpath.split(self.name, 1)[1].replace("\\", "/") # BUG: windows being stupid
        self.zf.write(tmpfile, path, compresslevel=None)
        return True
