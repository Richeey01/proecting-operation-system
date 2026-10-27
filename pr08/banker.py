import sys

def parse_bank_file(filename):
    with open(filename) as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    # Ищем AVAILABLE
    available = []
    alloc = []
    max_m = []
    
    mode = None
    for line in lines:
        if line.startswith("AVAILABLE:"):
            available = list(map(int, line.split()[1:]))
        elif line.startswith("ALLOCATION:"):
            mode = "alloc"
            continue
        elif line.startswith("MAX:"):
            mode = "max"
            continue
            
        if mode == "alloc":
            nums = list(map(int, line.split()))
            alloc.append(nums)
            if len(alloc) == 5:
                mode = None
        elif mode == "max":
            nums = list(map(int, line.split()))
            max_m.append(nums)
            if len(max_m) == 5:
                mode = None
                
    return available, alloc, max_m

def is_safe(available, alloc, max_m):
    num_procs = len(alloc)
    num_res = len(available)
    
    work = list(available)
    finish = [False] * num_procs
    safe_seq = []
    
    need = [[max_m[i][j] - alloc[i][j] for j in range(num_res)] for i in range(num_procs)]
    
    while len(safe_seq) < num_procs:
        found = False
        for i in range(num_procs):
            if not finish[i]:
                if all(need[i][j] <= work[j] for j in range(num_res)):
                    for j in range(num_res):
                        work[j] += alloc[i][j]
                    finish[i] = True
                    safe_seq.append(f"P{i}")
                    found = True
                    break
        if not found:
            return False, []
            
    return True, safe_seq

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "bank1.txt"
    avail, alloc, max_m = parse_bank_file(filename)
    
    print(f"Проверка файла {filename}:")
    safe, seq = is_safe(avail, alloc, max_m)
    if safe:
        print(f"Состояние БЕЗОПАСНОЕ. Последовательность: {seq}")
    else:
        print("Состояние НЕБЕЗОПАСНОЕ (UNSAFE).")
