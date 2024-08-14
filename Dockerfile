FROM python:3.12.4-slim

WORKDIR /file_service

COPY ./requirements/base.txt /file_service/requirements.txt
RUN pip install --root-user-action=ignore --no-cache-dir --upgrade -r /file_service/requirements.txt

COPY ./src /file_service/src

CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]
