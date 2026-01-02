import time
import yaml
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from ..utils.browser import get_chrome_driver
from ..utils.cookie_manager import CookieManager
from ..utils.data_exporter import DataExporter
from ..models.item import Item
from ..strategies.sort_strategy import ComprehensiveSortStrategy, SalesSortStrategy
from datetime import datetime
import logging
import os

class JDSpider:
    def __init__(self, config):
        self.config = config
        self.driver = get_chrome_driver(config.get('headless', True))
        self.wait = WebDriverWait(self.driver, 15)
        self.items = []
        self.logger = self._init_logger()
        self.exporter = DataExporter
        self.cookie_manager = CookieManager()
        self.output_file = self._get_output_file()
        self.sort_strategy = self._get_sort_strategy()

    def _init_logger(self):
        logger = logging.getLogger('JDSpider')
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(os.path.join(os.path.dirname(__file__), '../logs/spider.log'), encoding='utf-8')
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger

    def _get_output_file(self):
        keyword = self.config['keyword']
        sort = self.config['sort_type']
        fmt = self.config['output_format'].lower()
        dt = datetime.now().strftime('%Y%m%d_%H%M')
        return f"{keyword}_{sort}_{dt}.{fmt}"

    def _get_sort_strategy(self):
        if self.config['sort_type'] == '销量':
            return SalesSortStrategy()
        return ComprehensiveSortStrategy()

    def login_with_cookie(self):
        self.driver.get('https://www.jd.com')
        if not self.cookie_manager.load_cookies(self.driver):
            self.logger.warning('未找到Cookie文件，请手动登录后保存Cookie。')
            input('请手动登录京东后回车继续...')
            self.cookie_manager.save_cookies(self.driver)
        self.driver.refresh()

    def search(self):
        self.driver.get('https://www.jd.com')
        search_box = self.wait.until(EC.presence_of_element_located((By.ID, 'key')))
        search_box.clear()
        search_box.send_keys(self.config['keyword'])
        search_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.button')))
        search_btn.click()

    def crawl(self):
        try:
            if self.config.get('use_cookie'):
                self.login_with_cookie()
            self.search()
            self.sort_strategy.apply_sort(self.driver)
            for page in range(1, self.config['max_pages'] + 1):
                self.logger.info(f"抓取第{page}页...")
                self._parse_page()
                self._export_page()
                if not self._next_page():
                    break
        except Exception as e:
            self.logger.error(f"爬虫运行异常: {e}")
        finally:
            self.driver.quit()

    def _parse_page(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.gl-item')))
            products = self.driver.find_elements(By.CSS_SELECTOR, '.gl-item')
            page_items = []
            for prod in products:
                try:
                    title = prod.find_element(By.CSS_SELECTOR, '.p-name em').text
                except Exception:
                    title = ''
                try:
                    img = prod.find_element(By.CSS_SELECTOR, '.p-img img')
                    image_url = img.get_attribute('src') or img.get_attribute('data-lazy-img') or ''
                except Exception:
                    image_url = ''
                try:
                    price_desc = prod.find_element(By.CSS_SELECTOR, '.p-price').text
                except Exception:
                    price_desc = ''
                try:
                    price = float(''.join(filter(str.isdigit, price_desc.replace('￥','').replace(',','') or '0')))
                except Exception:
                    price = 0.0
                try:
                    comment_text = prod.find_element(By.CSS_SELECTOR, '.p-commit').text
                    comment_count = self._parse_comment_count(comment_text)
                except Exception:
                    comment_count = 0
                try:
                    product_url = prod.find_element(By.CSS_SELECTOR, '.p-name a').get_attribute('href')
                except Exception:
                    product_url = ''
                try:
                    shop_name = prod.find_element(By.CSS_SELECTOR, '.p-shopnum a, .p-shop a').text
                except Exception:
                    shop_name = ''
                try:
                    shop_url = prod.find_element(By.CSS_SELECTOR, '.p-shopnum a, .p-shop a').get_attribute('href')
                except Exception:
                    shop_url = ''
                item = Item(
                    title=title,
                    image_url=image_url,
                    price_desc=price_desc,
                    price=price,
                    comment_count=comment_count,
                    product_url=product_url,
                    shop_name=shop_name,
                    shop_url=shop_url,
                )
                page_items.append(item)
            self.items.extend(page_items)
            self.page_items = page_items
        except TimeoutException:
            self.logger.error('页面加载超时，自动重试...')
            time.sleep(2)
            self._parse_page()
        except Exception as e:
            self.logger.error(f'解析页面异常: {e}')

    def _parse_comment_count(self, text):
        try:
            if '万' in text:
                num = float(text.replace('万','').replace('+','')) * 10000
            else:
                num = int(''.join(filter(str.isdigit, text)))
            return int(num)
        except:
            return 0

    def _export_page(self):
        fmt = self.config['output_format'].lower()
        if fmt == 'csv':
            self.exporter.export_csv(self.page_items, self.output_file)
        else:
            self.exporter.export_xlsx(self.page_items, self.output_file, self.config.get('show_image_in_excel', False))

    def _next_page(self):
        try:
            next_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.pn-next')))
            if 'disabled' in next_btn.get_attribute('class'):
                return False
            next_btn.click()
            time.sleep(2)
            return True
        except Exception:
            self.logger.info('已到最后一页或翻页失败')
            return False 