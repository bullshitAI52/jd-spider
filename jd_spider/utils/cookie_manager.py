import pickle
import os
from selenium.webdriver.remote.webdriver import WebDriver

class CookieManager:
    _instance = None
    _cookie_file = 'cookies.pkl'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def save_cookies(self, driver: WebDriver, path: str = None):
        path = path or self._cookie_file
        with open(path, 'wb') as file:
            pickle.dump(driver.get_cookies(), file)

    def load_cookies(self, driver: WebDriver, path: str = None):
        path = path or self._cookie_file
        if not os.path.exists(path):
            return False
        with open(path, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        return True 