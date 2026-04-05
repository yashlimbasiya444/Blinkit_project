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


def parse_product():
    urls = get_pending_urls()
    print("TOTAL URLS:", len(urls))

    with requests.Session() as session:
        for url in urls:
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

                # Outermost product wrapper (span 2 wala div)
                base_path = tree.xpath(
                    "//div[contains(@id,'plpContainer')]"
                    "//div[@data-pf='reset' and contains(@style,'grid-column: span 2')]"
                    "/div[contains(@class,'tw-relative tw-flex tw-h-full')]"
                )

                for product in base_path:
                    # Name
                    name = product.xpath(".//div[contains(@class,'tw-line-clamp-2')]/text()")

                    # Weight
                    weight = product.xpath(".//div[contains(@class,'tw-line-clamp-1')]/text()")

                    # Discounted price
                    discount_price = product.xpath(
                        ".//div[contains(@class,'tw-font-semibold') and contains(@class,'tw-text-200')]/text()"
                    )

                    # Original price — strip whitespace
                    original_price_parts = product.xpath(
                        ".//div[contains(@class,'tw-line-through')]//span[last()]/text()"
                    )
                    original_price = original_price_parts[0].strip() if original_price_parts else None

                    # Discount badge — "15%\nOFF" → join
                    discount_parts = product.xpath(
                        ".//div[contains(@class,'tw-font-extrabold')]/text()"
                    )
                    discount = "".join(discount_parts).replace("\n", "").strip()

                    # Image — direct child img
                    image = product.xpath(
                        ".//div[contains(@class,'tw-px-2')]//img[contains(@class,'tw-transition-opacity')]/@src"
                    )

                    print("PRODUCT:", name[0].strip() if name else "N/A")
                    print("WEIGHT:", weight[0].strip() if weight else "N/A")
                    print("DISCOUNT PRICE:", discount_price[0].strip() if discount_price else "N/A")
                    print("ORIGINAL PRICE:", original_price if original_price else "N/A")
                    print("DISCOUNT:", discount if discount else "N/A")
                    print("IMAGE:", image[0] if image else "N/A")
                    print("---")

            except Exception as e:
                print("ERROR:", e)


if __name__ == "__main__":
    parse_product()