
import json
import os

REQUEST_FIFO = "/tmp/pr7_request.fifo"


def main():
    expression = input("Введите выражение (например, 2 + 3 * 4): ")
    response_fifo = f"/tmp/pr7_response_{os.getpid()}.fifo"

    try:
        os.mkfifo(response_fifo)

        request = {
            "expression": expression,
            "response_fifo": response_fifo,
        }

        with open(REQUEST_FIFO, "w") as request_file:
            request_file.write(json.dumps(request) + "\n")

        with open(response_fifo, "r") as response_file:
            response = json.loads(response_file.readline())

        if "result" in response:
            print("Ответ сервера:", response["result"])
        else:
            print("Ошибка:", response.get("error", "Неизвестная ошибка"))

    except FileNotFoundError:
        print("Не найден FIFO. Убедись, что сервер запущен.")
    except OSError as error:
        print("Ошибка IPC:", error)
    finally:
        if os.path.exists(response_fifo):
            os.unlink(response_fifo)


if __name__ == "__main__":
    main()
