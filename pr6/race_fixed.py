
import threading

THREADS = 4
INCREMENTS = 100_000

counter = 0
lock = threading.Lock()


def worker():
    global counter

    for _ in range(INCREMENTS):
        with lock:
            counter += 1


def main():
    threads = [
        threading.Thread(target=worker)
        for _ in range(THREADS)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    expected = THREADS * INCREMENTS

    print("Ожидаемый результат:", expected)
    print("Фактический результат:", counter)
    print("Результат правильный:", counter == expected)


if __name__ == "__main__":
    main()
