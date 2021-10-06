import sys
import time
import logging
import requests
import aiohttp
import asyncio

# Get an instance of a logger
logger = logging.getLogger('pokemons_crawler')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)




BASE_URL ='https://pokeapi.co/api/v2/pokemon'


def get_pagineted_urls(base_url: str):
    limit = 200
    offset = 0

    logger.info('Geting pagined urls started')
    response = requests.get(base_url)

    if response.status_code != 200:
        logger.error('Getting paginated failed')
        return None

    total_items = response.json()['count']
    total_urls = round(response.json()['count'] / limit)
    last_limit = total_items - ((total_items // limit) * limit)

    for url in range(total_urls):
        if url != (total_urls - 1):
            yield f'{base_url}?limit={limit}&offset={offset}'
            offset += limit
        else:
            yield f'{base_url}?limit={last_limit}&offset={offset}'


async def get_details_urls(client, url):
    logger.info(f'Geting pokemon details urls from {url} started')
    response = await client.request(method='GET', url=url)
    response.raise_for_status()
    response_json = await response.json()
    urls = []
    for result in response_json['results']:
        urls.append(result['url'])
    return urls


async def get_details(client, url):
    logger.info(f'Geting pokemon details from {url}')
    response = await client.request(method='GET', url=url)
    response.raise_for_status()
    response_json = await response.json()
    detail = {
       'id': response_json['id'],
       'name': response_json['name'],
       'characteristics': {
           'stats': response_json['stats'],
           'abilities': response_json['abilities'],
           'height': response_json['height'],
           'weight': response_json['weight']
       }
    }
    return detail

async def run_crawler():
    async with aiohttp.ClientSession() as client:
        logger.info('Pokemon crawler started')
        start_time = time.time()
        detail_urls = await asyncio.gather(*[get_details_urls(client, url) for url in get_pagineted_urls(BASE_URL)])
        pokemon_list = await asyncio.gather(*[get_details(client, url) for urls in detail_urls for url in urls])
        end_time = time.time()
        logger.info(f'Pokemon crawler finished: {len(pokemon_list)} pokemon crawled in {(end_time - start_time)} seconds')
        return pokemon_list


def get_pokemons():
    return asyncio.run(run_crawler())

if __name__ == '__main__':
    get_pokemons()
