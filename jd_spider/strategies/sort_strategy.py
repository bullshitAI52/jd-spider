from abc import ABC, abstractmethod

class SortStrategy(ABC):
    @abstractmethod
    def apply_sort(self, driver):
        pass

class ComprehensiveSortStrategy(SortStrategy):
    def apply_sort(self, driver):
        # 默认综合，无需操作
        pass

class SalesSortStrategy(SortStrategy):
    def apply_sort(self, driver):
        # 假设销量排序按钮有data-sort='销量'属性
        try:
            sales_btn = driver.find_element('xpath', "//a[contains(text(),'销量')]" )
            sales_btn.click()
        except Exception as e:
            print(f"销量排序点击失败: {e}") 