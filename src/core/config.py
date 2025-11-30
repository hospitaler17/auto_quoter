import json
import sys
from typing import Any, Dict


def load_config(config_path: str = 'config.json') -> Dict[str, Any]:
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл конфигурации '{config_path}' не найден.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Ошибка: Неверный формат JSON в '{config_path}'.")
        sys.exit(1)
