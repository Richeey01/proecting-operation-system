import threading
import time
import random

class Fork:
    def __init__(self, index):
        self.index = index
        self.locked_by = index
        self.lock = threading.Lock()

    def acquire(self, blocking=True, timeout=-1):
        return self.lock.acquire(blocking, timeout)

    def release(self):
        self.lock.release()

    def __enter__(self):
        self.lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()

class Philosopher(threading.Thread):
    def __init__(self, index, left_fork, right_fork, ordered=False):
        super().__init__()
        self.index = index
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.meals_eaten = 0
        self.ordered = ordered

    def run(self):
        for _ in range(5):
            # Думает
            time.sleep(random.uniform(0.01, 0.05))
            
            if self.ordered:
                # Решение: упорядоченный захват (сначала вилка с меньшим индексом)
                first, second = (self.left_fork, self.right_fork) if self.left_fork.index < self.right_fork.index else (self.right_fork, self.left_fork)
                with first:
                    with second:
                        self.eat()
            else:
                # Потенциальный deadlock (наивный подход)
                with self.left_fork:
                    time.sleep(0.01)
                    with self.right_fork:
                        self.eat()

    def eat(self):
        self.meals_eaten += 1

if __name__ == "__main__":
    print("Запуск обедающих философов с упорядочиванием вилок (без deadlock)...")
    forks = [Fork(i) for i in range(5)]
    philosophers = [
        Philosopher(i, forks[i], forks[(i+1)%5], ordered=True) 
        for i in range(5)
    ]
    
    for p in philosophers: p.start()
    for p in philosophers: p.join()
    
    for p in philosophers:
        print(f"Философ {p.index} поел {p.meals_eaten} раз.")
    print("Все философы успешно завершили трапезу без взаимоблокировок.")
