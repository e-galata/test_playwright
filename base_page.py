import allure

class AllureStepMeta(type):
    """
    Метакласс для автоматического добавления allure.step ко всем методам класса.
    """
    def __new__(cls, name, bases, dct):
        for attr_name, attr_value in dct.items():
            if callable(attr_value) and not attr_name.startswith("__"):
                dct[attr_name] = allure.step(attr_value.__doc__)(attr_value)
        return super().__new__(cls, name, bases, dct)

class BasePage(metaclass=AllureStepMeta):
    '''
    Base class for any page of the tests
    '''
    BASE_URL = "https://id.skyeng.ru"
    
    def __init__(self, page):
        self.page = page
    
    def goto(self, path=""):
        """Go to the page"""
        self.page.goto(f"{self.BASE_URL}{path}")
        return self

    def page_loaded(self, method="load"):
        """Method to wait when page loaded"""
        self.page.wait_for_load_state(method)
        return self

    def open_page_by_click(self, selector, page_class):
        """
        Universal method to open new page by selector, return the new page
        of page_class for work with its own methods
        """
        assert issubclass(page_class, BasePage), "Use page classes that inherit from BasePage"
        
        with self.page.expect_popup() as popup_info:
            self.page.click(selector)
        return page_class(popup_info.value).page_loaded()
