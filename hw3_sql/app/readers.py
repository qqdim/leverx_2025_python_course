import json
import sys
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any


class Reader(ABC):
    @abstractmethod
    def read(self,path: Path) -> List[Dict[str, Any]]:
        pass


class JSONReader(Reader):
    def read(self,path: Path) -> List[Dict[str, Any]]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f'File not found: {path}')
            sys.exit(1)
        except json.JSONDecodeError:
            logging.error(f'Error JSON file: {path}')
            sys.exit(1)


def get_reader(file_path: Path) -> Reader:
    extension = file_path.suffix.lower()
    if extension == '.json':
        return JSONReader()
    else:
        logging.error(f"Unsupported file format: {extension}")
        sys.exit(1)