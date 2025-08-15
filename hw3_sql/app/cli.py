import json
import argparse
import sys
import logging
from pathlib import Path
from .readers import get_reader
from .db import DatabaseManager, QueryRunner
from typing import Dict, Any


def load_config(config_path: Path) -> Dict[str, Any]:
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f'Config file not found: {config_path}.')
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f'Error JSON file: {config_path}')
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Load student/room data into a MySQL database and run queries.')
    parser.add_argument('--students', default='data/students.json', help='Students.json path.')
    parser.add_argument('--rooms', default='data/rooms.json', help='Rooms.json path.')
    parser.add_argument('--config', default='config.json', help='DB config file path.')
    args = parser.parse_args()

    config = load_config(args.config)

    student_reader = get_reader(Path(args.students))
    room_reader = get_reader(Path(args.rooms))

    students_data = student_reader.read(Path(args.students))
    rooms_data = room_reader.read(Path(args.rooms))

    db_manager = DatabaseManager(config)

    with db_manager as connection:
        DatabaseManager.create_tables(connection)
        DatabaseManager.insert_data(connection, rooms_data, students_data)

        query_runner = QueryRunner(connection)
        query_runner.run_all()