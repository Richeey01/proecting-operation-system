import threading
import time

class DeadlockDetectedError(Exception):
    pass

class WaitGraph:
    def __init__(self):
        self.lock = threading.Lock()
        self.graph = {} # {thread_id: set(target_thread_ids)}

    def add_edge(self, t_from, t_to):
        with self.lock:
            if t_from not in self.graph:
                self.graph[t_from] = set()
            self.graph[t_from].add(t_to)
            return self._detect_cycle(t_from)

    def remove_edge(self, t_from, t_to):
        with self.lock:
            if t_from in self.graph and t_to in self.graph[t_from]:
                self.graph[t_from].remove(t_to)

    def _detect_cycle(self, start):
        visited = set()
        stack = set()
        
        def dfs(node):
            if node in stack:
                return True
            if node in visited:
                return False
            visited.add(node)
            stack.add(node)
            for neighbor in self.graph.get(node, []):
                if dfs(neighbor):
                    return True
            stack.remove(node)
            return False

        return dfs(start)

global_wfg = WaitGraph()

class TrackedLock:
    def __init__(self, name="Lock"):
        self.mutex = threading.Lock()
        self.name = name
        self.current_holder = None

    def acquire(self, timeout=1.0):
        t_id = threading.get_ident()
        start_time = time.time()
        
        while True:
            # Пробуем захватить мьютекс без блокировки
            if self.mutex.acquire(blocking=False):
                self.current_holder = t_id
                # Удаляем возможные старые ребра ожидания для этого потока
                if t_id in global_wfg.graph:
                    global_wfg.graph[t_id].clear()
                return True
            
            # Если занят, кто владелец?
            holder = self.current_holder
            if holder and holder != t_id:
                if global_wfg.add_edge(t_id, holder):
                    raise DeadlockDetectedError(f"Обнаружен тупик (Deadlock): поток {t_id} ждет владельца {holder}!")
            
            if timeout >= 0 and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Таймаут ожидания блокировки {self.name}")
            
            time.sleep(0.01)

    def release(self):
        t_id = threading.get_ident()
        if self.current_holder == t_id:
            self.current_holder = None
            if t_id in global_wfg.graph:
                global_wfg.graph[t_id].clear()
        try:
            self.mutex.release()
        except RuntimeError:
            pass

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

if __name__ == "__main__":
    lock_a = TrackedLock("LockA")
    lock_b = TrackedLock("LockB")

    def thread1():
        try:
            with lock_a:
                print("Поток 1 захватил A")
                time.sleep(0.05)
                with lock_b:
                    print("Поток 1 захватил B")
        except DeadlockDetectedError as e:
            print(f"[ПОЙМАНО В ПОТОКЕ 1]: {e}")

    def thread2():
        try:
            with lock_b:
                print("Поток 2 захватил B")
                time.sleep(0.05)
                with lock_a:
                    print("Поток 2 захватил A")
        except DeadlockDetectedError as e:
            print(f"[ПОЙМАНО В ПОТОКЕ 2]: {e}")

    t1 = threading.Thread(target=thread1)
    t2 = threading.Thread(target=thread2)
    t1.start(); t2.start()
    t1.join(); t2.join()
    print("Тест TrackedLock завершен успешно (без зависаний).")
