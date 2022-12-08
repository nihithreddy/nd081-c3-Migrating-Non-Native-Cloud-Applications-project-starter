import os
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy 
from azure.servicebus import QueueClient
import redis


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

app.secret_key = app.config.get('SECRET_KEY')

queue_client = QueueClient.from_connection_string(app.config.get('SERVICE_BUS_CONNECTION_STRING'),
                                                 app.config.get('SERVICE_BUS_QUEUE_NAME'))

db = SQLAlchemy(app)

#Connect to the azure redis for cache instance on pprt 6380
redis_connection = redis.StrictRedis(host=app.config.get('REDIS_HOST'),port=6380,db=0,password=app.config.get('REDIS_PASSWORD'),ssl=True,decode_responses=True)

from . import routes