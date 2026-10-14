
import threading

CAPACITY = 5
TOTAL_ITEMS = 1000
PRODUCERS = 3
CONSUMERS = 2

buffer = [None] * CAPACITY
in_index = 0
out_index = 0

empty_slots = threading.Semaphore(CAPACITY)
filled_slots = threading.Semaphore(0)
mutex = threading.Lock()

consumed = []
consumed_lock = threading.Lock()


def put(item):
    global in_index

    empty_slots.acquire()
    with mutex:
        buffer[in_index] = item
        in_index = (in_index + 1) % CAPACITY
    filled_slots.release()


def get():
    global out_index

    filled_slots.acquire()
    with mutex:
        item = buffer[out_index]
        buffer[out_index] = None
        out_index = (out_index + 1) % CAPACITY
    empty_slots.release()
    return item


def producer(start, end):
    for item in range(start, end):
        put(item)


def consumer():
    while True:
        item = get()

        if item is None:
            break

        with consumed_lock:
            consumed.append(item)


def main():
    consumers = [
        threading.Thread(target=consumer)
        for _ in range(CONSUMERS)
    ]

    for thread in consumers:
        thread.start()

    producers = []
    for i in range(PRODUCERS):
        start = i * TOTAL_ITEMS // PRODUCERS
        end = (i + 1) * TOTAL_ITEMS // PRODUCERS

        thread = threading.Thread(
            target=producer,
            args=(start, end)
        )
        producers.append(thread)
        thread.start()

    for thread in producers:
        thread.join()

    # Send a stop signal to each consumer.
    for _ in range(CONSUMERS):
        put(None)

    for thread in consumers:
        thread.join()

    print("Производителей:", PRODUCERS)
    print("Потребителей:", CONSUMERS)
    print("Вместимость буфера:", CAPACITY)
    print("Ожидалось элементов:", TOTAL_ITEMS)
    print("Обработано элементов:", len(consumed))
    print("Все элементы уникальны:", len(set(consumed)) == TOTAL_ITEMS)
    print("Потерь нет:", set(consumed) == set(range(TOTAL_ITEMS)))


if __name__ == "__main__":
    main()

