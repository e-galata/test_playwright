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

    def page_loaded(self, method="load"):
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
