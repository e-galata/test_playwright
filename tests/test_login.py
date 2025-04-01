import pytest
from pages.login_page import LoginPage
from messages.login_messages import LoginMessages

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
def test_login(page, api_user, mock_api, create_and_delete_test_user):
    '''
    page - a fixture contains the page context with which we will interact.
    api_user - a fixture where we pass user parameters, specify the schema, and provide
    fields; any missing fields will be generated by faker and returned as a ready JSON
    mock_api - a mock API fixture; we pass parameters to it and receive a ready mock API.
    create_and_delete_test_user - creates a temporary user and deletes it during teardown.
    ''' 

    mock_api(
        url_pattern="**/frame/login-submit",
        method="POST",
        body={
            "success": False,
            "message": LoginMessages.ERROR_TEXT
        }
    )


    (
        LoginPage(page)
        .navigate()
        .switch_to_password_auth()
        .fill_credentials(api_user["email"], api_user["password"])
        .submit()
        .verify_error_message()
    )
