import json
import pytest
import requests
from schemas.user import SCHEMAS
from typing import Optional, Dict, Any
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
        pytest.fail(warning_msg)
    
    try:
        user_data = schema_class(**body).model_dump()
        yield user_data  # Возвращаем данные в тест
    
    except ValidationError as e:
        pytest.fail(f"Ошибка валидации: {e}")

def _make_api_request(url, method, expected_status, payload=None, timeout=10):
    """
    Универсальный обработчик API запросов.
    Возвращает данные из ответа или завершает тест с ошибкой при проблемах.
    """
    try:
        # Выполняем запрос
        response = requests.request(
            method=method.upper(),
            url=url,
            json=payload,
            timeout=timeout
        )

        # Проверка статус-кода
        if response.status_code != expected_status:
            pytest.fail(
                f"Неверный статус-код ответа.\n"
                f"Ожидалось: {expected_status}\n"
                f"Получено: {response.status_code}\n"
                f"URL: {method} {url}\n"
                f"Ответ: {response.text[:500]}"
            )

        # Парсинг JSON
        try:
            # Проверяем, есть ли содержимое в ответе
            if not response.content:
                return None
    
            response_data = response.json()
    
            # Расширенная проверка на "пустые" данные
            if response_data is None or response_data == "" or response_data in ([], {}, ""):
                return None
        
        except ValueError as e:
            pytest.fail(
                f"Невалидный JSON в ответе. Ошибка: {str(e)}\n"
                f"URL: {method} {url}\n"
                f"Ответ: {response.text[:500]}"
            ) 

        # Возвращаем распарсенные данные
        return response_data

    except requests.exceptions.Timeout:
        pytest.fail(
            f"Превышено время ожидания ({timeout} сек).\n"
            f"URL: {method} {url}"
        )

    except requests.exceptions.RequestException as e:
        pytest.fail(
            f"Ошибка при выполнении запроса.\n"
            f"URL: {method} {url}\n"
            f"Ошибка: {str(e)}"
        )

@pytest.fixture
def temporary_test_user():
     create = _make_api_request(url="https://reqres.in/api/users",method="POST",payload={"name":"test","job":"qa"},expected_status=201)
     assert "id" in create
     yield
     delete = _make_api_request(url="https://reqres.in/api/users/"+create["id"],method="DELETE",expected_status=204)
