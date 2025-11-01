from lazyscraper import Request, LinksExtractor, export_duckdb
from selectolax.parser import HTMLParser 
from time import sleep 


def parser(request, response, list_: list) -> None:
    
    def parse_title(elements):
        for e in elements:
            if e.attributes.get('title'):
                break 
        return e.attributes.get('title')

    html_parser = HTMLParser(response.text)
    category= html_parser.css_first("h1").text()
    books= html_parser.css_first("ol.row")
    for book in books.iter():
        title= parse_title(book.css("a"))
        price= book.css_first("p.price_color").text()
        availability= book.css_first("p.instock.availability").text()
        list_.append({
            "title": title,
            "category": category,
            "price": float(price.replace("£","")),
        })
    sleep(5)
    print(list_)
    if html_parser.css_first("ul.pager") and html_parser.css_first("ul.pager").css_first("a").text() == "next":
        url_list = request.url.split('/')[:-1]
        url_list.append(html_parser.css_first("ul.pager").css_first("a").attributes.get("href"))
        request.url = "/".join(url_list)
        response = request.get()
        parser(request, response, list_)

    
def iter_links(links: list[str], request: Request) -> list[dict]:
    data=[]
    for link in links:
        url= f"https://books.toscrape.com/{link}" 
        request.url= url 
        response= request.get()
        parser(request, response, data)
    return data
    

def main():
    req = Request(URL= "https://books.toscrape.com/", headers= None, params= None, proxies= None, cookies= None, impersonate= "chrome")
    res = req.get()

    links_parser = LinksExtractor(res)
    links = links_parser.parse_element("div.side_categories")[1:]
    sleep(2)
    data = iter_links(links, req)

    export_duckdb(data= data, file_name= "library.ddb", table_name= "books")

if __name__ == "__main__":
    main()
