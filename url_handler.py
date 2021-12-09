import urllib
from urllib.request import urlopen
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Optional


class Url:
    def __init__(self, url) -> None:
        self.url = url
        
    def join(self, toJoin: str):
        return Url(urljoin(self.url, toJoin))

    def get(self) -> str:
        return self.url

    def getParsed(self):
        return urlparse(self.url)

    def __eq__(self, other) -> bool:
        return self.url == other.url


class Preprocess_url:
    def __init__(self, base_url: str, endpoint: Optional[str]) -> None:
        self.base_url: Url = Url(base_url)
        self.endpoint: str  = endpoint

        self.page_url: Url
        if endpoint == None:
            self.page_url = self.base_url
        else:
            self.page_url = self.base_url.join(self.endpoint)

    @classmethod
    def withUrlType(cls, base_url: Url, endpoint: Optional[str]):
        return cls(base_url.get(), endpoint)

    def getUrl(self) -> str:
        return self.page_url.get()
    
    def getParsed(self):
        return self.page_url.getParsed()

    def getPageSource(self) -> str:
        try:
            urlRequest = urlopen(self.page_url.get())
            return urlRequest.read()
        except urllib.error.HTTPError as e:
            raise e

    def getSoup(self) -> str:
        return BeautifulSoup(self.getPageSource(), 'html.parser')
