import os
import requests
from typing import List, Generator
from dataclasses import dataclass
from common import *
from bs4 import BeautifulSoup
from url_handler import Url, Preprocess_url
from saver import save_as_file
from itertools import takewhile


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
        'xkcd': 'https://c.xkcd.com/random/comic',
        'ext': 'https://existentialcomics.com/comic/random'
    }


    @staticmethod
    def getUrl(comicName) -> Url:
        if (comicName not in ComicSnatcher.comics):
            raise AssertionError(f"'{comicName}' invaild key")
        return Url(ComicSnatcher.comics[comicName])


class ComicSnatcherXkcd(ComicSnatcher):
    @staticmethod
    def is_vaild_url(url: Url) -> bool:
        def is_numeric(s: str) -> bool:
            for i in s:
                if not (i >= '0' and i <= '9'): return False
            return True

        parsedUrl = url.getParsed()
        comicIdx = parsedUrl.path.strip('/')
        return bool(url.get() == ComicSnatcher.comics['xkcd'] or parsedUrl.netloc == 'xkcd.com' and is_numeric(comicIdx))


    @staticmethod
    def snatch_xkcd_from(url: str) -> bytes:
        url: Preprocess_url = Preprocess_url(url, None)
        if not ComicSnatcherXkcd.is_vaild_url(url.page_url):
            raise SnatchAttemptFailed(f'invaild url "{url.getUrl()}"')

        try:
            urlSoup = url.getSoup()
        except Exception as e:
            raise SnatchAttemptFailed(e)

        div = urlSoup.find("div", id="comic")
        divImgUrl = div.img["src"]
        imgUrl = ComicSnatcher.getUrl('xkcd').join(divImgUrl)
        LOG_INFO(f'fetching comic from {imgUrl.get()}')
        imgBytes: Response = requests.get(imgUrl.get())
        return imgBytes.content


    @staticmethod
    def snatch_xkcd() -> bytes:
        LOG_INFO(f'Picking random xkcd comic using {ComicSnatcher.comics["xkcd"]}')
        return ComicSnatcherXkcd.snatch_xkcd_from(ComicSnatcher.comics['xkcd'])



@dataclass
class ComicSnatcherXkcdResult:
    comic_name: str
    raw_data: bytes


class ComicSnatcherExt(ComicSnatcher):
    def __init__(self, url: str = None, save_in: str = None) -> None:
        self.is_random: bool = bool(url == None)
        self.is_save_in: bool = bool(url == None)
        self.url: Preprocess_url = Preprocess_url(url, None) if not self.is_random else Preprocess_url(ComicSnatcher.comics['ext'], None)
        self.save_in = save_in
    
    @staticmethod
    def getPngName(url: Url) -> str:
        urlStr = url.get()
        return urlStr[urlStr.rfind('/') + 1: urlStr.rfind('.')]

    @staticmethod
    def getFolderNameFromUrl(url: Url) -> str:
        return ''.join(list(takewhile(lambda x: not x.isdigit(), ComicSnatcherExt.getPngName(url))))


    def snatch(self) -> Generator[ComicSnatcherXkcdResult, None, None]:
        if self.is_random:
            LOG_INFO(f'Picking random existential comic using {ComicSnatcher.comics["ext"]}')

        try:
            urlSoup = self.url.getSoup()
        except Exception as e:
            raise SnatchAttemptFailed(e)

        def getImgByte(imgTip: str) -> ComicSnatcherXkcdResult:
            imgUrl = self.url.page_url.join(imgTip)
            LOG_INFO(f'fetching comic from {imgUrl.get()}')
            imgBytes: Response = requests.get(imgUrl.get())
            return ComicSnatcherXkcdResult(ComicSnatcherExt.getPngName(imgUrl), imgBytes.content)


        imgs = urlSoup.findAll("img", class_="comicImg")
        imgUrls: List[str] = list(map(lambda x: x['src'], imgs))

        if self.is_save_in:
            assert(len(imgUrls) >= 1)
            self.save_in = ComicSnatcherExt.getFolderNameFromUrl(Url(imgUrls[0]))
            os.mkdir(self.save_in)

        for imgUrl in imgUrls:
            yield getImgByte(imgUrl)

    def save_as_folder(self) -> None:
        for res in self.snatch():
            save_as_file(res.raw_data, f'{self.save_in}/{res.comic_name}.png')
