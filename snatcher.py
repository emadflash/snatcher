import requests
from common import *
from bs4 import BeautifulSoup
from url_handler import Url, Preprocess_url


class SnatchAttemptFailed(Exception):
    """raised when we didnt' snatch anything"""


class NewsSnatcher:
    CNN = "https://edition.cnn.com/"

    @staticmethod
    def snatch_cnn() -> str:
        url = Preprocess_url(NewsSnatcher.CNN, None)
        urlSoup = url.getSoup()
        return urlSoup.prettify()


class ComicSnatcher:
    comics = {
        'xkcd': 'https://c.xkcd.com/random/comic'
    }


    @staticmethod
    def getUrl(comicName) -> Url:
        if (comicName not in ComicSnatcher.comics):
            raise AssertionError(f"'{comicName}' invaild key")
        return Url(ComicSnatcher.comics[comicName])

    @staticmethod
    def is_vaild_url(url: Url) -> bool:
        def is_numeric(s: str) -> bool:
            for i in s:
                if not (i >= '0' and i <= '9'): return False
            return True

        parsedUrl = url.getParsed()
        comicIdx = parsedUrl.path.strip('/')
        return bool(parsedUrl.netloc == 'xkcd.com' and is_numeric(comicIdx))


    @staticmethod
    def snatch_xkcd_from(url: str) -> bytes:
        url: Preprocess_url = Preprocess_url(url, None)
        if not ComicSnatcher.is_vaild_url(url.page_url):
            raise SnatchAttemptFailed(f'invaild url "{url.getUrl()}"')

        try:
            urlSoup = url.getSoup()
        except Exception as e:
            raise SnatchAttemptFailed(e)

        div = urlSoup.find("div", id="comic")
        divImgUrl = div.img["src"]
        imgUrl = ComicSnatcher.getUrl('xkcd').join(divImgUrl)
        LOG_INFO(f'fetching comic from {imgUrl.get()}')
        result = requests.get(imgUrl.get())
        return result.content


    @staticmethod
    def snatch_xkcd() -> bytes:
        LOG_INFO(f'Picking random xkcd comic using {ComicSnatcher.comics["xkcd"]}')
        return ComicSnatcher.snatch_xkcd_from(ComicSnatcher.comics['xkcd'])
