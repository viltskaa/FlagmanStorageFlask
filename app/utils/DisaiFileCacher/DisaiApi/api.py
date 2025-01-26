from bs4 import BeautifulSoup as Bf
import requests

from app.utils.DisaiFileCacher.DisaiApi import DisaiRequestAnswer


def disai_api_request(
        search_barcode: str | int,
        *,
        base_url: str = "https://ru.disai.org",
        name_path: str = ".caption h1"
) -> DisaiRequestAnswer | None:
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    data = {"search_query": search_barcode}

    try:
        response = requests.post(base_url, data=data, headers=headers, allow_redirects=True)
        if response.status_code != 200:
            return None

        response.encoding = response.apparent_encoding

        soup = Bf(response.text, features="html.parser")
        art = soup.select(name_path)[0].get_text().split()[0].strip()

        return DisaiRequestAnswer(art, search_barcode)
    except requests.RequestException:
        return None
