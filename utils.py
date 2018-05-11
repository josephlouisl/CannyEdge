import aiobotocore
import aio_pika

import settings

class AWSWrapper:
    def __init__(self):
        self.session = aiobotocore.get_session()

    async def upload_file(self, file_content, bucket, key, AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID):
        async with self.session.create_client(
                's3',
                region_name='eu-west-3',
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                aws_access_key_id=AWS_ACCESS_KEY_ID) as client:
            resp = await client.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=file_content
                )
            return resp

    async def get_file(self, bucket, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, key):
        async with self.session.create_client(
                's3',
                region_name='eu-west-3',
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                aws_access_key_id=AWS_ACCESS_KEY_ID) as client:
            response = await client.get_object(Bucket=bucket, Key=key)
            async with response['Body'] as stream:
                reading = True
                filename = settings.MEDIA_ROOT + key.split('/')[-1]
                f = open(filename, 'wb')
                while reading:
                    data = await stream.read(1024)
                    if not len(data):
                        reading = False
                    else:
                        f.write(data)
                f.close()


            return filename


async def rabbit_pub(loop, queue, body):
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/", loop=loop)

    async with connection:
        routing_key = queue
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=body.encode()
            ),
            routing_key=routing_key
        )


async def wait_for_done(result):
    while not result.ready():
        await asyncio.sleep(0.25)
    return result.get()