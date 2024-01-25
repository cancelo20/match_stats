FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . ./

ENV API_TOKEN=61f192b92b5e47f7a40b184f7582a67f

ENV TG_TOKEN=6407094126:AAHfOJ99W0NoQEHgr2wjTNJ6NS_rPoJfGCE

ENV TEAMS_URL=https://api.football-data.org/v4/teams

ENV LEAGUES_URL=https://api.football-data.org/v4/competitions

ENV SECRET_KEY=django-insecure-(aoy-m&#kog&%z%fepcu8q_yt8n0vxjd)q2=7j7b5s4r6p)r6&

CMD ["python3", "manage.py", "runbot" ]
