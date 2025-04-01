class BasePage:
    '''
    Base class for any page of the tests
    '''
    BASE_URL = "https://id.skyeng.ru"
    
    def __init__(self, page):
        self.page = page
    
    def goto(self, path=""):
        self.page.goto(f"{self.BASE_URL}{path}")
        return self
