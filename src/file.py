import csv
import argparse
from tabulate import tabulate
import re
from statistics import mean

FILE = '--file'
FILTER = '--where'
AGGREGATION = '--aggregate'
FILENAME = 'data.csv'


def add_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Условия фильтрации и аггрегации',
        usage='main.py [options]'
        )
    parser.add_argument(
        FILE,
        required=False,
        type=str,
        help='Метка пути к файлу'
        )
    parser.add_argument(
        FILTER,
        type=str,
        required=False,
        help='Метка фильтрации')
    parser.add_argument(
        AGGREGATION,
        type=str,
        required=False,
        help='Метка аггрегации')

    return parser


def check_arguments(parser: argparse.ArgumentParser, cli_args=None) -> bool:
    args = parser.parse_args(cli_args)

    if args.file is None:
        print('Параметр --file не указан')
        return False

    return True


def load_data(path: str) -> list[dict]:
    try:
        with open(path, 'r') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError as e:
        print('Ошибка чтения файла:', e)
        return []


def apply_where(data: list[dict], where: str) -> list[dict]:
    if not where:
        return data

    pattern = r'^([a-z]+)([<>=])(.+)$'
    match = re.match(pattern, where)
    if match:
        key, operation, value = match.groups()
    else:
        print('Параметр where неправильно задан')
        return data
    try:
        value_converted = float(value)
    except ValueError:
        value_converted = value

    if type(value_converted) is float:
        match operation:
            case '=':
                filtered_data = [
                    el for el in data if float(el[key]) == value_converted
                    ]
                return filtered_data
            case '>':
                filtered_data = [
                    el for el in data if float(el[key]) > value_converted
                    ]
                return filtered_data

            case '<':
                filtered_data = [
                    el for el in data if float(el[key]) < value_converted
                    ]
                return filtered_data

    else:
        if operation == '=':
            filtered_data = [
                el for el in data if el[key] == value_converted
                ]
            return filtered_data
        else:
            print('Для нечисловых значений может использоваться только оператор =')
            return data


def apply_aggregate(data: list[dict], aggregate: str) -> tuple[str, float]:
    if not aggregate:
        print('Параметр aggregate не задан')
        return ()

    pattern = r'^([a-z]+)=(min|avg|max)$'
    match = re.match(pattern, aggregate)
    if match:
        key, value = match.groups()
    else:
        print('Параметр aggregate неправильно задан')
        return ()
    if key not in ['price', 'rating']:
        print('Нельзя применять аггрегацию к нечисловым столбцам')
        return ()
    else:
        values = [float(el[key]) for el in data]

        match value:
            case 'min':
                res = min(values)
            case 'max':
                res = max(values)
            case 'avg':
                res = mean(values)

    return value, res


def execute_command():
    parser = add_args()
    is_checked = check_arguments(parser)
    if not is_checked:
        return
    else:
        args = parser.parse_args()
        data = load_data(args.file)
        filtered = apply_where(data, args.where) if args.where else data
        if args.aggregate:
            result = apply_aggregate(filtered, args.aggregate)
            if len(result) == 2:
                header, value = result
                print(tabulate([[value]], headers=[header], tablefmt='github'))

        else:
            if filtered != data:
                print(tabulate(filtered, headers='keys', tablefmt='github'))
