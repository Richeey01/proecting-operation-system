
import os

PROC = "/proc"
processes = {}


def read_process(pid):
    try:
        with open(f"{PROC}/{pid}/status", "r") as file:
            status = file.readlines()

        data = {}

        for line in status:
            if line.startswith("Name:"):
                data["name"] = line.split(":", 1)[1].strip()
            elif line.startswith("State:"):
                data["state"] = line.split(":", 1)[1].strip().split()[0]
            elif line.startswith("Pid:"):
                data["pid"] = int(line.split(":", 1)[1].strip())
            elif line.startswith("PPid:"):
                data["ppid"] = int(line.split(":", 1)[1].strip())
            elif line.startswith("Uid:"):
                data["uid"] = int(line.split()[1])
            elif line.startswith("VmRSS:"):
                data["rss"] = int(line.split()[1])

        data.setdefault("rss", 0)
        data["rss"] = data["rss"] // 1024

        if data.get("uid") != os.getuid():
            return None

        return data

    except (FileNotFoundError, PermissionError, ProcessLookupError, ValueError):
        return None


for entry in os.listdir(PROC):
    if entry.isdigit():
        process = read_process(entry)

        if process:
            processes[process["pid"]] = process

children = {}

for pid, process in processes.items():
    ppid = process["ppid"]
    children.setdefault(ppid, []).append(pid)

for pids in children.values():
    pids.sort()


def print_tree(pid, indent=0):
    process = processes[pid]

    print(
        "  " * indent
        + f'{pid} [{process["state"]}] '
        + f'RSS={process["rss"]} MB '
        + f'{process["name"]}'
    )

    for child_pid in children.get(pid, []):
        print_tree(child_pid, indent + 1)


roots = [
    pid for pid, process in processes.items()
    if process["ppid"] not in processes
]

for pid in sorted(roots):
    print_tree(pid)


