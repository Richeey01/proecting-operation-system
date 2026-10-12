
import os
import sys
import time


def main():
    if len(sys.argv) < 3:
        print("Использование: python3 runner.py N команда [аргументы]")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        if n < 1:
            raise ValueError
    except ValueError:
        print("Ошибка: N должно быть положительным целым числом")
        sys.exit(1)

    command = sys.argv[2:]
    children = {}

    for i in range(n):
        start_time = time.monotonic()
        pid = os.fork()

        if pid == 0:
            try:
                os.execvp(command[0], command)
            except OSError as error:
                print(f"Не удалось запустить команду: {error}", file=sys.stderr)
                os._exit(127)

        children[pid] = (i + 1, start_time)

    remaining = set(children)

    while remaining:
        try:
            pid, status = os.waitpid(-1, 0)
        except InterruptedError:
            continue

        if pid not in remaining:
            continue

        remaining.remove(pid)
        number, start_time = children[pid]
        elapsed = time.monotonic() - start_time

        if os.WIFEXITED(status):
            code = os.WEXITSTATUS(status)
            print(
                f"Ребёнок {number}: PID={pid}, "
                f"код возврата={code}, время={elapsed:.2f} сек."
            )
        elif os.WIFSIGNALED(status):
            sig = os.WTERMSIG(status)
            print(
                f"Ребёнок {number}: PID={pid}, "
                f"завершён сигналом {sig}, время={elapsed:.2f} сек."
            )


if __name__ == "__main__":
    main()
