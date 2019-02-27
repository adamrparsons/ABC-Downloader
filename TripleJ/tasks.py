from celery import Celery

app = Celery('tasks', backend='db+sqlite:///db.sqlite3', broker='amqp://guest:guest@localhost:5672/')

@app.task
def add(x,y):
    return x + y
