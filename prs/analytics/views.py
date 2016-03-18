from django.db.models import Count
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.loader import get_template
from django.template.context import RequestContext
from django.db import connection

from recommender.builder import Builder

from .models import Event
from datetime import datetime
import time
import json


def dashboard(request):
    template = get_template('dashboard.html')

    return HttpResponse(template.render())


def user(request, userid):
    context = RequestContext(request, {
        'user': userid,
    })
    template = get_template('user.html')

    return HttpResponse(template.render(context))


def top_content(request):
    cursor = connection.cursor()
    cursor.execute('SELECT \
                        content_id,\
                        mov.title,\
                        count(*) as sold\
                    FROM    public."evidenceCollector_log" log\
                    JOIN    public.movies mov ON CAST(log.content_id AS INTEGER) = CAST(mov.id AS INTEGER)\
                    WHERE 	event like \'buy\' \
                    GROUP BY content_id, mov.title \
                    ORDER BY sold desc \
                    LIMIT 10 \
        ')

    data = dictfetchall(cursor)
    return JsonResponse(data, safe=False)


def get_user_statistics(request, userid):

    date_timestamp = time.strptime(request.GET["date"], "%Y-%m-%d")

    end_date = datetime.fromtimestamp(time.mktime(date_timestamp))
    start_date = monthdelta(end_date, -1)

    sessions_with_conversions = Event.objects.filter(created__range=(start_date, end_date), event='buy', user_id=userid) \
        .values('sessionId').distinct()
    buy_data = Event.objects.filter(created__range=(start_date, end_date), event='buy', user_id=userid) \
        .values('event', 'user_id', 'content_id', 'sessionId')
    sessions = Event.objects.filter(created__range=(start_date, end_date), user_id=userid) \
        .values('sessionId').distinct()

    if (len(sessions) == 0):
        conversions = 0
    else:
        conversions = (len(sessions_with_conversions) / len(sessions)) * 100
        conversions = round(conversions)

    return JsonResponse(
        {"items_bought": len(buy_data),
         "conversions": conversions,
         "sessions": len(sessions)})


def get_statistics(request):
    date_timestamp = time.strptime(request.GET["date"], "%Y-%m-%d")

    end_date = datetime.fromtimestamp(time.mktime(date_timestamp))

    start_date = monthdelta(end_date, -1)

    print("getting statics for ", start_date, " and ", end_date)

    sessions_with_conversions = Event.objects.filter(created__range=(start_date, end_date), event='buy') \
        .values('sessionId').distinct()
    buy_data = Event.objects.filter(created__range=(start_date, end_date), event='buy') \
        .values('event', 'user_id', 'content_id', 'sessionId')
    visitors = Event.objects.filter(created__range=(start_date, end_date)) \
        .values('user_id').distinct()
    sessions = Event.objects.filter(created__range=(start_date, end_date)) \
        .values('sessionId').distinct()

    if (len(sessions) == 0):
        conversions = 0
    else:
        conversions = (len(sessions_with_conversions) / len(sessions)) * 100
        conversions = round(conversions)

    return JsonResponse(
        {"items_sold": len(buy_data),
         "conversions": conversions,
         "visitors": len(visitors),
         "sessions": len(sessions)});


def events_on_conversions(request):
    cursor = connection.cursor()
    cursor.execute('select \
                                (case when c.conversion = 1 then \'buy\' else \'no buy\' end) as conversion,\
                                event,\
                                count(*) as count_items\
                              FROM \
                                    public."evidenceCollector_log" log\
                              LEFT JOIN \
                                (SELECT "sessionId", 1 as conversion \
                                 FROM   public."evidenceCollector_log" \
                                 WHERE  event=\'buy\') c \
                                 ON     log."sessionId" = c."sessionId" \
                               GROUP BY conversion, event')
    data = dictfetchall(cursor)
    print(data)
    return JsonResponse(data, safe=False)


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]

def user_evidence(request, userid):

    cursor = connection.cursor()
    cursor.execute('SELECT \
                        user_id, \
                        content_id,\
                        mov.title,\
                        count(case when event = \'buy\' then 1 end) as buys,\
                        count(case when event = \'details\' then 1 end) as details,\
                        count(case when event = \'moredetails\' then 1 end) as moredetails\
                    FROM \
                      public."evidenceCollector_log" log\
                    JOIN    public.movies mov \
                    ON CAST(log.content_id AS VARCHAR(50)) = CAST(mov.id AS VARCHAR(50))\
                    WHERE\
                        user_id = \'%s\'\
                    group by log.user_id, log.content_id, mov.title\
                    order by log.user_id, log.content_id' % userid)
    data = dictfetchall(cursor)
    movie_ratings = Builder.generate_implicit_ratings(data)
    Builder.save_ratings(userid, movie_ratings)
    Builder.build_similarity_model(movie_ratings)

    return JsonResponse(movie_ratings, safe=False)

class movie_rating():
    title = ""
    rating = 0

    def __init__(self, title, rating):
        self.title = title
        self.rating = rating


def top_content_by_eventtype(request):
    event_type = request.GET.get_template('eventtype', 'buy')

    data = Event.objects.filter(event=event_type) \
               .values('content_id') \
               .annotate(count_items=Count('user_id')) \
               .order_by('-count_items')[:10]
    return JsonResponse(list(data), safe=False)


def monthdelta(date, delta):
    m, y = (date.month + delta) % 12, date.year + ((date.month) + delta - 1) // 12
    if not m: m = 12
    d = min(date.day, [31,
                       29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date.replace(day=d, month=m, year=y)
