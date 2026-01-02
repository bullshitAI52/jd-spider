from ..spiders.jd_spider import JDSpider

class SpiderFactory:
    @staticmethod
    def create_spider(platform: str, config: dict):
        if platform.lower() == 'jd':
            return JDSpider(config)
        else:
            raise ValueError(f"不支持的平台: {platform}") 