import re
import asyncio
from curl_cffi.requests import AsyncSession
from lxml import html
from pipline import get_pending_urls
from pipeline_product import insert_product,create_product_table


HEADERS = {
    "user-agent": "Mozilla/5.0"
}

COOKIES = {
    'gr_1_lat': '22.469426',
    'gr_1_lon': '88.37518030000001',
    'gr_1_locality': 'Kolkata',
}


def clean(x):
    return x[0].strip() if x else None


def create_slug(name):
    return name.lower().replace(" ", "-").replace("(", "").replace(")", "")


import random
import asyncio


async def fetch(session, url, retries=3):
    for attempt in range(retries):
        try:
            response = await session.get(
                url,
                headers=HEADERS,
                cookies=COOKIES,
                impersonate="chrome110",
                timeout=30
            )

            return response

        except Exception as e:
            print(f"Retry {attempt+1} Error:", e)

            await asyncio.sleep(random.uniform(2, 5))

    return None


async def process_url(session, url):
    response = await fetch(session, url)

    if not response or response.status_code != 200:
        return

    tree = html.fromstring(response.content)

    # CATEGORY ID (REGEX)
    canonical = clean(tree.xpath("//link[@rel='canonical']/@href"))

    category_id = None
    if canonical:
        match = re.search(r'/cid/(\d+/\d+)', canonical)
        if match:
            category_id = match.group(1)

    # CATEGORY NAME
    category_name = clean(tree.xpath("//h1/text()"))

    # PRODUCTS
    products = tree.xpath("//div[@id='plpContainer']//div[@id]")

    for product in products:

        product_id = product.get("id")

        product_name = clean(
            product.xpath(".//div[contains(@class,'tw-line-clamp-2')]/text()")
        )

        if not product_name:
            continue

        slug = create_slug(product_name)
        product_url = f"https://blinkit.com/prn/{slug}/prid/{product_id}"

        data = {
            "category_id": category_id,
            "category_name": category_name,
            "product_id": product_id,
            "product_name": product_name,
            "product_url": product_url,
            "status": "pending"
        }

        insert_product(data)


async def main():
    urls = get_pending_urls()
    print("TOTAL URLS:", len(urls))

    # limit for safety (avoid blocking)
    semaphore = asyncio.Semaphore(5)

    async with AsyncSession() as session:

        async def sem_task(url):
            async with semaphore:
                await process_url(session, url)
                await asyncio.sleep(1)  # delay to avoid block

        tasks = [sem_task(url) for url in urls]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    create_product_table()
    asyncio.run(main())