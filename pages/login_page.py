from playwright.sync_api import expect
from locators.login_locators import LoginLocators
from messages.login_messages import LoginMessages
from base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.locators = LoginLocators()
        self.messages = LoginMessages()
    
    def navigate(self):
        """Navigate to login page"""
        self.goto("/login")
        return self
    
    def switch_to_password_auth(self):
        """Find by text login form"""
        self.page.get_by_text(self.locators.LOGIN_WITH_PASSWORD_BUTTON, exact=True).click()
        return self
    
    def fill_credentials(self, email: str, password: str):
        """Fill a login and password to the form"""
        self.page.locator(self.locators.USERNAME_INPUT).fill(email)
        self.page.locator(self.locators.PASSWORD_INPUT).fill(password)
        return self
    
    def submit(self):
        """Push submit button in the login form"""
        self.page.locator(self.locators.SUBMIT_BUTTON).click()
        return self
    
    def verify_error_message(self):
        """Verify invalid login message"""
        error_locator = self.page.get_by_text(self.locators.ERROR_MESSAGE)
        expect(error_locator).to_be_visible()
        expect(error_locator).to_contain_text(self.messages.ERROR_TEXT)
        expect(error_locator).to_have_text(self.messages.ERROR_TEXT)
        return self
