import time
import xml.etree.ElementTree as ET

import feedgenerator
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

if __name__ == "__main__":
    # Setup selenium
    # service = ChromeService(ChromeDriverManager(version="114.0.5735.90").install())
    service = ChromeService()
    options = Options()
    options.add_argument("--headless")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
    )
    options.binary_location = "/usr/local/bin/chrome-linux64/chrome"

    keys = ["recently", "ranking/daily"]
    for key in keys:
        driver = webdriver.Chrome(
            service=service,
            options=options,
        )

        try:
            # URLを開いて、レンダリングを待ち、ソースを取得する
            url = f"https://ascii2d.net/{key}"
            driver.get(url)
            time.sleep(5)
            html = driver.page_source
            # print(html)

            soup = BeautifulSoup(html, "html.parser")
            headers = soup.find_all(class_="recently_header")
            print(len(list(headers)))
            img_urls = []
            for header in headers:
                img_urls.append(list(header.find_all("a"))[-1]["href"])

            box = soup.find_all(class_="item-box")
            print(len(list(box)))
            thumbnails = []
            titles = []
            for b in box:
                thumbnails.append(b.find("img")["src"])
                titles.append(b.find("img")["alt"])

            print(img_urls)

            # feedgeneratorに入れる
            key = key.replace("/", "-")
            feeds = feedgenerator.Rss201rev2Feed(
                title=f"feed-ngk-{key}",
                link="https://noreyb.github.io/feed-ngk",
                description=f"feed-ngk-{key}",
            )
            for img_url, thumbnail, title in zip(img_urls, thumbnails, titles):
                enclosure = feedgenerator.Enclosure(
                    url=img_url,
                    length="0",
                    mime_type="image/jpeg",
                )

                feeds.add_item(
                    title=title,
                    link=img_url,
                    description=title,
                    enclosure=enclosure,
                )

            # xmlとして出力する
            output_path = f"./output/feed-ngk-{key}.xml"
            with open(output_path, "w") as f:
                f.write(feeds.writeString("utf-8"))

            tree = ET.parse(output_path)
            ET.indent(tree, space="    ")
            tree.write(
                output_path,
                encoding="utf-8",
                xml_declaration=True,
            )
        finally:
            driver.quit()
