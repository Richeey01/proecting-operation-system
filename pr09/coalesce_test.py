from memsim import MemoryManager, load

ops = load("ops2.txt")

print(f"{'Стратегия':<20}{'Отказы':>10}{'Внешняя фр.':>16}")

for strategy in ["first", "best", "worst"]:
    for merge in [False, True]:
        mm = MemoryManager(strategy, coalesce=merge)
        fragmentation = []

        for cmd, pid, *rest in ops:
            if cmd == "alloc":
                mm.alloc(pid, rest[0])
            else:
                mm.free(pid)

            total, largest, _ = mm.stats()
            value = 1 - largest / total if total else 0
            fragmentation.append(value)

        name = strategy + (" + merge" if merge else " без merge")
        average = sum(fragmentation) / len(fragmentation)

        print(f"{name:<20}{mm.refused:>10}{average:>16.2f}")
