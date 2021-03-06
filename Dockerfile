FROM pytorch/pytorch:1.4-cuda10.1-cudnn7-devel

RUN apt-get update && apt-get install -y \
  libgtk2.0-dev \
  libgl1-mesa-glx

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 80

COPY . /app

CMD ["python", "main.py"]