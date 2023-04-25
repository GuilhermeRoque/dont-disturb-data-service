FROM python:3.11.3-bullseye
LABEL authors="guilherme"
RUN mkdir /app
WORKDIR /app
COPY ./src .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]