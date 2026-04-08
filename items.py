import re
import os
import json
from lxml import html
from curl_cffi import requests
from urllib.parse import urljoin
# import pipeline functions
from pipline import create_table, save_categories


URL = 'https://blinkit.com/categories'
BASE_URL = "https://blinkit.com/"

COOKIES = {
    'gr_1_deviceId': '374f5796-70f8-4ddd-a93f-3a84983d77d3',
    '__cf_bm': '6Vs98sAmeGwSG6KxS9Hw5NZyfhY79DqGgn33.6P8fuo-1775368427-1.0.1.1-DCK6CG2vZILaWeC8n5_WG2EgzkcDct7VKE0OOJcVbHqW679tx7YqcsB6fyxPLZ3jj3Xv8rssc2ytYWO558lObwi3OXWf8e8.eMwEr6cqUHc',
    '_cfuvid': 'RtNJsozKWncTozRQRJlqRUPitHrWmD9vOQJgX2LaZ9Uu-1775368427917-0.0.1.1-604800000',
    'gr_1_lat': '22.469426',
    'gr_1_lon': '88.37518030000001',
    'gr_1_locality': 'Kolkata',
}

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    'sec-ch-ua-platform': '"Windows"',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}


def get_main_categories():
    response = requests.get(URL, headers=HEADERS, cookies=COOKIES, impersonate="chrome110")
    if response.status_code != 200:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return

    tree = html.fromstring(response.content)
    categories_list = []

    # safer xpath
    base_path = tree.xpath("//h2")

    for section in base_path:
        data_info = {
            'name': section.xpath("string(.)").strip(),
            'cate_details': []
        }

        sub_items = section.xpath("./following-sibling::div[1]//a")

        for cat_name in sub_items:
            item_url = cat_name.xpath("string(./@href)")
            # pattern = re.match(r"^/cid/(\d+)/(\d+)$", item_url)
            # categories_id = pattern
            # print(categories_id)

            categories_item = {
                "categories_name": cat_name.xpath("string(.)").strip(),
                "categories_url": urljoin(BASE_URL, item_url)
            }

            data_info['cate_details'].append(categories_item)

        # avoid empty sections
        if data_info['cate_details']:
            categories_list.append(data_info)

    # save json
    data_dir = os.path.join(os.getcwd(), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    file_path = os.path.join(data_dir, "categories.json")

    with open(file_path, "w", encoding='utf-8') as f:
        json.dump(categories_list, f, indent=4)

    print(f"Saved {len(categories_list)} categories")

    # DB operations
    create_table()
    save_categories(categories_list)

    print("Data inserted into database")


if __name__ == '__main__':
    get_main_categories()