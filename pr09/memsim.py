MEMORY = 1024


class Block:
    def __init__(self, start, size, pid=None):
        self.start, self.size, self.pid = start, size, pid

    @property
    def free(self):
        return self.pid is None


class MemoryManager:
    def __init__(self, strategy="first", coalesce=False):
        self.blocks = [Block(0, MEMORY)]
        self.strategy = strategy
        self.coalesce = coalesce
        self.refused = 0

    def candidates(self, size):
        return [b for b in self.blocks if b.free and b.size >= size]

    def choose(self, size):
        c = self.candidates(size)
        if not c:
            return None
        if self.strategy == "first":
            return c[0]
        if self.strategy == "best":
            return min(c, key=lambda b: b.size)
        return max(c, key=lambda b: b.size)          # worst

    def alloc(self, pid, size):
        hole = self.choose(size)
        if hole is None:
            self.refused += 1
            return False
        i = self.blocks.index(hole)
        self.blocks[i] = Block(hole.start, size, pid)
        if hole.size > size:
            rest = Block(hole.start + size, hole.size - size)
            self.blocks.insert(i + 1, rest)
        return True

    def free(self, pid):
        for b in self.blocks:
            if b.pid == pid:
                b.pid = None
        if self.coalesce:
            self.merge()

    def merge(self):
        merged = [self.blocks[0]]
        for b in self.blocks[1:]:
            last = merged[-1]
            if last.free and b.free:
                last.size += b.size
            else:
                merged.append(b)
        self.blocks = merged

    def stats(self):
        holes = [b.size for b in self.blocks if b.free]
        return sum(holes), max(holes, default=0), len(holes)

    def show(self):
        parts = [f"[{b.pid or '-'}:{b.size}]" for b in self.blocks]
        return " ".join(parts)


def run(ops, strategy, coalesce=False, verbose=False):
    mm = MemoryManager(strategy, coalesce)
    for n, (cmd, pid, *rest) in enumerate(ops, 1):
        if cmd == "alloc":
            ok = mm.alloc(pid, rest[0])
            note = "" if ok else "  ← ОТКАЗ"
        else:
            mm.free(pid)
            note = ""
        if verbose:
            print(f"{n:>2} {cmd:<5} {pid:<3} {rest[0] if rest else '':>4}  {mm.show()}{note}")
    return mm


def load(path):
    ops = []
    for line in open(path):
        p = line.split()
        if p:
            ops.append((p[0], p[1], int(p[2])) if p[0] == "alloc" else (p[0], p[1]))
    return ops
