#!/usr/bin/env bash
# report.sh <каталог> <ERROR|WARN> [--top N]

usage() {
    echo "Использование: $0 <каталог> <ERROR|WARN> [--top N]" >&2
    echo "  каталог  - папка с файлами *.log" >&2
    echo "  уровень  - ERROR или WARN" >&2
    echo "  --top N  - показать только N первых модулей (N - целое число > 0)" >&2
}

if [ $# -lt 2 ]; then
    usage
    exit 1
fi

dir="$1"
level="$2"
top=""

if [ "$level" != "ERROR" ] && [ "$level" != "WARN" ]; then
    echo "Ошибка: неверный уровень '$level'" >&2
    usage
    exit 1
fi

if [ ! -d "$dir" ]; then
    echo "Ошибка: каталог '$dir' не существует" >&2
    usage
    exit 1
fi

if [ $# -gt 2 ]; then
    if [ "$3" != "--top" ] || [ $# -ne 4 ]; then
        echo "Ошибка: неверные аргументы" >&2
        usage
        exit 1
    fi
    top="$4"
    if ! [[ "$top" =~ ^[0-9]+$ ]] || [ "$top" -lt 1 ]; then
        echo "Ошибка: N должно быть целым числом больше 0, получено '$top'" >&2
        usage
        exit 1
    fi
fi

result=$(cat "$dir"/*.log \
  | awk -v lvl="$level" '$3 == lvl { sub(/^module=/, "", $4); print $4 }' \
  | sort | uniq -c | sort -rn \
  | awk '{ printf "%-10s %6d\n", $2, $1 }')

if [ -n "$top" ]; then
    echo "$result" | head -n "$top"
else
    echo "$result"
fi
