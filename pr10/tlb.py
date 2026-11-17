from collections import OrderedDict

from translate import (
    PAGE_SIZE,
    BASE_DIR,
    load_page_table
)


class TLB:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("Размер TLB должен быть >= 1")

        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.faults = 0

    def access(self, addr, table):
        page = addr // PAGE_SIZE
        offset = addr % PAGE_SIZE

        if page in self.cache:
            self.hits += 1

            frame = self.cache[page]
            self.cache.move_to_end(page)

            return "HIT", frame * PAGE_SIZE + offset

        self.misses += 1

        frame = table.get(page)

        if frame is None:
            self.faults += 1
            return "MISS / PAGE FAULT", None

        if len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)

        self.cache[page] = frame

        return "MISS", frame * PAGE_SIZE + offset

    def hit_rate(self):
        # Не считаем обращения к отсутствующим страницам
        valid = self.hits + self.misses - self.faults

        return self.hits / valid if valid else 0


def eat(hit_rate, memory_ns=100, tlb_ns=10):
    hit_time = tlb_ns + memory_ns
    miss_time = tlb_ns + 2 * memory_ns

    return (
        hit_rate * hit_time
        + (1 - hit_rate) * miss_time
    )


def main():
    table = load_page_table()

    with open(BASE_DIR / "refs.txt", encoding="utf-8") as file:
        addresses = [
            int(line.strip())
            for line in file
            if line.strip()
        ]

    tlb = TLB(capacity=2)

    for addr in addresses:
        result, physical = tlb.access(addr, table)

        print(
            f"addr={addr:<5} "
            f"{result:<18} physical={physical}"
        )

    print("\nСтатистика:")
    print("HIT:", tlb.hits)
    print("MISS:", tlb.misses)
    print("PAGE FAULT:", tlb.faults)

    h = tlb.hit_rate()

    print(f"Hit Rate: {h:.2%}")

    print("\nЭффективное время доступа:")

    for rate in [0.0, 0.25, 0.5, 0.75, 0.9, 1.0]:
        print(
            f"Hit Rate={rate:.0%} "
            f"-> EAT={eat(rate):.1f} нс"
        )

    print(f"\nEAT по refs.txt: {eat(h):.1f} нс")


if __name__ == "__main__":
    main()