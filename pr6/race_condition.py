
import threading
import time

THREADS = 4
INCREMENTS = 100_000

counter = 0


def worker():
    global counter

    for i in range(INCREMENTS):
        value = counter

        # Encourage a context switch between reading and writing.
        if i % 100 == 0:
            time.sleep(0)

        counter = value + 1


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
    print("Потерянные увеличения:", expected - counter)


if __name__ == "__main__":
    main()
