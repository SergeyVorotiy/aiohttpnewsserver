import datetime
import json

from aiohttp import web

from asyncio import sleep


async def get_handler(request: web.Request):
    response = web.WebSocketResponse(heartbeat=10)
    ws_connection_available = response.can_prepare(request)

    if not ws_connection_available:
        with open('./index.html', 'rb') as template:
            return web.Response(body=template.read(), content_type='text/html')

    await response.prepare(request)

    await response.send_str('Hello, you are subscribed on news!')



    try:
        time = datetime.datetime.now()
        print(f'New subscriber connected.{time}')
        request.app['sockets'].append(response)

        async for message in response:
            if message.type == web.WSMsgType.TEXT:
                for ws_connection in request.app['sockets']:
                    await ws_connection.send_str(message.data)
            elif message.type == web.WSMsgType.PING:
                print(message)
                for ws_connection in request.app['sockets']:
                    await ws_connection.send_str('ping')
            else:
                return response
        return response
    finally:
        request.app['sockets'].remove(response)
        print(f'One of subscribers disconnected {datetime.datetime.now()}')

async def news_handler(request: web.Request):
    # if request.method == 'POST':
    #     request.app['news'].append(request.content)
    #     for ws_connection in request.app['sockets']:
    #         await ws_connection.send_str(request.content[''])
    #     with open('sendNews.html', 'rb') as send:
    #         return web.Response(body=send.read(), status=201, content_type='text/html')
    if request.method == 'GET':
        request.app['news'].append('news')
        for ws_connection in request.app['sockets']:
            await ws_connection.send_str('news')
    with open('sendNews.html', 'rb') as send:
        return web.Response(body=send.read(), status=201, content_type='text/html')


async def on_shutdown(app: web.Application):
    for ws in app['sockets']:
        await ws.close()

def init():
    app = web.Application()
    app['sockets'] = []
    app['news'] = []
    app.router.add_get('/', get_handler)
    app.router.add_get('/POST/news', news_handler)

    app.on_shutdown.append(on_shutdown)
    return app

if __name__ == '__main__':
    web.run_app(init())
