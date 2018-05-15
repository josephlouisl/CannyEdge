import json

import asyncio
import aio_pika

import settings
from utils import AWSWrapper, Task, wait_for_done, delete_file
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
                task_id = data['task_id']
                task = Task(loop, id=task_id)
                
                await task.set_status('Started downloading')
                try:
                    file_path = await aws_client.get_file(**data['aws_data'])
                except Exception as e:
                    await task.set_status("Download error")
                    raise e
                else:
                    await task.set_status("Started image processing")
                    try:
                        result_future = canny_task.delay(file_path)
                        canny_img_path = await wait_for_done(result_future)
                    except Exception as e:
                        await task.set_status("Processing error")
                        raise e
                    else:
                        delete_file(file_path)
                        data['aws_data']['file_path'] = canny_img_path
                        data['key'] = canny_img_path.split('/')[-1]
                        await task.set_status("Started uploading canny image")
                        try:
                            resp = await aws_client.upload_huge(**data['aws_data'])
                            await task.set_status("Canny edge image uploaded")
                        except Exception as e:
                            await task.set_status("Error uploading")
                            raise e
                        delete_file(canny_img_path)



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()