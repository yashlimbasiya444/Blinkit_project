from curl_cffi import requests
from lxml import html
from pipline import get_pending_urls


COOKIES = {
    'gr_1_lat': '22.469426',
    'gr_1_lon': '88.37518030000001',
    'gr_1_locality': 'Kolkata',
}

HEADERS = {
    'user-agent': 'Mozilla/5.0'
}


def clean(x):
    return x[0].strip() if x else None


def get_image(product):
    paths = [
        ".//img/@src",
        ".//img/@data-src",
        ".//img/@srcset",
    ]

    for p in paths:
        img = product.xpath(p)
        if img:
            val = img[0].strip()
            if " " in val:
                val = val.split(" ")[0]
            if "http" in val:
                return val
    return None


def parse_product():
    urls = get_pending_urls()
    print("TOTAL URLS:", len(urls))

    with requests.Session() as session:
        for url in urls:
            print("\nURL:", url)

            try:
                response = session.get(
                    url,
                    headers=HEADERS,
                    cookies=COOKIES,
                    impersonate="chrome110"
                )

                if response.status_code != 200:
                    continue

                tree = html.fromstring(response.content)

                products = tree.xpath(
                    "//div[contains(@id,'plpContainer')]//div[contains(@class,'tw-flex') and contains(@class,'tw-flex-col')]"
                )

                seen = set()

                for product in products:

                    name = clean(product.xpath(".//div[contains(@class,'tw-line-clamp-2')]/text()"))

                    if not name:
                        continue
                    if name in seen:
                        continue

                    seen.add(name)

                    weight = clean(product.xpath(".//div[contains(@class,'tw-line-clamp-1')]/text()"))

                    # PRICE FIX
                    prices = product.xpath(
                        ".//div[contains(@class,'tw-font-semibold') or contains(@class,'tw-line-through')]//text()"
                    )
                    prices = [p.strip() for p in prices if "₹" in p]

                    discount_price = None
                    original_price = None

                    if len(prices) == 1:
                        discount_price = prices[0]
                    elif len(prices) >= 2:
                        discount_price = prices[0]
                        original_price = prices[1]

                    discount = "".join(
                        product.xpath(".//div[contains(@class,'tw-font-extrabold')]/text()")
                    ).replace("\n", "").strip()

                    image = get_image(product)

                    print("NAME:", name)
                    print("WEIGHT:", weight or "N/A")
                    print("PRICE:", discount_price or "N/A")
                    print("MRP:", original_price or "N/A")
                    print("DISCOUNT:", discount or "N/A")
                    print("IMAGE:", image or "N/A")
                    print("-" * 40)

            except Exception as e:
                print("ERROR:", e)


if __name__ == "__main__":
    parse_product()