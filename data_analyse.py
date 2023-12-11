import math
import os
import warnings
import requests
import pandas as pd
import matplotlib.pyplot as plt
from pandas import read_parquet
from sklearn import tree
from sklearn.tree import export_graphviz

warnings.filterwarnings('ignore')


def plot_year_pie(df):
    x = [i for i in range(1920, 2025, 5)]
    y = [0 for i in range(1920, 2025, 5)]
    x_label = ['{}~{}'.format(i, i + 5) for i in x]
    print(x_label)
    values = df.values
    for year in df.keys().values:
        for i in range(len(x)):
            if year in range(x[i], x[i] + 5):
                y[i] += values[i]
    plt.pie(y, labels=x_label, autopct='%.2f%%')
    plt.savefig('./year_pie.png')
    plt.show()


def plot_country_pie(df):
    x = df.values
    x_label = df.keys().values
    plt.pie(x, labels=x_label, autopct='%.2f%%')
    plt.savefig('./country_pie.png')
    plt.show()


def main():
    file_path = "./movie_details/"  # data path
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

    year = df["year"].describe()
    print(year)
    plot_year_pie(df['year'].value_counts())
    plot_country_pie(df['country'].value_counts())

    y = df['rate'].str.slice(0, 3).astype(float)
    X = df.drop(axis=1, columns=['rate'])
    X['Cat'] = X['country'] + X['language'] + X['title'] + X['director'] + X['writer'] + X['star']
    X = X.drop(axis=1,
               columns=['country', 'language', 'title', 'director', 'writer', 'star', 'detail_url', 'duration'])
    from sklearn.feature_extraction.text import CountVectorizer
    text_transformer = CountVectorizer()
    X_cat_enc = pd.DataFrame(text_transformer.fit_transform(X['Cat']).toarray(),
                             columns=text_transformer.get_feature_names_out())
    # print(X_cat_enc)
    X_enc = pd.concat([X[['rank', 'year']], X_cat_enc], axis=1)
    # print(X_cat_enc.shape)
    # print(X_enc.shape)
    # print(X_enc.head())
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X_enc, y, test_size=0.2, random_state=20,
                                                        shuffle=True)
    # print(X_train_tfidf)
    dtr = tree.DecisionTreeRegressor()
    dtr = dtr.fit(X_train, y_train)
    dtr_y_predict = dtr.predict(X_test)
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
    print('R-squared value of DecisionTreeRegressor:', dtr.score(X_test, y_test))
    print('The mean squared error of DecisionTreeRegressor:', mean_squared_error(y_test, dtr_y_predict))
    print('The mean absolute error of DecisionTreeRegressor:', mean_absolute_error(y_test, dtr_y_predict))

    fig = plt.figure(figsize=(25, 20))
    _ = tree.plot_tree(
        dtr,
        feature_names=X_enc.columns.values,
        filled=True
    )
    


if __name__ == '__main__':
    main()
