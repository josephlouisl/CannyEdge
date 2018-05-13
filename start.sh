#!/bin/bash
if [ $APP == "celery_worker" ]
	then
	celery -A tasks worker --loglevel=info
elif [ $APP == "task_server" ]
	then
	python consumer.py
else
	python app.py
fi
