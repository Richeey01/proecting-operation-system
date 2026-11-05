from memsim import MEMORY


class Buddy:
    def __init__(self, log=False):
        self.free = {MEMORY: [0]}   # размер → адреса свободных блоков
        self.owned = {}             # pid → (адрес, блок, запрошено)
        self.refused, self.log = 0, log

    def alloc(self, pid, size):
        need = 1
        while need < size:
            need *= 2
        s = need
        while s <= MEMORY and not self.free.get(s):
            s *= 2
        if s > MEMORY:
            self.refused += 1
            return False
        addr = self.free[s].pop(0)
        while s > need:             # делим пополам до нужного
            s //= 2
            self.free.setdefault(s, []).append(addr + s)
            if self.log: print(f"   делим → {s}+{s}")
        self.owned[pid] = (addr, need, size)
        return True

    def release(self, pid):
        if pid not in self.owned:   # alloc был отклонён
            return
        addr, s, _ = self.owned.pop(pid)
        while s < MEMORY:
            buddy = addr ^ s
            if buddy in self.free.get(s, []):
                self.free[s].remove(buddy)
                addr, s = min(addr, buddy), s * 2
                if self.log: print(f"   слияние → {s}")
            else:
                break
        self.free.setdefault(s, []).append(addr)
        self.free[s].sort()

    def stats(self):
        holes = [s for s, lst in self.free.items() for _ in lst]
        internal = sum(b - r for _, b, r in self.owned.values())
        return sum(holes), max(holes, default=0), internal
