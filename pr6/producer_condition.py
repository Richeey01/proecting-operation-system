
import threading

CAPACITY = 5
TOTAL_ITEMS = 1000
PRODUCERS = 3
CONSUMERS = 2

buffer = [None] * CAPACITY
count = 0
in_index = 0
out_index = 0

condition = threading.Condition()
consumed = []
violations = []


def put(item):
    global count, in_index

    with condition:
        while count == CAPACITY:
            condition.wait()

        if count >= CAPACITY:
            violations.append("Переполнение буфера")

        buffer[in_index] = item
        in_index = (in_index + 1) % CAPACITY
        count += 1

        condition.notify_all()


def get():
    global count, out_index

    with condition:
        while count == 0:
            condition.wait()

        if count <= 0:
            violations.append("Чтение из пустого буфера")

        item = buffer[out_index]
        buffer[out_index] = None
        out_index = (out_index + 1) % CAPACITY
        count -= 1

        condition.notify_all()
        return item


def producer(start, end):
    for item in range(start, end):
        put(item)


def consumer():
    while True:
        item = get()

        if item is None:
            break

        with condition:
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

    print("Вместимость буфера:", CAPACITY)
    print("Ожидалось элементов:", TOTAL_ITEMS)
    print("Обработано элементов:", len(consumed))
    print("Все элементы уникальны:", len(set(consumed)) == TOTAL_ITEMS)
    print("Потерь нет:", set(consumed) == set(range(TOTAL_ITEMS)))
    print("Нарушения:", violations)


if __name__ == "__main__":
    main()
