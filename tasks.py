from celery import Celery
import cv2
import numpy as np
from PIL import Image

import settings


app = Celery('tasks', broker='pyamqp://guest@localhost//', backend='rpc://')


@app.task
def canny_task(img_path):
	img = cv2.imread(img_path, 0)
	edges = cv2.Canny(img,100,200)
	print(edges)
	im = Image.fromarray(edges)
	img_name = settings.MEDIA_ROOT + 'canny_' + img_path.split('/')[-1]
	im.save(img_name)
	return img_name
