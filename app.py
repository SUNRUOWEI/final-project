import os
from operator import itemgetter

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from collections import Counter
import pandas as pd
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.preprocessing import OneHotEncoder
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict


app = Flask(__name__)
bootstrap = Bootstrap(app)


def read_data():
    file_path = r"movie_details"  # data path
    data_source = os.listdir(file_path)
    movies = []
    for path in data_source:
        import json
        with open(os.path.join(file_path, path), 'r') as f:
            data = json.load(f)
            data['rank'] = int(data['rank'])
            movies.append(data)
    movies = sorted(movies, key=itemgetter('rank'))
    return movies

def tree_data():

    movies = read_data()
    tree = defaultdict(list)
    for movie in movies:
        tree[movie['year']].append(movie)
    return tree


def predict(value):
    file_path = r"movie_details"  # data path
    data_source = os.listdir(file_path)
    df = pd.DataFrame()
    for path in data_source:
        import json
        with open(os.path.join(file_path, path), 'r') as f:
            data = json.load(f)
            df1 = pd.DataFrame.from_dict(data, orient='index').T
            df = pd.concat([df, df1])
    df = df.reset_index()

    df['rank'] = df['rank'].astype(int)
    df['year'] = df['year'].astype(int)

    y = df['rate'].str.slice(0, 3).astype(float)
    X = df.drop(axis=1, columns=['rate'])
    X['Cat'] = X['country'] + X['language'] + X['title'] + X['director'] + X['writer'] + X['star']
    X = X.drop(axis=1,
               columns=['country', 'language', 'title', 'director', 'writer', 'star', 'detail_url', 'duration', 'rank'])
    from sklearn.feature_extraction.text import CountVectorizer
    text_transformer = CountVectorizer()
    X_cat_enc = pd.DataFrame(text_transformer.fit_transform(X['Cat']).toarray(),
                             columns=text_transformer.get_feature_names_out())
    X_enc = pd.concat([X['year'], X_cat_enc], axis=1)
    dtr = tree.DecisionTreeRegressor(random_state=400, max_depth=100)
    dtr = dtr.fit(X_enc, y)

    test_cat_enc = pd.DataFrame(text_transformer.transform(value['Cat']).toarray(),
                             columns=text_transformer.get_feature_names_out())
    test_enc = pd.concat([value['year'], test_cat_enc], axis=1)
    dtr_y_predict = dtr.predict(test_enc)

    fig = plt.figure(figsize=(25, 20))
    _ = tree.plot_tree(
        dtr,
        feature_names=X_enc.columns.values,
        filled=True
    )
    # Save picture
    fig.savefig(r"static/images/decistion_tree.png")
    return dtr_y_predict


@app.route('/')
def index():
    movies = read_data()
    print(movies)
    return render_template('index.html', movies=movies)


@app.route('/pie')
def pie():
    return render_template('pie.html')


@app.route('/analyse')
def analyse():
    return render_template('analyses.html')


@app.route('/result', methods=["POST"])
def result():

    title = request.form['title']
    year = request.form['year']
    language = request.form['language']
    country = request.form['country']
    director = request.form['director']
    writer = request.form['writer']
    star = request.form['star']

    # Call query function
    search_movies = find_movies(title, year, language, country, director, writer, star)
    results = []
    for movie in search_movies:
        cat = movie['country'] + movie['language'] + movie['title'] + \
              movie['director'] + movie['writer'] + movie['star']
        new_data = {'year': movie['year'], 'Cat': cat}
        new_data_df = pd.DataFrame([new_data])
        prediction = predict(new_data_df)
        results.append((movie['title'], prediction))

    for movie in search_movies:
        # Find predictions that match the current movie title
        prediction = next((pred for title, pred in results if title == movie['title']), None)
        # Add the prediction to the movie dictionary
        movie['prediction'] = prediction
        # Order the predicted results from largest to smallest
    sorted_movies = sorted(search_movies, key=lambda x: x['prediction'], reverse=True)
    return render_template('result.html', movies=sorted_movies)

def find_movies(title, year, language, country, director, writer, star):
    filtered_movies = []
    all_movies = read_data()
    for movie in all_movies:
        if (not title or title.lower() in movie['title'].lower()) and \
           (not year or year == movie['year']) and \
           (not language or language.lower() in movie['language'].lower()) and \
           (not country or country.lower() in movie['country'].lower()) and \
           (not director or director.lower() in movie['director'].lower()) and \
           (not writer or writer.lower() in movie['writer'].lower()) and \
           (not star or star.lower() in movie['star'].lower()):
            filtered_movies.append(movie)
    return filtered_movies



if __name__ == '__main__':
    app.run(debug=True)
