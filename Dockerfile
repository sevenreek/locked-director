FROM python

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./game_director /code/game_director

WORKDIR /code

CMD ["uvicorn", "game_director.webapi.main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]