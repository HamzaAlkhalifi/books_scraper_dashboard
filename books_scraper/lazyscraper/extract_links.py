from selectolax.parser import HTMLParser 
from curl_cffi.requests import Response

class LinksExtractor:
    def __init__(self, response: Response ):
        self.response = response.text

    def parse_element(self, element) -> list:
        parser = HTMLParser(self.response)

        href = [node.attributes.get("href")
            for node in parser.css(element + " a")
            if node.attributes.get("href")]

        return href
    
    def parse(self) -> list:
        parser = HTMLParser(self.response)

        href = [node.attributes.get("href") 
            for node in parser.css("a")
            if node.attributes.get("href")]

        return href 
