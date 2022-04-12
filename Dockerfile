FROM python:3.8.10
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y libsndfile1-dev
RUN apt-get -y install ffmpeg
COPY . .
EXPOSE 8000


CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80" ]