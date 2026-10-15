
from array import array
from multiprocessing import Process, Pipe, shared_memory
import time

N = 10_000_000
EXPECTED_SUM = N * (N - 1) // 2


def shared_memory_worker(name, connection):
    shm = shared_memory.SharedMemory(name=name)

    try:
        connection.recv()  # Ждём, пока родитель запишет массив.
        view = shm.buf.cast("Q")
        total = sum(view)
        result = (len(view), total)
        del view
        connection.send(result)
    finally:
        shm.close()
        connection.close()


def pipe_worker(connection):
    try:
        payload = connection.recv_bytes()
        view = memoryview(payload).cast("Q")
        result = (len(view), sum(view))
        del view
        connection.send(result)
    finally:
        connection.close()


def main():
    print(f"Количество чисел: {N:,}".replace(",", " "))
    print("Подготовка массива...")

    values = array("Q", range(N))
    payload = values.tobytes()
    size_mb = len(payload) / (1024 * 1024)

    print(f"Размер массива: {size_mb:.2f} MiB")

    # Вариант 1: разделяемая память
    shm = shared_memory.SharedMemory(create=True, size=len(payload))
    parent_conn, child_conn = Pipe()

    process = Process(
        target=shared_memory_worker,
        args=(shm.name, child_conn)
    )
    process.start()
    child_conn.close()

    try:
        start = time.perf_counter()
        shm.buf[:] = payload
        parent_conn.send("ready")
        count, total = parent_conn.recv()
        shm_time = time.perf_counter() - start

        print("\n--- Shared Memory ---")
        print(f"Получено чисел: {count}")
        print(f"Сумма правильная: {total == EXPECTED_SUM}")
        print(f"Время: {shm_time:.3f} сек")
    finally:
        parent_conn.close()
        process.join()
        shm.close()
        shm.unlink()

    # Вариант 2: передача массива через Pipe
    parent_conn, child_conn = Pipe()
    process = Process(target=pipe_worker, args=(child_conn,))
    process.start()
    child_conn.close()

    try:
        start = time.perf_counter()
        parent_conn.send_bytes(payload)
        count, total = parent_conn.recv()
        pipe_time = time.perf_counter() - start

        print("\n--- Pipe ---")
        print(f"Получено чисел: {count}")
        print(f"Сумма правильная: {total == EXPECTED_SUM}")
        print(f"Время: {pipe_time:.3f} сек")

        print("\n--- Сравнение ---")
        print(f"Shared Memory: {shm_time:.3f} сек")
        print(f"Pipe:          {pipe_time:.3f} сек")

        if shm_time < pipe_time:
            print("В этом запуске Shared Memory быстрее.")
        elif pipe_time < shm_time:
            print("В этом запуске Pipe быстрее.")
        else:
            print("Время практически одинаковое.")
    finally:
        parent_conn.close()
        process.join()


if __name__ == "__main__":
    main()
