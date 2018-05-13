import json

import asyncio
import aio_pika

import settings
from utils import AWSWrapper, wait_for_done, delete_file
from tasks import canny_task


async def main(loop):
    connection = await aio_pika.connect_robust(
        settings.RABBITMQ_HOST, loop=loop
    )

    queue_name = settings.PRECESS_IMG_QUEUE

    async with connection:
        # Creating channel
        channel = await connection.channel()

        # Declaring queue
        queue = await channel.declare_queue(
            queue_name, auto_delete=True
        )

        async for message in queue:
            with message.process():
                data = json.loads(message.body.decode('utf-8'))
                aws_client = AWSWrapper()
                file_path = await aws_client.get_file(**data)
                result_future = canny_task.delay(file_path)
                canny_img_path = await wait_for_done(result_future)
                delete_file(file_path)
                data['file_path'] = canny_img_path
                data['key'] = canny_img_path.split('/')[-1]
                resp = await aws_client.upload_huge(**data)
                delete_file(canny_img_path)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()