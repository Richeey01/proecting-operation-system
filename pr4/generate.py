import random

random.seed(42)

with open("numbers.txt", "w") as f:
    for i in range(10_000_000):
        f.write(str(random.randint(1, 100)) + "\n")

print("Файл numbers.txt создан")
