import requests
from common import *
from bs4 import BeautifulSoup
from url_handler import Url, Preprocess_url


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
    def snatch_xkcd() -> bytes:
        url: Preprocess_url = Preprocess_url.withUrlType(ComicSnatcher.getUrl('xkcd'), None)
        urlSoup = url.getSoup()
        div = urlSoup.find("div", id="comic")
        divImgUrl = div.img["src"]
        imgUrl = ComicSnatcher.getUrl('xkcd').join(divImgUrl)
        LOG_INFO(f'fetching comic from {imgUrl.get()}')
        result = requests.get(imgUrl.get())
        return result.content
