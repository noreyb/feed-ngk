import time
import xml.etree.ElementTree as ET

import feedgenerator
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

if __name__ == "__main__":
    keys = ["recently", "ranking/daily"]
    for key in keys:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(f"https://ascii2d.net/{key}")
            time.sleep(5)
            html = page.content()

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
