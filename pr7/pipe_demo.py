
from multiprocessing import Process, Pipe


def receiver(connection):
    try:
        numbers = connection.recv()
        print("Получено от родителя:", numbers)
        print("Сумма:", sum(numbers))
    finally:
        connection.close()


def main():
    parent_conn, child_conn = Pipe()

    process = Process(target=receiver, args=(child_conn,))
    process.start()
    child_conn.close()

    parent_conn.send([10, 20, 30, 40, 50])
    parent_conn.close()

    process.join()


if __name__ == "__main__":
    main()
