import threading
import time

condition = threading.Condition()
ready = False

checked = threading.Event()
allow_wait = threading.Event()


def waiter():
    global ready

    # Intentionally incorrect: checking without holding the condition lock.
    if not ready:
        print("Поток: условие False, собираюсь ждать")
        checked.set()

        # Force the incorrect interleaving for demonstration.
        allow_wait.wait()

        with condition:
            notified = condition.wait(timeout=2)

        if notified:
            print("Поток: получил уведомление")
        else:
            print("Поток: тайм-аут — уведомление потеряно")


def notifier():
    global ready

    checked.wait()

    with condition:
        ready = True
        print("Другой поток: ready=True, отправляю уведомление")
        condition.notify()

    # Let the waiter start waiting only after notify has happened.
    allow_wait.set()


def main():
    t1 = threading.Thread(target=waiter)
    t2 = threading.Thread(target=notifier)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("Демонстрация завершена")


if __name__ == "__main__":
    main()
