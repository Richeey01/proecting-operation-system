import random
random.seed(42)
live, ops, n = [], [], 0
while len(ops) < 200:
    if live and random.random() < 0.45:
        pid = random.choice(live); live.remove(pid)
        ops.append(f"free {pid}")
    else:
        n += 1; pid = f"P{n}"; live.append(pid)
        size = random.choice([random.randint(8, 40), random.randint(40, 120), random.randint(120, 300)])
        ops.append(f"alloc {pid} {size}")
open("ops2.txt", "w").write("\n".join(ops) + "\n")
print(len(ops), "операций,", n, "процессов")
