import pytest
from playwright.sync_api import expect

@pytest.mark.parametrize("api_user", [
    {
        "schema": "/api/users",
        "body": {"name": "Иван Тестовый"}
    },
    {
        "schema": "premium",
        "body": {
            "email": "test@example.com",
            "credit_card": "4111111111111111"
        }
    }
], indirect=True)
def test_dynamic_user_creation(page, api_user, mock_api, create_and_delete_test_user):
    
    # Мокаем API логина
    mock_api("**/frame/login-submit", method="POST", body='{"success": false, "message": "mocked shmoked"}')

    # Создаем пользователя, не явно, в фикстуре, после теста он сам удалится

    # Тест логина
    page.goto("https://id.skyeng.ru/login")
    page.get_by_text("Войти с помощью пароля", exact=True).click()
    page.locator('input[name="username"]').fill(api_user["email"])
    page.locator('input[name="password"]').fill(api_user["password"])
    page.locator('button:has-text("Войти")').click()
    
    # Проверка результата
    error_locator = page.get_by_text("mocked shmoked")
    expect(error_locator).to_be_visible()
    expect(error_locator).to_contain_text("mocked shmoked")
    # Дополнительная проверка точного текста
    expect(error_locator).to_have_text("mocked shmoked")  # Полное совпадение
