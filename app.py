import json

from aiohttp import web
import asyncio

from utils import AWSWrapper, Task, rabbit_pub
import settings

async def task_handler(request):
    data = await request.json()
    try:
        aws_data = {
                'bucket': data['BUCKET'],
                'key': data['file_path'],
                'AWS_SECRET_ACCESS_KEY': data['SECRET_ACCESS_KEY'],
                'AWS_ACCESS_KEY_ID': data['ACCESS_KEY_ID']
            }
        task = Task(app.loop)
        await task.set_status("Pending")
        data = {"aws_data": aws_data, "task_id": task.id}
        serialized_data = json.dumps(data)
        await rabbit_pub(app.loop, settings.PRECESS_IMG_QUEUE, serialized_data)
    except KeyError:
        raise web.HTTPForbidden()
    resp = {"task_id": task.id}
    return web.json_response(resp)


async def task_status_handler(request):
    task_id = request.match_info['id']
    try:
        task = Task(app.loop, task_id)
        status = await task.get_status()
        resp = {"task_status": status}
    except:
        resp = {"task_status": "Not found"}
    return web.json_response(resp)


app = web.Application()
app.add_routes([
    web.post('/', task_handler),
    web.get('/{id}', task_status_handler)
    ])


web.run_app(app, port=8000)