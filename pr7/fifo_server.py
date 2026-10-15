
import json
import os

from calc_utils import calculate

REQUEST_FIFO = "/tmp/pr7_request.fifo"


def handle_request(line):
    try:
        request = json.loads(line)
        expression = request["expression"]
        response_fifo = request["response_fifo"]

        # Разрешаем ответы только в именованные каналы нашего клиента.
        if not (
            isinstance(response_fifo, str)
            and response_fifo.startswith("/tmp/pr7_response_")
            and os.path.basename(response_fifo) == response_fifo[5:]
        ):
            raise ValueError("Недопустимый путь ответа")

        try:
            result = calculate(expression)
            response = {"result": result}
        except Exception as error:
            response = {"error": str(error)}

        with open(response_fifo, "w") as response_file:
            response_file.write(json.dumps(response) + "\n")

        print(f"Запрос: {expression} -> {response}", flush=True)

    except Exception as error:
        print(f"Ошибка запроса: {error}", flush=True)


def main():
    if os.path.exists(REQUEST_FIFO):
        if not os.path.exists(REQUEST_FIFO) or not os.stat(REQUEST_FIFO).st_mode & 0o170000 == 0o010000:
            raise RuntimeError(f"{REQUEST_FIFO} существует и не является FIFO")
        os.unlink(REQUEST_FIFO)

    os.mkfifo(REQUEST_FIFO)
    print(f"FIFO-сервер запущен: {REQUEST_FIFO}")
    print("Остановка: Ctrl+C")

    try:
        while True:
            # После закрытия клиентом канала открываем его заново.
            with open(REQUEST_FIFO, "r") as request_file:
                for line in request_file:
                    if line.strip():
                        handle_request(line)
    except KeyboardInterrupt:
        print("\nСервер останавливается")
    finally:
        if os.path.exists(REQUEST_FIFO):
            os.unlink(REQUEST_FIFO)
        print("FIFO-сервер остановлен, канал удалён")


if __name__ == "__main__":
    main()
