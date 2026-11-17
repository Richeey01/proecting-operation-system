import random
import matplotlib.pyplot as plt

from tlb import TLB

random.seed(42)

PAGE_SIZE = 1024

# Все 16 страниц присутствуют
table = {page: page + 20 for page in range(16)}

# Генерируем 20000 обращений с локальностью
pages = []

for i in range(20000):
    # Рабочая область периодически меняется
    base = 0 if (i // 2000) % 2 == 0 else 8

    if random.random() < 0.9:
        page = base + random.randrange(4)
    else:
        page = random.randrange(16)

    pages.append(page)

addresses = [
    page * PAGE_SIZE + random.randrange(PAGE_SIZE)
    for page in pages
]

sizes = [1, 2, 4, 8, 16]
rates = []

for size in sizes:
    tlb = TLB(size)

    for addr in addresses:
        tlb.access(addr, table)

    rate = tlb.hit_rate()
    rates.append(rate)

    print(f"TLB={size:<2} Hit Rate={rate:.2%}")

plt.figure(figsize=(8, 5))
plt.plot(sizes, rates, marker="o")

plt.xlabel("Размер TLB (записей)")
plt.ylabel("Доля попаданий")
plt.title("Размер TLB и Hit Rate")
plt.xticks(sizes)
plt.ylim(0, 1)
plt.grid(True, alpha=0.3)

plt.savefig("tlb_hit_rate.png", dpi=150)
plt.show()