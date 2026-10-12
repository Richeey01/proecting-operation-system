
import os
import time


def get_rss_mb():
    with open("/proc/self/status", "r") as file:
        for line in file:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return 0


print("Создаём большой список...", flush=True)

data = [0] * 5_000_000

print(f"RSS родителя до fork: {get_rss_mb():.1f} MB", flush=True)

pid = os.fork()

if pid == 0:
    print(f"PID ребёнка: {os.getpid()}", flush=True)
    print(f"RSS ребёнка до изменения: {get_rss_mb():.1f} MB", flush=True)

    for i in range(len(data)):
        data[i] = i + 1

    print(f"RSS ребёнка после изменения: {get_rss_mb():.1f} MB", flush=True)
    os._exit(0)

os.waitpid(pid, 0)
print("Ребёнок завершён.", flush=True)
