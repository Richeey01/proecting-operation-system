#!/usr/bin/env python3
"""Генератор исходных данных для ПР-2: каталог data/ с 50 журналами.
Запуск: python3 gen_logs.py (результат детерминирован, seed=2026)"""
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 2026
N_FILES = 50
START = datetime(2026, 2, 1)
EMPTY_FILE = 25       # намеренно пустой журнал (граничный случай)
NO_ERROR_FILE = 8     # журнал без единой строки ERROR
INCIDENT_FILE = 17    # день инцидента: всплеск ошибок module=db

LEVELS = ["INFO", "DEBUG", "WARN", "ERROR"]
LEVEL_W = [60, 15, 17, 8]
MODULES = ["net", "db", "auth", "disk", "sched", "cache", "api", "fs"]
MOD_W = {
    "INFO":  [15, 15, 15, 10, 10, 10, 15, 10],
    "DEBUG": [10, 10, 10, 10, 20, 20, 10, 10],
    "WARN":  [20, 15, 10, 20, 5, 15, 10, 5],
    "ERROR": [30, 25, 12, 15, 3, 5, 7, 3],
}
MSG = {
    "INFO": ["service started", "request completed", "user logged in",
             "cache warmed up", "config reloaded", "job scheduled"],
    "DEBUG": ["entering handler", "queue length checked", "retry counter reset",
              "buffer flushed", "heartbeat sent"],
    "WARN": ["slow response", "retrying request", "disk usage above 80%",
             "deprecated option used", "token expires soon"],
    "ERROR": ["connection timeout", "connection refused", "query failed",
              "permission denied", "no space left on device", "invalid token",
              "segment read failed"],
}


def line(rng, ts, level, module=None):
    if module is None:
        module = rng.choices(MODULES, MOD_W[level])[0]
    return f'{ts:%Y-%m-%d %H:%M:%S} {level} module={module} msg="{rng.choice(MSG[level])}"'


def main():
    rng = random.Random(SEED)
    out = Path("data")
    out.mkdir(exist_ok=True)
    for i in range(1, N_FILES + 1):
        path = out / f"{i:02d}.log"
        if i == EMPTY_FILE:
            path.write_text("")
            continue
        day = START + timedelta(days=i - 1)
        n = rng.randint(200, 900)
        secs = rng.sample(range(86400), n)
        burst = set()
        if i == INCIDENT_FILE:
            taken = set(secs)
            burst = set(rng.sample([x for x in range(50400, 54000) if x not in taken], 120))
            secs += list(burst)
        secs.sort()
        rows = []
        for s in secs:
            ts = day + timedelta(seconds=s)
            lvl = rng.choices(LEVELS, LEVEL_W)[0]
            if i == NO_ERROR_FILE and lvl == "ERROR":
                lvl = "WARN"
            if s in burst:
                rows.append(line(rng, ts, "ERROR", "db"))
                continue
            rows.append(line(rng, ts, lvl))
        path.write_text("\n".join(rows) + "\n")


if __name__ == "__main__":
    main()

