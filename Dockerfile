FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE 1 
ENV PYTHONUNBUFFERED 1
RUN pip install poetry
WORKDIR /usr/app/
COPY poetry.lock pyproject.toml /usr/app/
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi
ENV PYTHONPATH='/usr/app/'
COPY . /usr/app/
EXPOSE 8000

