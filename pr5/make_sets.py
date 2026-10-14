
import random

random.seed(42)

# Набор 2: процессы с большими burst
with open("set2.txt", "w") as f:
    for i in range(20):
        pid = f"P{i + 1}"
        arrival = i * 2
        burst = random.randint(15, 50)
        priority = random.randint(1, 5)
        f.write(f"{pid} {arrival} {burst} {priority}\n")

# Набор 3: короткие процессы и один длинный
with open("set3.txt", "w") as f:
    f.write("P1 0 100 3\n")

    for i in range(19):
        pid = f"P{i + 2}"
        arrival = i + 1
        burst = random.randint(1, 5)
        priority = random.randint(1, 5)
        f.write(f"{pid} {arrival} {burst} {priority}\n")

print("Наборы set2.txt и set3.txt созданы")
