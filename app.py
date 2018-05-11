from aiohttp import web
import asyncio
import json

from utils import AWSWrapper, rabbit_pub
import settings

async def handle(request):
    data = await request.json()
    try:
        aws_data = {
                'bucket': data['BUCKET'],
                'key': data['file_path'],
                'AWS_SECRET_ACCESS_KEY': data['SECRET_ACCESS_KEY'],
                'AWS_ACCESS_KEY_ID': data['ACCESS_KEY_ID']
            }
        serialized_data = json.dumps(aws_data)
        await rabbit_pub(app.loop, settings.PRECESS_IMG_QUEUE, serialized_data)
    except KeyError:
        pass
    return web.Response(text="OK \n")


app = web.Application()
app.add_routes([web.post('/', handle),])


web.run_app(app, port=8000)