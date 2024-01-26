FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . ./

CMD ["python3", "manage.py", "runbot" ]
