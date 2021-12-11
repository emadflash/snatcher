import os
import shutil
from dataclasses import dataclass
from itertools import takewhile
from typing import Generator, List

import requests
from bs4 import BeautifulSoup
from PIL import Image

from common import *
from saver import save_as_file
from url_handler import Preprocess_url, Url


class SnatchAttemptFailed(Exception):
    """raised when we didnt' snatch anything"""


class SnatchFaildPdfCreateError(Exception):
    """raised when we weren't able to create pdf"""


class NewsSnatcher:
    CNN = "https://edition.cnn.com/"

    @staticmethod
    def snatch_cnn() -> str:
        url = Preprocess_url(NewsSnatcher.CNN, None)
        urlSoup = url.getSoup()
        return urlSoup.prettify()


class ComicSnatcher:
    comics = {
        "xkcd": "https://c.xkcd.com/random/comic",
        "ext": "https://existentialcomics.com/comic/random",
    }

    @staticmethod
    def getUrl(comicName) -> Url:
        if comicName not in ComicSnatcher.comics:
            raise AssertionError(f"'{comicName}' invaild key")
        return Url(ComicSnatcher.comics[comicName])


class ComicSnatcherXkcd(ComicSnatcher):
    @staticmethod
    def is_vaild_url(url: Url) -> bool:
        def is_numeric(s: str) -> bool:
            for i in s:
                if not (i >= "0" and i <= "9"):
                    return False
            return True

        parsedUrl = url.getParsed()
        comicIdx = parsedUrl.path.strip("/")
        return bool(
            url.get() == ComicSnatcher.comics["xkcd"]
            or parsedUrl.netloc == "xkcd.com"
            and is_numeric(comicIdx)
        )

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
        imgUrl = ComicSnatcher.getUrl("xkcd").join(divImgUrl)
        LOG_INFO(f"fetching comic from {imgUrl.get()}")
        imgBytes: Response = requests.get(imgUrl.get())
        return imgBytes.content

    @staticmethod
    def snatch_xkcd() -> bytes:
        LOG_INFO(f'Picking random xkcd comic using {ComicSnatcher.comics["xkcd"]}')
        return ComicSnatcherXkcd.snatch_xkcd_from(ComicSnatcher.comics["xkcd"])


@dataclass
class ComicSnatcherXkcdResult:
    comic_name: str
    raw_data: bytes


class ComicSnatcherExt(ComicSnatcher):
    def __init__(
        self, url: str = None, save_in: str = None, is_save_pdf: bool = False
    ) -> None:
        self.is_random: bool = bool(url == None)
        self.is_save_in: bool = bool(url != None)
        self.url: Preprocess_url = (
            Preprocess_url(url, None)
            if not self.is_random
            else Preprocess_url(ComicSnatcher.comics["ext"], None)
        )
        self.save_in: str = save_in
        self.is_save_pdf: bool = is_save_pdf

    @staticmethod
    def is_vaild_url(url: Url) -> bool:
        urlParsed = url.getParsed()
        return bool(urlParsed.netloc == "existentialcomics.com")

    @staticmethod
    def getPngName(url: Url) -> str:
        urlStr = url.get()
        return urlStr[urlStr.rfind("/") + 1 : urlStr.rfind(".")]

    @staticmethod
    def getFolderNameFromUrl(url: Url) -> str:
        return "".join(
            list(takewhile(lambda x: not x.isdigit(), ComicSnatcherExt.getPngName(url)))
        )

    @staticmethod
    def getPdfNameFromStr(url: str) -> str:
        return f"{url}.pdf"

    def snatch(self) -> Generator[ComicSnatcherXkcdResult, None, None]:
        if self.is_random:
            LOG_INFO(
                f'Picking random existential comic using {ComicSnatcher.comics["ext"]}'
            )

        if not self.is_random:
            if not ComicSnatcherExt.is_vaild_url(self.url):
                raise SnatchAttemptFailed(f'invaild url "{self.url.get()}"')

        try:
            urlSoup = self.url.getSoup()
        except Exception as e:
            raise SnatchAttemptFailed(e)

        def getImgByte(imgTip: str) -> ComicSnatcherXkcdResult:
            imgUrl = self.url.page_url.join(imgTip)
            LOG_INFO(f"fetching comic from {imgUrl.get()}")
            imgBytes: Response = requests.get(imgUrl.get())
            return ComicSnatcherXkcdResult(
                ComicSnatcherExt.getPngName(imgUrl), imgBytes.content
            )

        imgs = urlSoup.findAll("img", class_="comicImg")
        imgUrls: List[str] = list(map(lambda x: x["src"], imgs))

        if self.is_save_in:
            assert len(imgUrls) >= 1
            self.save_in = ComicSnatcherExt.getFolderNameFromUrl(Url(imgUrls[0]))
            os.mkdir(self.save_in)

        for imgUrl in imgUrls:
            yield getImgByte(imgUrl)

    def save_as_folder(self) -> List[str]:
        img_loc: str
        img_locs: List[str] = list()

        for res in self.snatch():
            img_loc = f"{self.save_in}/{res.comic_name}.png"
            img_locs.append(img_loc)
            save_as_file(res.raw_data, img_loc)

        return img_locs

    def remove_folder(self) -> None:
        try:
            shutil.rmtree(self.save_in)
            LOG_INFO(f"deleted folder {self.save_in}")
        except OSError:
            panic(f'failded deleting dir "{self.save_in}"')

    @staticmethod
    def remove_file(file: str) -> None:
        try:
            os.remove(file)
            LOG_INFO(f"removed file {file}")
        except OSError:
            panic(f'failded deleting file "{file}"')

    def panic(self, msg: str) -> None:
        self.remove_folder()
        panic(msg)

    def save_as_pdf(self) -> None:
        assert self.is_save_pdf
        img_locs: List[str] = self.save_as_folder()

        assert len(img_locs) >= 1

        try:
            first_img = Image.open(img_locs[0])
            img_list = [Image.open(img) for img in img_locs[1::]]
        except Exception as e:
            raise SnatchFaildPdfCreateError(e)

        pdfName = ComicSnatcherExt.getPdfNameFromStr(self.save_in)
        LOG_INFO(f'writing pdf "{pdfName}"')

        try:
            if len(img_locs) < 2:
                first_img = first_img.convert("RGB")
                first_img.save(pdfName)
            else:
                first_img.save(pdfName, save_all=True, append_images=img_list)
        except Exception as e:
            ComicSnatcherExt.remove_file(pdfName)
            raise SnatchFaildPdfCreateError(e)

        self.remove_folder()

    def save(self) -> None:
        self.save_as_pdf() if self.is_save_pdf else self.save_as_folder()
