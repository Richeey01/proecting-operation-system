import os, sys, errno

if len(sys.argv) < 2:
    print("Usage: safe_cat <path> [--chunk N]")
    sys.exit(1)

path = sys.argv[1]
chunk = 4096

if "--chunk" in sys.argv:
    try:
        chunk = int(sys.argv[sys.argv.index("--chunk") + 1])
    except:
        sys.exit(1)

total = count = 0

try:
    fd = os.open(path, os.O_RDONLY)

    while True:
        data = os.read(fd, chunk)
        if not data:
            break
        os.write(1, data)
        total += len(data)
        count += 1

    os.close(fd)

except OSError as e:
    print(f"Syscall error | errno={e.errno} "
          f"({errno.errorcode.get(e.errno)}) | {e.strerror}")

    if e.errno == errno.EACCES:
        print("Недостаточно прав")

    sys.exit(1)


print("\n--- stats ---", file=sys.stderr)
print(f"bytes read: {total}", file=sys.stderr)
print(f"read calls: {count}", file=sys.stderr)
