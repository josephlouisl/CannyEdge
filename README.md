# Canny edge image detection app 

## Local development:

#### Install

```
pip install -r requirements.txt
```
[Instal rabbit](https://www.digitalocean.com/community/tutorials/how-to-install-and-manage-rabbitmq)

Install memcached

Configurate settings.py
#### Run

```
python app.py
python consumer.py
celery -A tasks worker --loglevel=info
```

## Running with docker-compose:

```
docker-compose up 
```

## Usage:
#### Request:
```
curl -d '{"BUCKET":"{{ S3_BUCKET_NAME }}", "file_path":"{{ IMAGE_PATH }}", "SECRET_ACCESS_KEY": "{{ AWS_SECRET_ACCESS_KEY}}", "ACCESS_KEY_ID": "{{ AWS_ACCESS_KEY_ID }}"}' -H "Content-Type: application/json" -X POST {{ HOST }} 
```
#### Resp:
```javascript
{"task_id": {{ KEY }} } 
```

#### Request:
curl {{ HOST }}/{{ KEY }}

#### Resp:
```javascript
{"task_status": {{ TASK_STATUS }} } 
```
Will create new image in your bucker with name canny + {{ old_image_name }}
