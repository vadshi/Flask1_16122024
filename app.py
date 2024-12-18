from flask import Flask, abort, g, jsonify, request
from typing import Any
from pathlib import Path
# import из SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'quotes.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Будет виден каждый запрос к БД в виде SQL
app.config["SQLALCHEMY_ECHO"] = False


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)


class QuoteModel(db.Model):
    __tablename__ = 'quotes'

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(32))
    text: Mapped[str] = mapped_column(String(255))

    def __init__(self, author, text):
        self.author = author
        self.text  = text

    def __repr__(self):
        return f"QuoteModel{self.id, self.author}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "text": self.text
        }


# URL: /quotes
@app.route("/quotes")
def get_quotes() -> list[dict[str: Any]]:
    """ Функция преобразует список словарей в массив объектов JSON."""
    quotes_db = db.session.scalars(db.select(QuoteModel)).all()
    # Формирую список словарей
    quotes = []
    for quote in quotes_db:
        quotes.append(quote.to_dict())
    return jsonify(quotes), 200
   

@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id: int) -> dict:
    """ Retrieve a single quote by ID """
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM quotes WHERE id = ?", (quote_id,)) # tuple with one element
    quote_db = cursor.fetchone()

    if quote_db:
        keys = ("id", "author", "text", "rating")
        quote = dict(zip(keys, quote_db))
        return jsonify(quote), 200
    return {"error": f"Quote with id={quote_id} not found."}, 404


@app.get("/quotes/count")
def quotes_count():
    """ Function returns count of quotes. """
    select_count = "SELECT count(*) as count FROM quotes"
    cursor = get_db().cursor()
    cursor.execute(select_count)
    count = cursor.fetchone()
    if count:
        return jsonify(count=count[0]), 200
    abort(503) # вернем ошибку 503

@app.route("/quotes", methods=['POST'])
def create_quote():
    """ Create a new quote in the database """
    new_quote = request.json
   
    if not new_quote or 'author' not in new_quote or 'text' not in new_quote:
        return jsonify(error="Missing required fields: author and text"), 400
    
    rating = new_quote.get("rating", 1)
    if rating not in range(1, 6):
        rating = 1
    new_quote["rating"] = rating
    insert_quote = "INSERT INTO quotes (author, text, rating) VALUES (?, ?, ?)"
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(insert_quote, tuple(new_quote.values()))
    new_quote_id = cursor.lastrowid
    try:
        connection.commit()
        cursor.close()
    except Exception as e:
        abort(503,f"error: {str(e)}")
    new_quote['id'] = new_quote_id
    return jsonify(new_quote), 201


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id: int):
    """ Update an existing quote """
    new_data = request.json
    
    allowed_keys = {"author", "text", "rating"}
    if not set(new_data.keys()).issubset(allowed_keys):
        return jsonify(error="Invalid fields for update"), 400
 
    if "rating" in new_data and new_data["rating"] not in range(1, 6):
        return jsonify(error="Rating must be between 1 and 5"), 400

    connection = get_db()
    cursor = connection.cursor()

    # Создаем кортеж значений для подстановки и список строк из полей для обновления
    update_values = list(new_data.values())
    update_fields = [f"{key} = ?" for key in new_data]

    if not update_fields:
        return jsonify(error="No valid update fields provided"), 400

    update_values.append(quote_id)
    update_query = f"UPDATE quotes SET {', '.join(update_fields)} WHERE id = ?"
    
    cursor.execute(update_query, update_values)
    connection.commit()
 
    if cursor.rowcount == 0:
        return jsonify(error=f"Quote with id={quote_id} not found"), 404
    
    responce, status_code = get_quote(quote_id)
    if status_code == 200:
        return responce, 200
    abort(404, f"Quote with id={quote_id} not found.") 


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id: int):
    delete_sql = "DELETE FROM quotes WHERE id = ?"
    params = (quote_id,)
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(delete_sql, params)
    rows = cursor.rowcount
    if rows:
        connection.commit()
        return jsonify(message=f"Quote with {quote_id} has deleted."), 200
    abort(404, f"Quote with id={quote_id} not found.")  


# @app.route("/quotes/filter")
# def filter_quotes():
#     """ TODO: change to work wit db."""
#     filtered_quotes = quotes.copy()
#     # request.args хранит данных, полученные из query parameters
#     for key, value in request.args.items():
#         result = []
#         if key not in ("author", 'text', "rating"):
#             return jsonify(error=f"Invalid param={key}"), 400
#         if key == "rating":
#             value = int(value)
#         for quote in filtered_quotes:
#             if quote[key] == value:
#                 result.append(quote)
#         filtered_quotes = result.copy()
#     return jsonify(filtered_quotes), 200


if __name__ == "__main__":
    app.run(debug=True)
