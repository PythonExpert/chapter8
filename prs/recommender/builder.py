import pandas as pd

from recommender.models import Ratings, CF_Similarity
from recommender import similarity
from django.db import connection
import datetime


class Builder:

    @staticmethod
    def generate_implicit_ratings(userdata):

        w_buys = 10
        w_moredetails = 2
        w_details = 10
        w_0 = 1

        movie_ratings = []
        maxrating = 0
        for movie in userdata:
            rating = w_buys * movie["buys"] + w_moredetails * movie["moredetails"] + w_details * movie["details"] + w_0
            if rating > maxrating:
                maxrating = rating
            movie_ratings.append({"id": movie["content_id"], "title": movie["title"], "rating": rating})

        for movie_rating in movie_ratings:
            movie_rating["rating"] /= maxrating
            movie_rating["rating"] *= 5

        return movie_ratings


    @staticmethod
    def save_ratings(userid, movie_ratings):

        print("saving ", len(movie_ratings))

        db_rating_objs = []
        for rating in movie_ratings:
            today = datetime.datetime.now()

            r = Ratings( \
                userid=userid, \
                movieid=rating["id"], \
                rating=rating["rating"], \
                date_day=today.day, \
                date_month=today.month, \
                date_year=today.year, \
                date_hour=today.hour, \
                date_minute=today.minute, \
                date_second=today.second, \
                type='implicit')
            print("saved ", r.userid, " ", r.movieid, " ", r.rating)

            db_rating_objs.append(r)

        Ratings.objects.bulk_create(db_rating_objs)

    @staticmethod
    def build_similarity_model(ratings_array):
        ratings = pd.DataFrame(ratings_array)
        similarity_dict = dict()

        for item in set(ratings["id"].tolist()):

            users = Ratings.objects.filter(movieid=item).values('userid')

            #todo: get ratings for these users.

            similarity_dict[item] = dict()
            for user in users:
                user_items = list(Ratings.objects.filter(userid=user['userid']))
                print("user_items", user, " \n",user_items)
                if item in user_items:
                    user_items.remove(item)
                for user_item in user_items:
                    print("similarity calculated between %s %s" %(item, user_item.movieid))
                    sim = similarity.cosine(ratings, item, user_item.movieid)
                    print("similarity calculated between %s %s to be %s" %( item, user_item['movieid'], sim))
                    similarity_dict[item][user_item] = sim
            print(item, " : ", similarity_dict[item])

        Builder.save_similarity_model(similarity_dict)
        return similarity_dict

    @staticmethod
    def save_similarity_model(model):
        #sim = CF_Similarity.objects.latest('created')
        print("%s similarities to be saved" % len(model))
        print(model)
        db_sim_objs = []
        for sim in model.items():
            print(sim)
            for item in sim[1]:
                i = CF_Similarity( \
                    source = sim[0],\
                    target = item[0], \
                    similarity = item[1], \
                    version = 1\
                )
                db_sim_objs.append(i)
        CF_Similarity.objects.bulk_create(db_sim_objs)
        print("similarities %s saved" % len(db_sim_objs))