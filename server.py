import numpy
import easyocr

# imports for env kafka redis
from dotenv import load_dotenv
from kafka import KafkaProducer
from kafka import KafkaConsumer
from json import loads
import base64
import json
import os
import redis

load_dotenv()


KAFKA_HOSTNAME = os.getenv("KAFKA_HOSTNAME")
KAFKA_PORT = os.getenv("KAFKA_PORT")
REDIS_HOSTNAME = os.getenv("REDIS_HOSTNAME")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

RECEIVE_TOPIC = 'EASY_OCR'
SEND_TOPIC_FULL = "IMAGE_RESULTS"
SEND_TOPIC_TEXT = "TEXT"


print(f"kafka : {KAFKA_HOSTNAME}:{KAFKA_PORT}")

# Redis initialize
r = redis.StrictRedis(host=REDIS_HOSTNAME, port=REDIS_PORT,
                      password=REDIS_PASSWORD, ssl=True)

# Kafka initialize - To receive img data to process
consumer_easyocr = KafkaConsumer(
    RECEIVE_TOPIC,
    bootstrap_servers=[f"{KAFKA_HOSTNAME}:{KAFKA_PORT}"],
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="my-group",
    value_deserializer=lambda x: loads(x.decode("utf-8")),
)

# Kafka initialize - For Sending processed img data further
producer = KafkaProducer(
    bootstrap_servers=[f"{KAFKA_HOSTNAME}:{KAFKA_PORT}"],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)


def recognize(img):
    reader = easyocr.Reader(['en'])
    predictions = reader.readtext(img)
    return predictions


def convert(o):
    if isinstance(o, numpy.int64):
        return int(o)
    raise TypeError


for message in consumer_easyocr:
    print('xxx--- inside easyocr consumer---xxx')
    print(f"kafka - - : {KAFKA_HOSTNAME}:{KAFKA_PORT}")

    message = message.value
    image_id = message['image_id']
    data = message['data']

    # Setting image-id to topic name(container name), so we can know which image it's currently processing
    r.set(RECEIVE_TOPIC, image_id)

    data = base64.b64decode(data.encode("ascii"))

    predictions = recognize(data)

    full_res = {
        'image_id': image_id
    }

    text_res = {
        'image_id': image_id
    }

    text = []
    coords = []
    for idx, prediction in enumerate(predictions):
        cords, word, confidence = prediction
        text.append(word)
        coords.append(cords)

    full_res["data"] = {"text": text, "coords": coords}
    text_res["data"] = {"text": text}
    print(text_res)

    # sending full and text res(without cordinates or probability) to kafka
    producer.send(SEND_TOPIC_FULL, value=json.dumps(full_res, default=convert))
    producer.send(SEND_TOPIC_TEXT, value=json.dumps(text_res, default=convert))

    producer.flush()
