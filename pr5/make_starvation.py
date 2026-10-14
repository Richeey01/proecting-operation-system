with open("starvation.txt", "w") as f:
    f.write("P1 0 20 10\n")

    for i in range(30):
        f.write(f"P{i + 2} {i + 1} 5 1\n")

print("Набор starvation.txt создан")
