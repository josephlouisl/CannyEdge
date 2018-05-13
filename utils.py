import aiobotocore
import aio_pika
import asyncio

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

    async def upload_huge(self, bucket, key, AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, file_path):
        async with self.session.create_client(
                's3',
                region_name='eu-west-3',
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                aws_access_key_id=AWS_ACCESS_KEY_ID) as client:
            data = await client.create_multipart_upload(Bucket=bucket, Key=key)
            upload_id = data['UploadId']
            f = open(file_path, 'rb')
            parts_generator = self.read_in_chunks(f, chunk_size=5*1024*1024)
            part_counter = 1
            part_info = {"Parts": []}
            for part in parts_generator:
                part_upload = await client.upload_part(
                    Bucket=bucket,
                    Key=key,
                    PartNumber=part_counter,
                    UploadId=upload_id,
                    Body=part
                    )
                part_info['Parts'].append({
                            'PartNumber': part_counter,
                            'ETag': part_upload['ETag']
                        })
                part_counter += 1
            resp = await client.complete_multipart_upload(
                            Bucket=bucket,
                            Key=key,
                            UploadId=upload_id,
                            MultipartUpload=part_info
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

    @staticmethod
    def read_in_chunks(file_object, chunk_size=1024):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k."""
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data


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
    while result.ready():
        await asyncio.sleep(0.25)
    return result.get()