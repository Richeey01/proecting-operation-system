
import json
import os
import socket
import multiprocessing

from calc_utils import calculate

SOCKET_PATH = "/tmp/pr7_calculator.sock"


def handle_client(conn):
    try:
        with conn:
            reader = conn.makefile("r", encoding="utf-8")
            line = reader.readline()

            if not line:
                return

            try:
                request = json.loads(line)
                expression = request["expression"]
                result = calculate(expression)
                response = {"result": result}
            except Exception as error:
                response = {"error": str(error)}

            conn.sendall(
                (json.dumps(response) + "\n").encode("utf-8")
            )
            print(
                f"Клиент PID={os.getpid()}: {response}",
                flush=True
            )
    except (BrokenPipeError, ConnectionResetError, OSError) as error:
        print(f"Ошибка соединения: {error}", flush=True)


def main():
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        server.bind(SOCKET_PATH)
        server.listen(10)
        print(f"Unix-сервер запущен: {SOCKET_PATH}")
        print("Остановка: Ctrl+C")

        while True:
            conn, _ = server.accept()

            process = multiprocessing.Process(
                target=handle_client,
                args=(conn,)
            )
            process.start()
            conn.close()

    except KeyboardInterrupt:
        print("\nСервер останавливается")
    finally:
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
        print("Unix-сокет удалён")


if __name__ == "__main__":
    main()
