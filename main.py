from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from forms import EditForm, AddForm
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# create database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

MOVIE_DB_API_KEY = "cd2a90e6ccc15c449305ba2ece6881b8"
MOVIE_DB_SEARCH_BY_MOVIE_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_SEARCH_BY_ID_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


# CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=False, unique=True)
    rating = db.Column(db.FLOAT, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(1000), nullable=False)


db.create_all()
# # create new movie
# new_movie = Movie(
#         title="Phone Booth",
#         year=2002,
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an " \
#                     "extortionist's sniper rifle. Unable to leave or receive outside help, " \
#                     "Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         review="My favourite character was the caller.",
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#     )
#
# # add and commit new movie to database.
# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    ordered_movies = Movie.query.order_by(Movie.rating.desc()).all()
    for index in range(len(ordered_movies)):
        ordered_movies[index].ranking = index + 1
    db.session.commit()
    print(ordered_movies)
    # all_movies = Movie.query.all()
    # print(all_movies)
    return render_template("index.html", movies=ordered_movies)


@app.route('/edit', methods=["GET", "POST"])
def edit():
    # # my code 👇
    # if request.method == "POST":
    #     movie_id = request.args.get("movie_id")
    #     updated_rating = request.form["change_rating"]
    #     updated_review = request.form["change_review"]
    #     print(f"movie id is {movie_id},"
    #           f"new rating is {updated_rating}, "
    #           f"new review is {updated_review}.")
    #     movie_in_db = Movie.query.get(movie_id)
    #     print(f"movie is {movie_in_db}.")
    #     movie_in_db.rating = float(updated_rating)
    #     movie_in_db.review = updated_review
    #     db.session.commit()
    #     print("updated!")
    #     return redirect(url_for("home"))
    # form = EditForm()
    # movie_id = request.args.get("movie_id")
    # movie = Movie.query.get(movie_id)
    # return render_template("edit.html", form=form, movie=movie)
    # my code 👆

    # angela's code👇
    movie_id = request.args.get("movie_id")
    movie = Movie.query.get(movie_id)
    form = EditForm()
    if form.validate_on_submit():
        updated_rating = form.change_rating.data
        updated_review = form.change_review.data
        movie.rating = float(updated_rating)
        movie.review = updated_review
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get("movie_id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    add_form = AddForm()
    if add_form.validate_on_submit():
        movie_title = add_form.movie_title.data
        url = MOVIE_DB_SEARCH_BY_MOVIE_URL
        params = {
            "api_key": MOVIE_DB_API_KEY,
            "language": "zh-CN",
            "query": movie_title,
            # "page": "1"
        }
        all_movie = requests.get(url=url, params=params).json()["results"]
        print(all_movie)
        return render_template("select.html", all_movie=all_movie)

    return render_template("add.html", form=add_form)


@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("movie_id")
    if movie_api_id:
        parameter = {
            "api_key": MOVIE_DB_API_KEY,
            "language": "zh-CN",
        }
        chosen_movie = requests.get(url=f"{MOVIE_DB_SEARCH_BY_ID_URL}/{movie_api_id}", params=parameter).json()
        title = chosen_movie["original_title"]
        img_url = MOVIE_DB_IMAGE_URL + chosen_movie["poster_path"]
        year = chosen_movie["release_date"].split("-")[0]
        description = chosen_movie["overview"]
        # create new movie
        new_movie = Movie(
            title=title,
            year=year,
            description=description,
            # rating=0,
            # ranking=0,
            # review="",
            img_url=img_url,
        )

        # add and commit new movie to database.
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit", movie_id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
