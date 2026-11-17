from pathlib import Path

PAGE_SIZE = 1024
NUM_PAGES = 16
BASE_DIR = Path(__file__).resolve().parent


def load_page_table(filename="pagetable.txt"):
    table = {}

    path = BASE_DIR / filename

    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            page, frame = line.split()
            page = int(page)

            if not 0 <= page < NUM_PAGES:
                raise ValueError(f"Неверная страница: {page}")

            table[page] = None if frame == "-" else int(frame)

    return table


def translate(addr, table):
    if not 0 <= addr < NUM_PAGES * PAGE_SIZE:
        raise ValueError("Адрес вне логического пространства")

    page = addr // PAGE_SIZE
    offset = addr % PAGE_SIZE

    frame = table.get(page)

    if frame is None:
        return page, offset, None, None

    physical = frame * PAGE_SIZE + offset

    return page, offset, frame, physical


def main():
    table = load_page_table()

    with open(BASE_DIR / "refs.txt", encoding="utf-8") as file:
        addresses = [
            int(line.strip())
            for line in file
            if line.strip()
        ]

    for addr in addresses:
        try:
            page, offset, frame, physical = translate(
                addr, table
            )

            if frame is None:
                print(
                    f"{addr}: page={page}, offset={offset} "
                    "-> СТРАНИЧНЫЙ ОТКАЗ"
                )
            else:
                print(
                    f"{addr}: page={page}, offset={offset}, "
                    f"frame={frame} -> physical={physical}"
                )

        except ValueError as error:
            print(f"{addr}: ОШИБКА: {error}")


if __name__ == "__main__":
    main()