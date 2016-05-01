import math
import numpy as np
import pandas as pd

import operator
from decimal import *
import timeit
from django.db import connection
from recommender.models import CF_Similarity
from recommender.models import Ratings

from django.db.models import Q
from django.db.models import Count
from django.db.models import Avg

from utils import OrmHelper


class Predictor:
    def __init__(self, userid):
        print("starting prediction.")
        self.userid = userid
        self.ratings = dict()
        self.avg_ratings = dict()
        self.ratings = dict()
        self.predicted_items = dict()

    def find_candidate_users(self, items2, k=2):
        # Find users that that share at least on rated item
        print("Items in find_candidate_user ", items2)

        active_user_ratings = self.get_ratings(self.userid)
        items = set(rating.movieid for rating in active_user_ratings)

        candidate_users = Ratings.objects.filter(movieid__in=items2)\
            .values('userid')\
            .annotate(overlapping=Count('movieid')).order_by('-overlapping')[:k]

        return candidate_users

    def find_usable_ratings(self, candidate_users):

        usable_ratings = Ratings.objects.filter(Q(userid__in=candidate_users.values('userid')))
        return usable_ratings

    def get_ratings(self, user):
        if user in self.ratings:
            return self.ratings[user]
        else:
            self.ratings[user] = Ratings.objects.filter(userid=user)
        return self.ratings[user]

    def get_avg_rating(self, user):
        ratings = self.get_ratings(user)

        if user in self.avg_ratings:
            return self.avg_ratings[user]
        else:
            self.avg_ratings[user] = ratings.aggregate(avg=Avg('rating'))['avg']

        print(self.avg_ratings[user])

        return Decimal(self.avg_ratings[user])

    def item_collaborative_filtering(self, number):
        active_user_items = self.get_ratings(self.userid)

        uis = [i.movieid for i in active_user_items]
        candidate_items = list(CF_Similarity.objects.filter(Q(source__in=active_user_items.values('movieid')))
                               .distinct()
                               .order_by('-similarity')[:number*5])

        prediction = dict()

        for item in candidate_items:
            target = item.target

            if target not in uis:
                pre = 0
                count = 0
                rated_items = dict([(i.source, i) for i in candidate_items if i.target == target])

                for aui in active_user_items:
                    movieid = aui.movieid.strip()
                    if movieid in rated_items:
                        sim = rated_items[movieid].similarity
                        pre += aui.rating * sim
                        count += 1

                prediction[target] = pre / count
        return prediction

    def average_ratings(self):  # A
        users = set(self.ratings["userid"])  # B
        average_ratings = dict()  # C

        for user in users:
            user_ratings = self.ratings[self.ratings["userid"] == user]  # D
            ra = user_ratings["rating"]
            average_ratings[user] = np.array(ra).mean()  # E

        return average_ratings

    def normalize_ratings(self):
        user_average = self.avg_ratings
        for user in user_average.keys():
            self.ratings.loc[:, 'normalized_rating'] = self.ratings.loc[:, 'rating'] \
                                                       - self.avg_ratings[user]

    def user_collaborative_filtering(self, number, k=2):

        active_user_ratings = self.get_ratings(self.userid)
        items = set(rating.movieid for rating in active_user_ratings)

        print("items: ", items)
        candidate_users = self.find_candidate_users(items, k)
        usable_ratings = self.find_usable_ratings(candidate_users)

        similarities = dict()

        for user in candidate_users:
            userid = user['userid'].strip()

            if self.userid != userid:
                print("users userid ", userid, ".")
                similarities[userid] = similarity.pearson(usable_ratings, self.userid, userid)

        predictedratings = dict()
        num_predicitons = 0

        print(len(usable_ratings))

        for item in usable_ratings.values("movieid").distinct():
            if not (item['movieid'] in items):
                movieid = item['movieid'].strip()
                pred = self.user_cf_prediction(usable_ratings, movieid, similarities)
                predictedratings[movieid] = pred
                num_predicitons += 1

        sorted_predictions = sorted(predictedratings.items(), key=operator.itemgetter(1), reverse=True)

        return sorted_predictions[:number]

    def user_cf_prediction(self, usable_ratings, movieid, similarities):

        # print("user collaborative filtering prediction user ", self.userid, " and ", movieid, ".")

        active_user_avg_ratings = Decimal(self.get_avg_rating(self.userid))

        dividend = Decimal(0)  # C
        divisor = Decimal(0)  # C

        for n in set(x['userid'].strip() for x in usable_ratings.filter(movieid=movieid).values('userid')):  # D

            userid = n
            sim = Decimal(similarities[userid])  # E
            rn_avg = self.get_avg_rating(userid)  # F
            r_ratings = self.get_ratings(userid)
            rn_item = Decimal(r_ratings.filter(movieid=movieid).values('rating')[0]['rating'])

            dividend += Decimal(sim * (rn_item - Decimal(rn_avg)))  # H
            divisor += Decimal(math.fabs(sim))  # I

        self.predicted_items[movieid] = (active_user_avg_ratings + dividend / divisor)
        return active_user_avg_ratings + dividend / divisor  # J
