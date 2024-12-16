from flask import Flask, jsonify
from typing import Any


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

about_me = {
   "name": "Вадим",
   "surname": "Шиховцов",
   "email": "vshihovcov@specialist.ru"
}


quotes = [
   {
       "id": 3,
       "author": "Rick Cook",
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с \
        большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. \
        Пока вселенная побеждает."
   },
   {
       "id": 5,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
   },
   {
       "id": 6,
       "author": "Mosher's Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
   },
   {
       "id": 8,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так."
   },

]


@app.route("/") # Это первый URL, который мы будем обрабатывать
def hello_world():  # Это функция-обработчик, которая будет вызвана для обработки URL'a
    return jsonify(hello="Hello, World!"), 200


@app.route("/about")
def about():
    return jsonify(about_me), 200


# URL: /quotes
@app.route("/quotes")
def get_quotes() -> list[dict[str: Any]]:
    """ Функция преобразует список словарей в массив объектов JSON."""
    return jsonify(quotes), 200
   

@app.route("/params/<value>")
def params_example(value):
    """ Пример динамического URL'a."""
    return jsonify(param=value, value_type=str(type(value))), 200

# /quotes/1
# /quotes/2
# ...
# /quotes/n-1
# /quotes/n
@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id: int) -> dict:
    """ Функция возвращает цитату по значению ключа id=quote_id. """
    for quote in quotes:
        if quote["id"] == quote_id:
            return jsonify(quote), 200
    return {"error": f"Quote with id={quote_id} not found."}, 404



if __name__ == "__main__":
    app.run(debug=True)
