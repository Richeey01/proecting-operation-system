from memsim import load
from buddy import Buddy

ops = load("ops2.txt")
memory = Buddy(log=True)

for number, (cmd, pid, *rest) in enumerate(ops, 1):
    if cmd == "alloc":
        size = rest[0]
        print(f"\nОперация {number}: alloc {pid} {size}")
        success = memory.alloc(pid, size)
        if not success:
            print("ОТКАЗ")
    else:
        print(f"\nОперация {number}: free {pid}")
        memory.release(pid)

print("\nИтог:")
print("Отказов:", memory.refused)
print("Свободная память:", memory.stats()[0])
print("Внутренняя фрагментация:", memory.stats()[2])
