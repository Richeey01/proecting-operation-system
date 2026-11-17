import os
import sys
import mmap
import ctypes
import struct
import subprocess

FILE = "shared_data.bin"
SIZE = os.sysconf("SC_PAGE_SIZE")


def get_pfn(addr):
    offset = (addr // SIZE) * 8

    try:
        with open("/proc/self/pagemap", "rb") as f:
            f.seek(offset)
            entry = struct.unpack("Q", f.read(8))[0]

        if not entry & (1 << 63):
            return "not present"

        pfn = entry & ((1 << 55) - 1)

        return str(pfn) if pfn else "hidden"

    except (PermissionError, OSError):
        return "unavailable"


def worker():
    with open(FILE, "r+b") as f:
        with mmap.mmap(
            f.fileno(),
            SIZE,
            access=mmap.ACCESS_WRITE
        ) as memory:

            addr = ctypes.addressof(
                ctypes.c_char.from_buffer(memory)
            )

            # Обращаемся к странице
            value = memory[0]

            print(
                f"PID={os.getpid()} "
                f"VA={hex(addr)} "
                f"PFN={get_pfn(addr)} "
                f"value={value}"
            )


def main():
    with open(FILE, "wb") as f:
        f.write(b"A" * SIZE)

    commands = [
        [sys.executable, os.path.abspath(__file__), "worker"]
        for _ in range(2)
    ]

    processes = [
        subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        for command in commands
    ]

    for process in processes:
        output, error = process.communicate()
        print(output.strip())

        if error:
            print(error.strip())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        worker()
    else:
        main()