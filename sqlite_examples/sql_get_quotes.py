# coding: utf-8
import sqlite3

select_quotes = "SELECT * from quotes"
# Подключение в БД
connection = sqlite3.connect("store.db")
# Создаем cursor, он позволяет делать SQL-запросы
cursor = connection.cursor()
# Выполняем запрос:
cursor.execute(select_quotes)

# Извлекаем результаты запроса
quotes = cursor.fetchall()
print(f"{quotes=}")

# Закрыть курсор:
cursor.close()
# Закрыть соединение:
connection.close()
