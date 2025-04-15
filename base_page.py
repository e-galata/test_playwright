import allure
import math
import time
import random
import logging

class AllureStepMeta(type):
    """
    Метакласс для автоматического добавления allure.step ко всем методам класса кроме базового.
    """
    def __new__(cls, name, bases, dct):
        # Создаем класс сначала без изменений
        new_class = super().__new__(cls, name, bases, dct)
        
        # Проверяем, что это не сам BasePage (но учитываем его наследников)
        if name != "BasePage":
            for attr_name, attr_value in vars(new_class).items():
                if callable(attr_value) and not attr_name.startswith("__"):
                    if attr_value.__doc__:  # Только для методов с docstring
                        setattr(
                            new_class, 
                            attr_name, 
                            allure.step(attr_value.__doc__)(attr_value)
                        )
        return new_class

class BasePage(metaclass=AllureStepMeta):
    """
    Base class for any page of the tests
    """
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

    def human_like_mouse_move(
        self,
        locator_or_selector,
        *,
        speed: float = 2.0,
        steps: int = None,
        deviation: float = 0.2
    ):
        """
        Оптимизированная имитация человеческого движения курсора.
        Args:
            locator_or_selector: Локатор или CSS-селектор
            speed: Скорость движения (2.0 - быстрее стандартной)
            steps: Количество шагов (None для авторасчета)
            deviation: Отклонение от прямой (0-1)
        """
        try:
            page = self.page
            locator = page.locator(locator_or_selector) if isinstance(locator_or_selector, str) else locator_or_selector

            # Оптимизация: объединяем ожидание и скролл
            locator.scroll_into_view_if_needed()
            box = locator.bounding_box()
            if not box:
                raise ValueError("Элемент не видим или не имеет размеров")

            # Вычисляем целевые координаты
            target_x = box["x"] + box["width"] / 2
            target_y = box["y"] + box["height"] / 2

            # Оптимизация: начинаем с текущей позиции курсора (если доступно)
            start_x, start_y = 0, 0

            distance = math.sqrt((target_x - start_x)**2 + (target_y - start_y)**2)
            steps = steps or max(8, min(30, int(distance / (15 * speed))))  # Оптимизированный расчет шагов

            # Оптимизация: предварительно вычисляем все точки траектории
            points = []
            for i in range(steps + 1):
                t = i / steps
                x = start_x + (target_x - start_x) * t
                y = start_y + (target_y - start_y) * t
            
                if deviation > 0 and 0 < t < 1:
                    max_offset = distance * deviation * 0.3  # Уменьшенное отклонение
                    x += random.uniform(-max_offset, max_offset) * (1 - t)
                    y += random.uniform(-max_offset, max_offset) * (1 - t)
            
                points.append((x, y))

            # Оптимизация: уменьшенное количество sleep и группировка движений
            for i, (x, y) in enumerate(points):
                page.mouse.move(x, y)
                if i % 2 == 0:  # Sleep только для каждого второго шага
                    time.sleep(random.uniform(0.005, 0.015) / speed)

        except Exception as e:
            selector = getattr(locator, '_selector', str(locator))
            logging.error(f"Ошибка движения к {selector}: {str(e)}")
            raise ValueError(f"Ошибка перемещения курсора: {str(e)}")

        return locator
