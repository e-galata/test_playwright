import json
import pytest
import requests
from schemas.user import SCHEMAS
from pydantic import ValidationError

def process_to_valid_json(body):
    '''
    Getting ready string to be json, replace boolean words to compatible
    '''
    if isinstance(body, str):
        # Replace (from → to)
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
    '''
    Fixture to mock REST api, gets url_pattern and params, execute add_mock that
    will return page.route. Method, action, status have a defualt value,
    can abort api request. In body might be string like a dict
    '''
    def add_mock(url_pattern, **kwargs):
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
    """
    Gets a schema and **kwargs from test (indirect, usually by parametrize)
    Gets data from "body", compare with schema (Pydantic)
    Generate missing data if it required by schema and doesn't get by "body"
    If we get unexpected fields from body (which are not in the schema), test
    will be stopped and alerted about it
    Passes context to use in the test (user_data - filled json by schema)
    Stops the test if can't make user_data by model_dump from Pydantic
    """
    # Getting schema from params
    schema_name = request.param["schema"]
    body = request.param.get("body", {})
    
    # Choose the schema from pydantic schemas we already have, must have the same names
    schema_class = SCHEMAS[schema_name]
    
    extra_fields = set(body.keys()) - set(schema_class.model_fields.keys())
    if extra_fields:
        warning_msg = f"⚠️  Non-existent fields passed in '{schema_name}': {extra_fields}"
        pytest.fail(warning_msg)
    
    try:
        user_data = schema_class(**body).model_dump()
    
    except ValidationError as e:
        pytest.fail(f"Validation error: {e}")

    yield user_data

def _make_api_request(url, method, expected_status, payload=None, timeout=10):
    """
    A generic API request handler.
    Returns data from the response or fails the test and alert 
    if there are problems.
    """
    try:
        # Make request by requests
        response = requests.request(
            method=method.upper(),
            url=url,
            json=payload,
            timeout=timeout
        )

        # Checking the status code
        if response.status_code != expected_status:
            pytest.fail(
                f"Invalid status code.\n"
                f"Expect: {expected_status}\n"
                f"Receive: {response.status_code}\n"
                f"URL: {method} {url}\n"
                f"Response: {response.text[:500]}"
            )

        # Parsing JSON
        try:
            # Check if there is content in the response
            if not response.text.strip():
                return None

            # Tru to parse JSON
            response_data = response.json()

            # Checking for "empty" data
            if not response_data:  # Check False, [], {}, ""
                return None

            return response_data

        except ValueError as e:
            pytest.fail(
                f"Invalid JSON in the response. Error: {str(e)}\n"
                f"URL: {method} {url}\n"
                f"Response: {response.text[:500]}"
            )

    except requests.exceptions.Timeout:
        pytest.fail(
            f"Timeout exceeded ({timeout} sec).\n"
            f"URL: {method} {url}"
        )

    except requests.exceptions.RequestException as e:
        pytest.fail(
            f"Error executing request.\n"
            f"URL: {method} {url}\n"
            f"Error: {str(e)}"
        )

@pytest.fixture
def create_and_delete_test_user():
    """
    Creating a temporary user and then deleting it.
    Using api request to reqres.in
    The response with user data might be used in the test by 
    yield create_response
    """
    # Create user
    user_data = {"name": "test", "job": "qa"}
    create_response = _make_api_request(
        url="https://reqres.in/api/users",
        method="POST",
        payload=user_data,
        expected_status=201
    )
    
    assert "id" in create_response, "User ID should be in the response"
    user_id = create_response["id"]
    
    yield  # This separates setup from teardown
    
    # Delete user (teardown)
    _make_api_request(
        url=f"https://reqres.in/api/users/{user_id}",
        method="DELETE",
        expected_status=204
    )
