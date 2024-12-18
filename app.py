from flask import Flask, abort, g, jsonify, request
from typing import Any
from pathlib import Path
from werkzeug.exceptions import HTTPException
# import из SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, func
from sqlalchemy.exc import InvalidRequestError

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from flask_migrate import Migrate


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
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    __tablename__ = 'authors'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(String(32), index=True, unique=True)
    quotes: Mapped[list['QuoteModel']] = relationship(back_populates='author', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, name):
        self.name = name
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
            }


class QuoteModel(db.Model):
    __tablename__ = 'quotes'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[str] = mapped_column(ForeignKey('authors.id'))
    author: Mapped['AuthorModel'] = relationship(back_populates='quotes')
    text: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int] = mapped_column(server_default='1')

    def __init__(self, author, text, rating=1):
        self.author = author
        self.text  = text
        self.rating = rating

    def __repr__(self):
        return f"QuoteModel{self.id, self.author}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text
        }


@app.errorhandler(HTTPException)
def handle_exeption(e):
    """ Функция для перехвата HTTP ошибок и возврата в виде JSON."""
    return jsonify({"error": str(e)}), e.code


@app.route("/authors", methods=["POST"])
def create_author():
    author_data = request.json
    author = AuthorModel(author_data["name"])
    db.session.add(author)
    db.session.commit()
    return author.to_dict(), 201


# URL: /authors/<int:author_id>/quotes
@app.route("/authors/<int:author_id>/quotes", methods=["GET", "POST"])
def get_author_quotes(author_id: int):
    author = db.get_or_404(AuthorModel, author_id)
    
    if request.method == "GET":
        quotes = []
        for quote in author.quotes:
            quotes.append(quote.to_dict())      
        return jsonify(author=author.to_dict() | {"quotes": quotes}), 200
    elif request.method == "POST":
        new_quote = request.json
        q = QuoteModel(author, new_quote["text"])
        db.session.add(q)
        db.session.commit()
        return jsonify(q.to_dict() | {"author_id": author.id}), 201
    else:
        abort(405)


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
    quote = db.get_or_404(QuoteModel, quote_id)
    return jsonify(quote.to_dict()), 200


@app.get("/quotes/count")
def quotes_count():
    """ Function returns count of quotes. """
    count = db.session.scalar(func.count(QuoteModel.id))
    return jsonify(count=count), 200


@app.route("/quotes", methods=['POST'])
def create_quote():
    """ Create a new quote in the database """
    data = request.json
    
    try:
        quote = QuoteModel(**data)
        db.session.add(quote)
        db.session.commit()
    except TypeError:
        return jsonify(error=(
            "Invalid data. Required: author and text. "
            f"Received: {', '.join(data.keys())} "
            )), 400  
    except Exception as e:
        abort(503, f"Database error: {str(e)}")
    
    return jsonify(quote.to_dict()), 201


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id: int):
    """ Update an existing quote """
    new_data = request.json

    allowed_keys = {"author", "text"} # add "rating" a bit later
    if not set(new_data.keys()).issubset(allowed_keys):
        return jsonify(error=f"Invalid fields for update: {', '.join(set(new_data.keys()) - allowed_keys)}"), 400
    
    quote_db = db.get_or_404(QuoteModel, quote_id)
    try:
        for key, value in new_data.items():
            if not hasattr(quote_db, key):
                raise Exception(f"Invalid {key = }.")
            setattr(quote_db, key, value)
        db.session.commit()
        return jsonify(quote_db.to_dict()), 200
    except Exception as e:
        abort(400, f"error: {str(e)}")


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id: int):
    quote = db.get_or_404(QuoteModel, quote_id)
    db.session.delete(quote)
    try:
        db.session.commit()
        return jsonify(success=f"Quote with {quote_id} has deleted."), 200
    except Exception as e:
        db.session.rollback()
        abort(503, f"Database error: {str(e)}")


@app.route("/quotes/filter")
def filter_quotes():
    """ DONE: change to work wit db."""
    data = request.args
    try:
        quotes = db.session.scalars(db.select(QuoteModel).filter_by(**data)).all()
    except InvalidRequestError:
        abort(400, f"Invalid data: {', '.join(data.keys())}.")

    return jsonify([quote.to_dict() for quote in quotes]), 200


if __name__ == "__main__":
    app.run(debug=True)
