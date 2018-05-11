import asyncio
import aio_pika
import json

import settings
from utils import AWSWrapper, wait_for_done
from tasks import canny_task


async def main(loop):
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/", loop=loop
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



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()