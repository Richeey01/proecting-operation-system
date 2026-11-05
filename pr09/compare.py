from memsim import MemoryManager, load
from buddy import Buddy

ops = load("ops2.txt")


def simulate(make, alloc, free, stats):
    m, ext, internal = make(), [], []
    for cmd, pid, *rest in ops:
        alloc(m, pid, rest[0]) if cmd == "alloc" else free(m, pid)
        tot, mx, extra = stats(m)
        ext.append(1 - mx / tot if tot else 0)   # доля свободной памяти вне самой большой дыры
        internal.append(extra)
    return m.refused, sum(ext) / len(ext), sum(internal) / len(internal)


print(f"{'подход':<16}{'отказов':>8}{'внешняя фр.':>13}{'внутренняя':>12}")
for strategy in ["first", "best", "worst"]:
    r, e, i = simulate(lambda: MemoryManager(strategy, coalesce=True),
                       MemoryManager.alloc, MemoryManager.free,
                       lambda m: (*m.stats()[:2], 0))
    print(f"{strategy + ' +merge':<16}{r:>8}{e:>13.2f}{i:>12.0f}")
r, e, i = simulate(Buddy, Buddy.alloc, Buddy.release, Buddy.stats)
print(f"{'buddy':<16}{r:>8}{e:>13.2f}{i:>12.0f}")
