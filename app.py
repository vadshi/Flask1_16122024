from flask import Flask, jsonify


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

about_me = {
   "name": "Вадим",
   "surname": "Шиховцов",
   "email": "vshihovcov@specialist.ru"
}


@app.route("/") # Это первый URL, который мы будем обрабатывать
def hello_world():  # Это функция-обработчик, которая будет вызвана для обработки URL'a
   return jsonify(hello="Hello, World!"), 200


@app.route("/about")
def about():
   return jsonify(about_me), 200


if __name__ == "__main__":
   app.run(debug=True)
