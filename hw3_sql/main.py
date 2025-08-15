import json
import argparse
import sys
import logging
import mysql.connector
from typing import List, Dict, Any
from pathlib import Path


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


class DataReader:
    @staticmethod
    def load_json(path: Path) -> List[Dict[str, Any]]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f'Data file not found: {path}')
            sys.exit(1)
        except json.JSONDecodeError:
            logging.error(f'Error JSON file: {path}')
            sys.exit(1)


class DatabaseManager:
    def __init__(self, db_config: Dict[str, Any]):
        self.config = db_config
        self.connection = None

    def __enter__(self):
        try:
            conn = mysql.connector.connect(host=self.config['db_host'],
                                           user=self.config['db_user'],
                                           password=self.config['db_password'])
            cursor = conn.cursor()
            cursor.execute(
                f'CREATE DATABASE IF NOT EXISTS {self.config["db_name"]} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
            conn.database = self.config['db_name']
            self.connection = conn
            return self.connection
        except mysql.connector.Error as e:
            logging.error(f'Error mySQL connecting : {e}')
            sys.exit(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    @staticmethod
    def create_tables(connection):
        create_rooms_table_query = 'CREATE TABLE rooms (id INT PRIMARY KEY, name VARCHAR(255) NOT NULL);'
        create_students_table_query = '''
        CREATE TABLE students (
            id INT PRIMARY KEY, name VARCHAR(255) NOT NULL, birthday DATETIME NOT NULL,
            sex CHAR(1) NOT NULL, room_id INT,
            FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE SET NULL
        );
        '''
        try:
            with connection.cursor() as cursor:
                cursor.execute('DROP TABLE IF EXISTS students;')
                cursor.execute('DROP TABLE IF EXISTS rooms;')
                cursor.execute(create_rooms_table_query)
                cursor.execute(create_students_table_query)
                connection.commit()
        except mysql.connector.Error as e:
            logging.error(f'Error creating tables: {e}')
            connection.rollback()
            sys.exit(1)

    @staticmethod
    def insert_data(connection, rooms_data: List[Dict], students_data: List[Dict]):
        insert_rooms_query = 'INSERT INTO rooms (id, name) VALUES (%s, %s)'
        insert_students_query = 'INSERT INTO students (id, name, birthday, sex, room_id) VALUES (%s, %s, %s, %s, %s)'
        rooms_to_insert = [(room['id'], room['name']) for room in rooms_data]
        students_to_insert = [(s['id'], s['name'], s['birthday'], s['sex'], s['room']) for s in students_data]
        try:
            with connection.cursor() as cursor:
                cursor.executemany(insert_rooms_query, rooms_to_insert)
                cursor.executemany(insert_students_query, students_to_insert)
                connection.commit()
        except mysql.connector.Error as e:
            logging.error(f'Error inserting data: {e}')
            connection.rollback()
            sys.exit(1)


class QueryRunner:
    def __init__(self, connection):
        self.connection = connection

    def _execute_query(self, query: str, description: str):
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                print(f'\n--- {description} ---')
                if not results:
                    print('No results found.')
                else:
                    for row in results:
                        print(row)
        except mysql.connector.Error as e:
            logging.error(f'Query failed [{description}]: {e}')

    @staticmethod
    def _load_sql(filename: str) -> str:
        query_path = Path('sql') / filename
        try:
            with open(query_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logging.error(f'SQL query file not found: {query_path}')
            sys.exit(1)

    def run_all(self):
        self._execute_query(self._load_sql('1_rooms_with_student_counts.sql'), 'List of rooms with student counts')
        self._execute_query(self._load_sql('2_top5_rooms_min_avg_age.sql'),
                            'Top 5 rooms with smallest average student age')
        self._execute_query(self._load_sql('3_top5_rooms_max_age_diff.sql'), 'Top 5 rooms with largest age difference')
        self._execute_query(self._load_sql('4_rooms_with_mixed_sex.sql'), 'List of rooms with mixed-sex students')


def main():
    parser = argparse.ArgumentParser(description='Load student/room data into a MySQL database and run queries.')
    parser.add_argument('--students', default='data/students.json', help='Students.json path.')
    parser.add_argument('--rooms', default='data/rooms.json', help='Rooms.json path.')
    parser.add_argument('--config', default='config.json', help='DB config file path.')
    args = parser.parse_args()

    config = load_config(args.config)
    students_data = DataReader.load_json(args.students)
    rooms_data = DataReader.load_json(args.rooms)

    db_manager = DatabaseManager(config)

    with db_manager as connection:
        DatabaseManager.create_tables(connection)
        DatabaseManager.insert_data(connection, rooms_data, students_data)

        query_runner = QueryRunner(connection)
        query_runner.run_all()


if __name__ == '__main__':
    main()