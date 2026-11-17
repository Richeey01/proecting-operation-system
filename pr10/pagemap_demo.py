import os
import ctypes
import struct

PAGE_SIZE = os.sysconf("SC_PAGE_SIZE")

# Создаём реальную переменную в памяти
variable = ctypes.c_int(12345)

# Получаем виртуальный адрес
addr = ctypes.addressof(variable)

# Принудительно читаем значение
print("Значение:", variable.value)
print("Виртуальный адрес:", hex(addr))
print("Размер страницы:", PAGE_SIZE)

# Находим область памяти, содержащую адрес
print("\nСоответствующая область из /proc/self/maps:")

with open("/proc/self/maps") as file:
    for line in file:
        region = line.split()[0]
        start, end = [
            int(x, 16) for x in region.split("-")
        ]

        if start <= addr < end:
            print(line.strip())
            break

# Читаем запись pagemap
index = (addr // PAGE_SIZE) * 8

try:
    with open("/proc/self/pagemap", "rb") as file:
        file.seek(index)
        data = file.read(8)

    if len(data) != 8:
        raise RuntimeError("Не удалось прочитать запись pagemap")

    entry = struct.unpack("Q", data)[0]

    present = bool(entry & (1 << 63))
    pfn = entry & ((1 << 55) - 1)

    print("\nСтраница присутствует:", present)

    if present and pfn != 0:
        physical = pfn * PAGE_SIZE + addr % PAGE_SIZE

        print("PFN:", pfn)
        print("Физический адрес:", hex(physical))

    elif present:
        print("PFN=0: вероятно, номер кадра скрыт.")
        print("Требуется CAP_SYS_ADMIN.")

    else:
        print("Страница сейчас не присутствует в RAM.")

except PermissionError:
    print("Нет прав для чтения pagemap.")
    print("Нужны соответствующие права Linux.")