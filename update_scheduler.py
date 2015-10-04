from pymongo import MongoClient

import aiohttp
import asyncio

db = MongoClient().ailas

MASTER_SERVER_URL = '40.115.53.131/api/get_hint/'


@asyncio.coroutine
def update_session(loop, url, session_id, client_url):
    ms_client = aiohttp.ClientSession(loop=loop)
    u_clietnt = aiohttp.ClientSession(loop=loop)
    async with ms_client.get(MASTER_SERVER_URL+str(session_id)) as get_response,
               u_client.post(client_url) as post_response:
        data = yield from get_response.read()
        yield from post_response.write(data)


@asyncio.coroutine
def schedule_update(loop, update_period=15.0):
    end_time = loop.time() + update_period
    while True:
        if (loop.time() + 1.0) >= end_time:
            end_time += update_period
            for session in db.sessions.find():
                for url in session['addrs']:
                    yield from update_session(loop=loop,
                                               session_id=session['id'],
                                               client_url=url)
        yield from asyncio.sleep(1)


def main():
    loop = asyncio.get_event_loop()
    loop.run_forever(schedule_update(loop=loop))


if __name__ == '__main__':
    main()
