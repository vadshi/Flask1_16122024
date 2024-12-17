# Flask1_16122024

### Инструкция по развертыванию проекта
1. Создать виртуальное окружение: `python3 -m venv flask_venv`  
2. Активировать виртуальное окружение `source flask_venv/bin/activate`  
3. Установить библиотеки: `pip install -r requirements.txt`  
4. Запуск приложения: `python app.py`


### Работа с sqlite3

1. Установка **CLI** для **sqlite**: `sudo apt install sqlite3`  
2. Создать дамп БД (схема + данные): `sqlite3 store.db .dump > sqlite_examples/storedb_dump.sql`  
3. Создать дамп БД (только схема): `sqlite3 store.db ".schema quotes" > sqlite_examples/storedb_schema.sql`  
4. Загрузить данные в БД: `sqlite3 new_store.db ".read sqlite_examples/storedb_dump.sql"`  


