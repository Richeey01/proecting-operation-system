
import os
import time

pid = os.fork()

if pid == 0:
    print(
        f"Ребёнок: PID={os.getpid()}, "
        f"первоначальный PPID={os.getppid()}",
        flush=True
    )

    time.sleep(10)

    print(
        f"После завершения родителя: "
        f"PID={os.getpid()}, новый PPID={os.getppid()}",
        flush=True
    )
    os._exit(0)

print(
    f"Родитель PID={os.getpid()} завершится сейчас. "
    f"PID ребёнка={pid}",
    flush=True
)
os._exit(0)
