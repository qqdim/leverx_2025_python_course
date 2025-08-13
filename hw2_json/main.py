import json
import argparse
import sys
from abc import ABC, abstractmethod
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


class DataLoader:
    def load_json(self, path: str) -> list:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Cannot read this JSON: {path}", file=sys.stderr)
            sys.exit(1)


class DataMerger:
    def merge(self, rooms: list, students: list) -> list:
        rooms_dict = {room['id']: {**room, "students": []} for room in rooms}
        for student in students:
            room_id = student.get('room')
            if room_id in rooms_dict:
                student_info = {'id': student['id'],
                                'name': student['name']}
                rooms_dict[room_id]['students'].append(student_info)
        return list(rooms_dict.values())


class Exporter(ABC):
    @abstractmethod
    def export(self, data: list, path: str):
        pass


class JSONExporter(Exporter):
    def export(self, data: list, path: str):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f'Error export {path}: {e}', file=sys.stderr)
            sys.exit(1)


class XMLExporter(Exporter):
    def export(self, data: list, path: str):
        root = Element('rooms')

        for room_item in data:
            room_el = SubElement(root, 'room')
            room_el.set('id', str(room_item['id']))
            room_el.set('name', room_item['name'])

            students_el = SubElement(root, 'students')
            for student_item in room_item['students']:
                student_el = SubElement(students_el, 'student')
                student_el.set('id', str(student_item['id']))
                student_el.text = student_item['name']

        xml_string = tostring(root, 'utf-8')
        parsed_string = minidom.parseString(xml_string)
        prety_xml = parsed_string.toprettyxml(indent=' ')

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(prety_xml)
        except IOError as e:
            print(f'Error export {path}: {e}', file=sys.stderr)
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='test')
    parser.add_argument('--rooms', '-r', default='src/rooms.json', help='Rooms.json path')
    parser.add_argument('--students', '-s', default='src/students.json', help='Students.json path')
    parser.add_argument('--format', '-f', default='json', choices=['json', 'xml'], help='Students.json path')
    parser.add_argument('--output', '-o', help='Output file path')
    args = parser.parse_args()

    loader = DataLoader()
    rooms_data = loader.load_json(args.rooms)
    students_data = loader.load_json(args.students)

    process = DataMerger()
    merged_data = process.merge(rooms_data, students_data)

    output_path = args.output or f'output.{args.format.lower()}'
    exporters = {
        'json': JSONExporter(),
        'xml': XMLExporter(),
    }
    exporter = exporters[args.format.lower()]
    exporter.export(merged_data, output_path)


if __name__ == "__main__":
    main()
