import csv
import os
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage
from datetime import datetime
from typing import List
from ..models.item import Item

class DataExporter:
    @staticmethod
    def export_csv(items: List[Item], filename: str):
        fieldnames = [
            '商品标题', '商品图片', '价格描述', '价格', '评论数', '商品链接', '店铺名称', '店铺链接', '抓取时间戳'
        ]
        with open(filename, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if f.tell() == 0:
                writer.writeheader()
            for item in items:
                writer.writerow({
                    '商品标题': item.title,
                    '商品图片': item.image_url,
                    '价格描述': item.price_desc,
                    '价格': item.price,
                    '评论数': item.comment_count,
                    '商品链接': item.product_url,
                    '店铺名称': item.shop_name,
                    '店铺链接': item.shop_url,
                    '抓取时间戳': item.crawl_time.strftime('%Y-%m-%d %H:%M:%S') if item.crawl_time else ''
                })

    @staticmethod
    def export_xlsx(items: List[Item], filename: str, show_image: bool = False):
        fieldnames = [
            '商品标题', '商品图片', '价格描述', '价格', '评论数', '商品链接', '店铺名称', '店铺链接', '抓取时间戳'
        ]
        if os.path.exists(filename):
            wb = load_workbook(filename)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(fieldnames)
        for item in items:
            row = [
                item.title,
                f'=IMAGE("{item.image_url}")' if show_image else item.image_url,
                item.price_desc,
                item.price,
                item.comment_count,
                item.product_url,
                item.shop_name,
                item.shop_url,
                item.crawl_time.strftime('%Y-%m-%d %H:%M:%S') if item.crawl_time else ''
            ]
            ws.append(row)
        wb.save(filename) 