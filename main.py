#!/usr/bin/env python3
"""Entry program for news-image-20261125.

Validates the bundled front-page image (entry.png) and copies it to
$MAKEFUN_OUTPUT_DIR/entry.png. Standard library only, no network,
deterministic: running it twice writes byte-identical output.
"""
import hashlib
import os
import struct
import sys
import zlib

EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1048576
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print("error: " + message, file=sys.stderr)
    raise SystemExit(1)


def validate_png(data):
    """Check the PNG is whole: signature, 1024x1024 IHDR, every chunk CRC."""
    if len(data) > MAX_BYTES:
        fail("entry.png is %d bytes, over the 1 MiB limit" % len(data))
    if len(data) < 8 or data[:8] != PNG_SIGNATURE:
        fail("entry.png is not a PNG file")
    pos = 8
    seen_ihdr = False
    seen_iend = False
    while pos < len(data):
        if pos + 8 > len(data):
            fail("truncated PNG chunk header")
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        chunk_type = data[pos + 4:pos + 8]
        end = pos + 12 + length
        if end > len(data):
            fail("truncated PNG chunk %r" % chunk_type)
        chunk_data = data[pos + 8:pos + 8 + length]
        stored_crc = struct.unpack(">I", data[pos + 8 + length:end])[0]
        actual_crc = zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            fail("bad CRC in PNG chunk %r" % chunk_type)
        if chunk_type == b"IHDR":
            if seen_ihdr:
                fail("duplicate IHDR chunk")
            if length != 13:
                fail("IHDR chunk has wrong length")
            width, height = struct.unpack(">II", chunk_data[:8])
            if width != EXPECTED_WIDTH or height != EXPECTED_HEIGHT:
                fail("entry.png is %dx%d, expected 1024x1024"
                     % (width, height))
            seen_ihdr = True
        if chunk_type == b"IEND":
            if end != len(data):
                fail("trailing data after IEND chunk")
            seen_iend = True
            break
        pos = end
    if not seen_ihdr:
        fail("PNG has no IHDR chunk")
    if not seen_iend:
        fail("PNG has no IEND chunk")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        fail("entry.png not found next to main.py")
    with open(source, "rb") as fh:
        data = fh.read()
    validate_png(data)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    # Write via a temp file in the same directory, then rename, so a
    # failed run can never leave a partial entry.png behind.
    tmp = dest + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, dest)
    with open(dest, "rb") as fh:
        written = fh.read()
    if hashlib.sha256(written).hexdigest() != hashlib.sha256(data).hexdigest():
        fail("output copy does not match entry.png")
    print("wrote %s (%d bytes, sha256 %s)"
          % (dest, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
