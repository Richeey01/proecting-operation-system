
import time
import statistics
import urllib.request
from array import array
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from threading import Thread
from multiprocessing import Pool


# Читаем числа до начала замеров
with open("numbers.txt") as f:
    numbers = array("q", (int(x) for x in f))

print("Чисел:", len(numbers))


def sum_part(part):
    return sum(part)


def one_thread():
    return sum(numbers)


def four_threads():
    size = len(numbers) // 4
    results = [0] * 4

    def worker(i):
        start = i * size
        end = len(numbers) if i == 3 else (i + 1) * size
        results[i] = sum(numbers[start:end])

    threads = []
    for i in range(4):
        t = Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return sum(results)


def four_processes():
    size = len(numbers) // 4
    parts = []

    for i in range(4):
        start = i * size
        end = len(numbers) if i == 3 else (i + 1) * size
        parts.append(numbers[start:end])

    with Pool(4) as pool:
        results = pool.map(sum_part, parts)

    return sum(results)


def measure(name, func):
    times = []
    result = None

    for i in range(3):
        start = time.perf_counter()
        result = func()
        times.append(time.perf_counter() - start)

    median = statistics.median(times)
    print(f"{name}: сумма={result}, "
          f"время={times}, медиана={median:.3f} сек.")
    return median

def change_process(data):
    data[0] = 20


def download(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        return len(response.read())

if __name__ == "__main__":
    print("\n=== Сумма чисел ===")

    t1 = measure("Один поток", one_thread)
    t2 = measure("4 потока", four_threads)
    t3 = measure("4 процесса", four_processes)

    # Пример общей и раздельной памяти
    print("\n=== Память ===")
    shared = [0]

    def change_list():
        shared[0] = 10

    t = Thread(target=change_list)
    t.start()
    t.join()
    print("После потока:", shared)

    def change_process(data):
        data[0] = 20

    with Pool(1) as pool:
        pool.map(change_process, [shared])

    print("После процесса:", shared)

    # Создаём 20 небольших файлов для сетевого теста
    import os
    os.makedirs("net_files", exist_ok=True)

    for i in range(20):
        with open(f"net_files/file{i}.txt", "w") as f:
            f.write("Test file " + str(i))

    urls = [
        f"http://127.0.0.1:8000/net_files/file{i}.txt"
        for i in range(20)
    ]

    def download(url):
        with urllib.request.urlopen(url, timeout=10) as response:
            return len(response.read())

    def sequential():
        return [download(url) for url in urls]

    def threaded():
        with ThreadPoolExecutor(max_workers=4) as executor:
            return list(executor.map(download, urls))

    def processed():
        with ProcessPoolExecutor(max_workers=4) as executor:
            return list(executor.map(download, urls))

    print("\n=== Сетевые задачи ===")
    print("Сначала запусти локальный сервер в другом терминале.")

    # Эти замеры запускаются после старта сервера
    try:
        n1 = measure("Последовательно", sequential)
        n2 = measure("Потоки", threaded)
        n3 = measure("Процессы", processed)
    except Exception as e:
        print("Ошибка сети:", e)
        print("Проверь, запущен ли локальный сервер.")

    print("\n=== Итог ===")
    print("Ядра CPU:", os.cpu_count())
    print("Сумма одинакова:", one_thread() == four_threads()
          == four_processes())
