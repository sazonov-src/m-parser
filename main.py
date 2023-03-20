import json
import time
import asyncio
import datetime
from typing import NamedTuple, Optional, List

import telegram

import compare
import pars

class ManagerSettings(NamedTuple):
    pars: List[dict]
    timedelta: dict = {'seconds': 2}
    set_to_db: dict = {'seconds': 20}

timedelta: Optional[datetime.timedelta] = None
future = None
settings: Optional[ManagerSettings] = None

def to_history():
    global settings, future
    now = datetime.datetime.now()
    if not future:
        future = now + timedelta
    remaining_seconds = (future - now).total_seconds()
    if remaining_seconds < 0:
        print('save the data')
        future = now + timedelta

async def main1(data):
    item_dict = await pars.get_items(data)
    print('1')
    manager = compare.compare(item_dict, 'simple_strategy')
    limited = compare.limited(manager, limit=20)
    for r in compare.sorted_by_delta(compare.get_only_sale_prices(limited)):
        # bot = telegram.Bot(token='token')
        # await bot.send_message(chat_id='1000612443', text=str(r))
        print(r)
    to_history()

async def handle_client(reader, writer):
    global settings, timedelta
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            try:
                res = json.loads(data.decode())
                settings = ManagerSettings(**res)
                timedelta = datetime.timedelta(**settings.set_to_db)
                print('value is obtained', settings)
                while True:
                    for pars_data in settings.pars:
                        await main1(pars.Settings(**pars_data))
                    # writer.write(str(some_int).encode())
                    await writer.drain()
                    await asyncio.sleep(datetime.timedelta(**settings.timedelta).seconds)
            except Exception as e:
                writer.write(f'Error: {e}'.encode())
                raise e
    except ConnectionResetError:
        print(f'клієнт розірвар зєднання')
    finally:
        writer.close()

async def main():
    server = await asyncio.start_server(handle_client, 'localhost', 6000)
    async with server:
        await server.serve_forever()

def run():
    asyncio.run(main())


if __name__ == '__main__':

    run()

    # print('Today :', type(today))
    # one_day = datetime.timedelta(days=1)
    # print('One day :', type(one_day))
    # yesterday = today - one_day
    # print('Yesterday:', yesterday)
    # tomorrow = today + one_day
    # print('Tomorrow :', tomorrow)
    # print()
    # res = tomorrow - yesterday
    #
    # print('tomorrow - yesterday:', )
    # print('yesterday - tomorrow:', yesterday - tomorrow)


