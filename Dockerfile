FROM python

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./game_director /code/game_director
COPY ./start.sh /code/start.sh

WORKDIR /code

#CMD ["uvicorn", "game_director.webapi.main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]
CMD ["bash", "start.sh"]