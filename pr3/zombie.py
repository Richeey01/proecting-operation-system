
import os
import time

pid = os.fork()

if pid == 0:
    print(f"Ребёнок завершился: PID={os.getpid()}", flush=True)
    os._exit(0)

print(f"Родитель: PID={os.getpid()}", flush=True)
print(f"PID ребёнка: {pid}", flush=True)
print("Родитель не вызывает wait() в течение 60 секунд.", flush=True)

time.sleep(60)

os.waitpid(pid, 0)
print("Родитель забрал статус ребёнка и завершает работу.", flush=True)
