
import threading
import time

THREADS = 4
PHASES = 3

condition = threading.Condition()
waiting = 0
generation = 0


def barrier():
    global waiting, generation

    with condition:
        current_generation = generation
        waiting += 1

        if waiting == THREADS:
            waiting = 0
            generation += 1
            condition.notify_all()
        else:
            while current_generation == generation:
                condition.wait()


def worker(thread_id):
    for phase in range(1, PHASES + 1):
        print(f"Поток {thread_id}: завершил фазу {phase}")

        # Wait until all four threads finish this phase.
        barrier()

        print(f"Поток {thread_id}: прошёл барьер фазы {phase}")
        time.sleep(0.1)


def main():
    threads = [
        threading.Thread(target=worker, args=(i,))
        for i in range(1, THREADS + 1)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("Все потоки завершили 3 фазы.")


if __name__ == "__main__":
    main()
