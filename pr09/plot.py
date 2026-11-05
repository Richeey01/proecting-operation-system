import matplotlib.pyplot as plt
from memsim import MemoryManager, load
from buddy import Buddy

ops = load("ops2.txt")

names = [
    "First Fit + Merge",
    "Best Fit + Merge",
    "Worst Fit + Merge",
    "Buddy System"
]

refusals = []
external = []
internal = []

# Три обычные стратегии
for strategy in ["first", "best", "worst"]:
    mm = MemoryManager(strategy, coalesce=True)
    ext_values = []

    for cmd, pid, *rest in ops:
        if cmd == "alloc":
            mm.alloc(pid, rest[0])
        else:
            mm.free(pid)

        total, largest, _ = mm.stats()
        ext_values.append(1 - largest / total if total else 0)

    refusals.append(mm.refused)
    external.append(sum(ext_values) / len(ext_values))
    internal.append(0)

# Buddy System
mm = Buddy()
ext_values = []
int_values = []

for cmd, pid, *rest in ops:
    if cmd == "alloc":
        mm.alloc(pid, rest[0])
    else:
        mm.release(pid)

    total, largest, waste = mm.stats()
    ext_values.append(1 - largest / total if total else 0)
    int_values.append(waste)

refusals.append(mm.refused)
external.append(sum(ext_values) / len(ext_values))
internal.append(sum(int_values) / len(int_values))

# График отказов
plt.figure(figsize=(9, 5))
plt.bar(names, refusals)
plt.title("Количество отказов при распределении памяти")
plt.ylabel("Количество отказов")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("refusals.png")
plt.close()

# График внешней фрагментации
plt.figure(figsize=(9, 5))
plt.bar(names, external)
plt.title("Средняя внешняя фрагментация")
plt.ylabel("Коэффициент фрагментации")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("external_fragmentation.png")
plt.close()

# График внутренней фрагментации
plt.figure(figsize=(9, 5))
plt.bar(names, internal)
plt.title("Средняя внутренняя фрагментация")
plt.ylabel("Количество неиспользуемой памяти")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("internal_fragmentation.png")
plt.close()

print("Графики успешно созданы!")
