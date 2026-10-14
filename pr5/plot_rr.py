
import matplotlib.pyplot as plt
from sched import read_processes, simulate, get_metrics

processes = read_processes("set2.txt")

quanta = list(range(1, 11))
waiting = []
switches = []

print("Квант | Среднее ожидание | Переключения")

for q in quanta:
    intervals, jobs = simulate(processes, "rr", quantum=q)
    metrics = get_metrics(processes, intervals, jobs)

    # Считаем переходы между разными процессами
    count = 0
    previous = None

    for pid, start, end in intervals:
        if pid != "IDLE":
            if previous is not None and pid != previous:
                count += 1
            previous = pid

    waiting.append(metrics["waiting"])
    switches.append(count)

    print(q, "|", round(metrics["waiting"], 2), "|", count)

fig, ax1 = plt.subplots()

ax1.plot(quanta, waiting, marker="o", label="Ожидание")
ax1.set_xlabel("Квант времени")
ax1.set_ylabel("Среднее ожидание")

ax2 = ax1.twinx()
ax2.plot(quanta, switches, marker="s", label="Переключения")
ax2.set_ylabel("Количество переключений")

plt.title("Round Robin: влияние кванта")
fig.tight_layout()
plt.savefig("rr_graph.png")
plt.show()

print("График сохранён в rr_graph.png")
