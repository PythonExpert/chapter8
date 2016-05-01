import datetime
import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity

import database

def build(ratings):
    print("calculating the similarities.")

    ratings['avg'] = ratings.groupby('userid')['rating'].transform(lambda x: normalize(x))
    print("normalized ratings.")

    rp = ratings.pivot_table(index=['movieid'], columns=['userid'], values='avg')
    print("rating matrix finished")

    cor = rp.transpose().corr(method='pearson', min_periods=25)
    #cor = cosine_similarity(rp.trainspose())
    print('correlation is finished')

    long_format_cor = cor.stack().reset_index(level=0)

    database.save_similarity_from_df(long_format_cor)

    print(long_format_cor.head())

    return cor


def normalize(x):
    if x.std() == 0:
        return 0
    return (x - x.mean()) / x.std()
