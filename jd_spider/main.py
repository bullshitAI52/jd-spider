import yaml
import os
import sys
from factories.spider_factory import SpiderFactory

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if not os.path.exists(config_path):
        print(f"配置文件 {config_path} 不存在！")
        sys.exit(1)
    config = load_config(config_path)
    spider = SpiderFactory.create_spider('jd', config)
    spider.crawl()

if __name__ == '__main__':
    main() 