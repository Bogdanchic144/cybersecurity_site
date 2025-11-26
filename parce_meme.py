import requests

from random import randint
from bs4 import BeautifulSoup
#from crawlee.playwright_crawler import PlaywrightCrawler

def get_memes():
    links = []
    # crawler = PlaywrightCrawler(
    #     # headless=False
    # )
    # await crawler.run(['https://ru.pinterest.com/lengavriuck/meme/'])
    # await context.page.wait_for_load_state('networkidle')
    # await context.infinite_scroll()
    memes = None
    conn_desc = requests.get("https://ru.pinterest.com/lengavriuck/meme/")
    if conn_desc.status_code == 200:
        html = conn_desc.text
        soup = BeautifulSoup(html, 'lxml')
        memes = soup.find_all('img', class_='hCL', elementtiming="grid-non-story-pin-image-unknown")

    for el in memes:
        meme = el["src"]
        links.append(meme)
    print(len(links))
    return links[randint(0,len(links)-1)]
