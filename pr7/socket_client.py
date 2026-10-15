
import json
import socket

SOCKET_PATH = "/tmp/pr7_calculator.sock"


def main():
    expression = input("Введите выражение (например, 2 + 3 * 4): ")

    request = {"expression": expression}

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(SOCKET_PATH)
            client.sendall(
                (json.dumps(request) + "\n").encode("utf-8")
            )

            reader = client.makefile("r", encoding="utf-8")
            response = json.loads(reader.readline())

        if "result" in response:
            print("Ответ сервера:", response["result"])
        else:
            print("Ошибка:", response.get("error", "Неизвестная ошибка"))

    except FileNotFoundError:
        print("Сервер не запущен: сначала запусти socket_server.py")
    except ConnectionRefusedError:
        print("Сервер не принимает соединения.")
    except OSError as error:
        print("Ошибка IPC:", error)


if __name__ == "__main__":
    main()
