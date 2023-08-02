import os
import time

from rest_framework.exceptions import ValidationError
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import telegram
import undetected_chromedriver as uc
from xvfbwrapper import Xvfb

from OzonParseApp.celery import app as celery_app
from products.models import Product
from .constants import (ATTRIBUTES_BLOCK, ATTRIBUTES_HEADER, ATTRIBUTES_ITEMS,
                        DEFAULT_TIMEOUT, DISPLAY_HEIGHT, DISPLAY_WIDTH,
                        PRODUCT_IN_LIST, PRODUCTS_ON_PAGE, URL)


def suppress_exception(uc: uc) -> None:
    """Пакет undetected_chromedriver поднимает ошибку. Эта функция-костыль
    обходит ошибку и позволяет парсеру работать."""
    old_del = uc.Chrome.__del__

    def new_del(self):
        try:
            old_del(self)
        except OSError:
            pass

    setattr(uc.Chrome, '__del__', new_del)


def parse_characters(driver, waiter, chains, element, original_window
                     ) -> dict[str, str]:
    """Функция парсит указанный товар и возвращает его характеристики внутри
    словаря."""
    element.send_keys(Keys.CONTROL + Keys.RETURN)
    waiter.until(EC.number_of_windows_to_be(2))
    new_window = driver.window_handles[-1]
    driver.switch_to.window(new_window)
    driver.execute_script('window.scrollTo(5,4000);')
    time.sleep(5)
    attributes = waiter.until(EC.presence_of_element_located(
        (By.CLASS_NAME, ATTRIBUTES_HEADER)
    ))
    chains.move_to_element(attributes).perform()
    time.sleep(5)
    elements = waiter.until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, ATTRIBUTES_BLOCK)
    ))
    main_dict = {}
    for elem in elements:
        sub_elems = elem.find_elements(By.CSS_SELECTOR, ATTRIBUTES_ITEMS)
        for sub_elem in sub_elems:
            key, value = sub_elem.text.split('\n')
            main_dict[key] = value
    driver.close()
    driver.switch_to.window(original_window)
    return main_dict


def validate_number(number: int) -> bool:
    """Проверяет что количество элементов для парсинга указано корректно."""
    return number and 0 < number <= 51


def parsing(driver, chains, waiter, page: int, items: int) -> list[Product]:
    """Функция принимает в себя номер страницы и количество элементов, которые
    нужно распарсить. Запускается парсинг нужной страницы и проходится по
    нужному количеству элементов. Возвращает список объектов модели."""
    url = URL + f'?page={page}'
    driver.get(url)
    time.sleep(3)
    elements = waiter.until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, PRODUCT_IN_LIST)
    ))
    original_window = driver.current_window_handle
    result = []
    counter = 0
    for element in elements:
        if counter >= items:
            break
        time.sleep(5)
        parsed_values_in_dict = parse_characters(
            driver, waiter, chains, element, original_window
        )
        result.append(Product(json=parsed_values_in_dict))
        counter += 1
    return result


def calculate_pages_to_parse(number: int) -> dict[int, int]:
    """Функция принимает количество элементов, которые нужно распарсить.
    Возвращает словарь, где ключом является номер страницы, а значением
    количество элементов на странице, что нуждаются в парсинге.
    Количество элементов указывается с целью избежать ненужного парсинга на
    последней странице."""
    page: int = 1
    dict_to_return = {}
    while True:
        if number > PRODUCTS_ON_PAGE:
            number = number - PRODUCTS_ON_PAGE
            dict_to_return[page] = PRODUCTS_ON_PAGE
            page += 1
            continue
        dict_to_return[page] = number
        return dict_to_return


def send_telegram_message(number) -> None:
    """Запускает бота по взятым из окружения переменным (Токен, ID чата).
    Посылает сообщение об успехе в указанный чат."""
    TELEGRAM_TOKEN = os.getenv('TG_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TG_CHAT_ID')
    if not all(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID):
        raise ValidationError('Данных для запуска бота недостаточно. Тут '
                              'должна быть кастомная ошибка, но с натягом '
                              'сойдет и такая.')
    bot = telegram.Bot(TELEGRAM_TOKEN)
    bot.send_message(
        TELEGRAM_CHAT_ID,
        ('Задача на парсинг товаров с сайта Ozon завершена.\n'
         f'Сохранено: {number} товаров.')
    )


@celery_app.task
def start_parser(number: int = 10) -> None:
    """Основная функция парсинга.
    Запускает все остальные процессы и сохраняет результаты в базу."""
    if not validate_number(number):
        raise ValidationError('Количество товаров должно быть больше 0 и не'
                              'больше 50')
    suppress_exception(uc)
    display = Xvfb(width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
    display.start()
    # options = uc.ChromeOptions()
    # options.arguments.extend(["--no-sandbox", "--disable-setuid-sandbox"])
    # url_to_chrome = 'http://chrome:3000/webdriver'
    driver = uc.Chrome(driver_executable_path='/app/chromedriver')
    chains = ActionChains(driver)
    waiter = WebDriverWait(driver, DEFAULT_TIMEOUT)
    somedict = calculate_pages_to_parse(number)
    model_objects = []
    for page, items in somedict.items():
        model_objects += parsing(driver, chains, waiter, page, items)
    Product.objects.bulk_create(model_objects)
    send_telegram_message(number)
    display.stop()
