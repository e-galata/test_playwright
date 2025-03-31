import json
import pytest
import requests
from schemas.user import SCHEMAS
from pydantic import ValidationError

def process_to_valid_json(body):
    if isinstance(body, str):
        # Словарь замен (что → на что)
        replacements = {
            "True": "true",
            "False": "false",
        }
        for old, new in replacements.items():
            body = body.replace(old, new)
        return json.loads(body)
    return body

@pytest.fixture
def mock_api(page):
    def add_mock(url_pattern: str, **kwargs):
        page.route(url_pattern, _create_mock_handler(**kwargs))
    return add_mock

def _create_mock_handler(method="GET", action="fulfill", body={}, status=200):
    def handler(route):
        if action == "fulfill" and route.request.method == method.upper():
            route.fulfill(status=status, json=process_to_valid_json(body))
        elif action == "abort":
            route.abort()
    return handler

@pytest.fixture
def api_user(request):
    """Фикстура, которая:
    1. Получает schema и **kwargs из параметров теста
    2. Находит Pydantic-схему
    3. Генерирует недостающие обязательные поля
    4. Создает пользователя через API
    5. Возвращает (json_data, fields) тесту
    6. Удаляет пользователя после теста
    """
    # Получаем параметры из теста
    schema_name = request.param["schema"]
    body = request.param.get("body", {})
    
    # Выбираем схему
    schema_class = SCHEMAS[schema_name]
    
    extra_fields = set(body.keys()) - set(schema_class.model_fields.keys())
    if extra_fields:
        warning_msg = f"⚠️  Переданы несуществующие поля в '{schema_name}': {extra_fields}"
        warnings.warn(warning_msg, UserWarning)
        print(f"\n\033[93m{warning_msg}\033[0m")  # Жёлтый цвет в консоли
    
    # Генерируем данные с учетом переданных полей
    try:
        user_data = schema_class(**body).model_dump()
    
    # Создаем пользователя
    #requests.post("https://api.example.com/users", json=user_data)
        print(f"\nДелаем запрос на создание пользователя с полями\n {user_data}")
    
        yield user_data  # Возвращаем данные в тест
    
    except ValidationError as e:
        pytest.fail(f"Ошибка валидации: {e}")

    finally:
    # Удаляем пользователя
    # requests.delete(f"https://api.example.com/users/{user_data['email']}")
        print(f"\nУдаляем пользователя с {user_data['email']}")
