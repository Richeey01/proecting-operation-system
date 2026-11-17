from translate import PAGE_SIZE, load_page_table

# 16 страниц делим на 4 группы по 4 страницы
L2_SIZE = 4


def build_two_level(flat_table):
    directory = {}

    for page, frame in flat_table.items():
        first = page // L2_SIZE
        second = page % L2_SIZE

        if first not in directory:
            directory[first] = {}

        directory[first][second] = frame

    return directory


def translate_two_level(addr, directory):
    page = addr // PAGE_SIZE
    offset = addr % PAGE_SIZE

    first = page // L2_SIZE
    second = page % L2_SIZE

    level2 = directory.get(first, {})
    frame = level2.get(second)

    if frame is None:
        return None

    return frame * PAGE_SIZE + offset


table = load_page_table()
directory = build_two_level(table)

for addr in [1200, 3100, 5000]:
    physical = translate_two_level(addr, directory)

    print(f"Адрес {addr} -> {physical}")

print("\nБез TLB для успешного доступа:")
print("1. Чтение таблицы первого уровня")
print("2. Чтение таблицы второго уровня")
print("3. Чтение самих данных")
print("Всего: 3 обращения к памяти")