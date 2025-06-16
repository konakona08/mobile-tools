import configparser
from typing import List, Union

class RegistryReader:
    def __init__(self, file_path: str):
        self.registry = configparser.ConfigParser()
        self._read_config(file_path)

    def _read_config(self, file_path: str):
        current_category = None
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#'):
                    current_category = line[1:].strip()
                    self.registry[current_category] = {}
                elif '=' in line and current_category is not None:
                    key, value = line.split('=', 1)
                    self.registry[current_category][key.strip()] = value.strip()


    def has_category(self, category: str) -> bool:
        return category in self.registry

    def has_element(self, category: str, element: str) -> bool:
        return self.has_category(category) and element in self.registry[category]

    def get_value(self, category: str, element: str) -> List[Union[str, float]]:
        if not self.has_element(category, element):
            raise ValueError(f"Element '{element}' not found in category '{category}'")

        value = self.registry[category][element]
        items = [item.strip() for item in value.split(',')]
        
        result = []
        for item in items:
            try:
                result.append(float(item))
            except ValueError:
                result.append(item)
        
        return result
