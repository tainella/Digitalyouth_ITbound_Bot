import argparse
import sys

from .base import Base, engine, session_scope
from .placeholders import placeholders
from ..core.settings import Settings

GREEN = "\033[92m"
RED = "\033[91m"
ENDC = '\033[0m'


def init_db():
    with session_scope() as session:
        Base.metadata.create_all(engine)
        print(f'{GREEN}База данных "{Settings().sqlite_dsn.split("/")[-1]}" удачно инициализирована{ENDC}')


def rm_db():
    print(f'{RED}ВНИМАНИЕ, ЭТО ДЕЙСТВИЕ УДАЛИТ ВСЕ ДАННЫЕ ИЗ БАЗЫ ДАННЫХ! ДЛЯ ПРОДОЛЖЕНИЕ НАЖМИТЕ ENTER{ENDC}')
    input()
    Base.metadata.drop_all(engine)
    print(f'{GREEN}База данных "{Settings().sqlite_dsn.split("/")[-1]}" удачно удалена{ENDC}')


def main():
    parser = argparse.ArgumentParser(description='менеджер базы данных')
    parser.add_argument('--init', action="store_true", help='инициализировать базу данных')
    parser.add_argument('--rm', action="store_true", help='удалить базу данных')
    parser.add_argument('--recreate', action="store_true", help='удалить и инициализировать базу данных')
    parser.add_argument('--placeholder', action="store_true", help='добавить в БД плейхолдеры')
    parser.add_argument('--all', action="store_true", help='сделать всё выше указанное')
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.init:
        init_db()
        sys.exit(0)
    if args.rm:
        rm_db()
        sys.exit(0)
    if args.recreate:
        rm_db()
        init_db()
        sys.exit(0)
    if args.placeholder:
        with session_scope() as session:
            placeholders(session)
        sys.exit(0)
    if args.all:
        rm_db()
        init_db()
        with session_scope() as session:
            placeholders(session)
        sys.exit(0)


if __name__ == "__main__":
    main()