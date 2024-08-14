# Тестовое задание на позицию Middle Backend разработчик (Python)

Описание тестового задания в [TASK.md](./TASK.md)

# Запуск
1. Создать .env
```bash
cp .env_example .env
```
2. Запустить сервис
   - Через Docker
        ```bach
        sudo docker-compose up
        ```
        > В docker-copmose прописано ```network_mode: host```, чтобы был доступ к локальной бд
    - Вручную
      1. Установить [Python 3.12](https://www.python.org/downloads/)
      2. Создать среду окружения
      ```bash
      python -m venv .venv && . .venv/bin/activate
      ```
      3. Установить базовые зависимости
      ```bash
      pip install -r requirements/base.txt
      ```
      4. Поднять сервис
      ```bash
      fastapi run src/main.py
      ```
3. Создать таблицу в базе данных
- Docker
```bash
docker exec -it <container_id> python src/database.py
```
- Вручную
```bash
python src/database.py
```
1. Перейти в [swagger](http://localhost:8000/docs#/)
# Тесты
Написаны базовые тесты проверки работоспособности методов.

Запуск:
1. Установить dev зависимости
```bash
pip install -r requirements/dev.txt
```
2. Поменять данные в .env на тестовые
3. Запустить тесты
```bash
pytest
```
# CRON зачистки файлов
Проверка скрипта:
```bash
python src/cron_clean.py
```
Крон задача в cron_clean, докер - DockerfileCron