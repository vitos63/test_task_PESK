FROM python:3.12.5
ENV PYTHONUNBUFFERED=1
WORKDIR /src
ENV PYTHONPATH=/src/src
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .