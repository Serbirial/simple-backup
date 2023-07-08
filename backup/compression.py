import zlib

from . import io

def create_compression_stream(level: int = 9, mem_level: int = 6):
    return zlib.compressobj(level=level, memLevel=mem_level) # TODO: add config for this

def chunked_decompression(chunk_generator):
    _bytes = []
    temp = zlib.decompressobj()
    for chunk in chunk_generator:
        _bytes.append(temp.decompress(chunk))
    temp.flush()
    decompressed = b''.join([chunk for chunk in _bytes])
    return decompressed

def decompress(file: io.CompressedFile):
    temp = zlib.decompress(file.compressed_bytes) # TODO: use decompressobj for streaming
    return io.File(temp, file.fullpath)

def compress_raw_chunks(chunks: list[bytes], compression_level: int = 1):
    return zlib.compress(b''.join([chunk for chunk in chunks]), compression_level)
