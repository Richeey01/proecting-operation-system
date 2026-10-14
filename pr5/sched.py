
import argparse
import statistics
from collections import deque


def read_processes(filename):
    processes = []

    with open(filename) as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue

            pid, arrival, burst, priority = parts
            processes.append({
                "pid": pid,
                "arrival": int(arrival),
                "burst": int(burst),
                "priority": int(priority)
            })

    if any(p["arrival"] < 0 or p["burst"] <= 0
           for p in processes):
        raise ValueError("Arrival должен быть >= 0, burst > 0")

    if not processes:
        raise ValueError("Файл не содержит процессов")

    if len({p["pid"] for p in processes}) != len(processes):
        raise ValueError("PID должны быть уникальными")

    return sorted(processes, key=lambda p: p["arrival"])


def simulate(processes, algorithm, quantum=3,
             aging=False, aging_interval=5):
    jobs = {
        p["pid"]: {
            **p,
            "left": p["burst"],
            "first": None,
            "finish": None
        }
        for p in processes
    }

    ready = []
    rr_queue = deque()
    intervals = []

    time = 0
    running = None
    slice_used = 0
    pending_requeue = None

    def add_interval(pid, start, end):
        if start >= end:
            return

        if (intervals and intervals[-1][0] == pid
                and intervals[-1][2] == start):
            intervals[-1] = (pid, intervals[-1][1], end)
        else:
            intervals.append((pid, start, end))

    while any(p["left"] > 0 for p in jobs.values()):
        # Сначала добавляем прибывшие процессы
        for p in processes:
            if p["arrival"] == time:
                if algorithm == "rr":
                    rr_queue.append(p["pid"])
                else:
                    ready.append(p["pid"])

        # В RR новые процессы в момент окончания кванта
        # должны попасть в очередь раньше вытесненного
        if pending_requeue is not None:
            rr_queue.append(pending_requeue)
            pending_requeue = None

        # Выбираем процесс
        if algorithm == "rr":
            if running is None and rr_queue:
                running = rr_queue.popleft()
                slice_used = 0

        elif algorithm in ("fcfs", "sjf"):
            if running is None and ready:
                if algorithm == "fcfs":
                    running = ready.pop(0)
                else:
                    running = min(
                        ready, key=lambda pid: jobs[pid]["burst"]
                    )
                    ready.remove(running)

        else:
            candidates = ready[:]
            if running is not None:
                candidates.append(running)

            if candidates:
                if algorithm == "srtf":
                    chosen = min(
                        candidates,
                        key=lambda pid: (jobs[pid]["left"],
                                         jobs[pid]["arrival"])
                    )
                else:
                    def effective_priority(pid):
                        p = jobs[pid]
                        waited = time - p["arrival"] - (
                            p["burst"] - p["left"]
                        )
                        value = p["priority"]
                        if aging:
                            value -= waited // aging_interval
                        return (value, p["arrival"])

                    chosen = min(candidates, key=effective_priority)

                if chosen != running:
                    if running is not None:
                        ready.append(running)
                    ready.remove(chosen)
                    running = chosen

        # Если процесс ещё не пришёл или готовых нет
        if running is None:
            add_interval("IDLE", time, time + 1)
            time += 1
            continue

        p = jobs[running]

        if p["first"] is None:
            p["first"] = time

        add_interval(running, time, time + 1)
        p["left"] -= 1
        time += 1

        if algorithm == "rr":
            slice_used += 1

        if p["left"] == 0:
            p["finish"] = time
            running = None
            slice_used = 0
        elif algorithm == "rr" and slice_used == quantum:
            pending_requeue = running
            running = None
            slice_used = 0

    return intervals, jobs


def get_metrics(processes, intervals, jobs):
    waiting = []
    turnaround = []
    response = []

    for p in processes:
        result = jobs[p["pid"]]
        turn = result["finish"] - p["arrival"]

        turnaround.append(turn)
        waiting.append(turn - p["burst"])
        response.append(result["first"] - p["arrival"])

    start = min(p["arrival"] for p in processes)
    end = max(p["finish"] for p in jobs.values())
    busy = sum(
        finish - begin
        for pid, begin, finish in intervals
        if pid != "IDLE"
    )

    return {
        "waiting": statistics.mean(waiting),
        "turnaround": statistics.mean(turnaround),
        "response": statistics.mean(response),
        "cpu": busy / (end - start) * 100
    }


def print_result(processes, intervals, jobs):
    print("\nДиаграмма Ганта:")
    print(" | ".join(
        f"{pid}[{start}-{end}]"
        for pid, start, end in intervals
    ))

    metrics = get_metrics(processes, intervals, jobs)

    print("\nСреднее ожидание:", round(metrics["waiting"], 2))
    print("Средний оборот:", round(metrics["turnaround"], 2))
    print("Среднее время отклика:", round(metrics["response"], 2))
    print("Загрузка CPU:", round(metrics["cpu"], 2), "%")

    print("\nPID | Ожидание | Оборот | Отклик")
    for p in processes:
        result = jobs[p["pid"]]
        turn = result["finish"] - p["arrival"]
        wait = turn - p["burst"]
        response = result["first"] - p["arrival"]
        print(f"{p['pid']} | {wait} | {turn} | {response}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algo", required=True,
                        choices=["fcfs", "sjf", "srtf",
                                 "priority", "rr"])
    parser.add_argument("--quantum", type=int, default=3)
    parser.add_argument("--aging", action="store_true")
    parser.add_argument("--aging-interval", type=int, default=5)
    parser.add_argument("file")
    args = parser.parse_args()

    if args.quantum <= 0 or args.aging_interval <= 0:
        parser.error("quantum и aging-interval должны быть > 0")

    processes = read_processes(args.file)
    intervals, jobs = simulate(
        processes, args.algo, args.quantum,
        args.aging, args.aging_interval
    )

    print("Алгоритм:", args.algo.upper())
    if args.algo == "rr":
        print("Квант:", args.quantum)

    print_result(processes, intervals, jobs)


if __name__ == "__main__":
    main()
