import uuid
import random

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.template import RequestContext
from django.template.context import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from movie.models import Movies
from movie.models import Genres

def index(request): 
    qs = request.GET
    
    movies_list = Movies.objects.order_by('-year')
    number_of_movies = Movies.objects.count()

    genres = Genres.objects.distinct('genre')

    paginator = Paginator(movies_list, 18)
    page = qs.get('page')

    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        movies = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        movies = paginator.page(paginator.num_pages)

    template = get_template('index.html')
    context = RequestContext(request, {
        'sessionid' : checkSessionId(request),
        'user' : request.user,
        'user_id': ensureUserId(request),
        'number_of_movies': number_of_movies,
        'movies': movies,
        'genres' : genres,
    })

    return HttpResponse(template.render(context))

def detail(request, movie_id):
	movie = Movies.objects.get(id= movie_id)
	template = get_template('details.html')

	context = RequestContext(request, {
	  'sessionid' : checkSessionId(request),
        'movie': movie,
        'user': request.user,
        'user_id' : ensureUserId(request),
	})
	return HttpResponse(template.render(context))

def genre(request, genre_name): 

    films_in_genre = Genres.objects.filter(genre=genre_name).values('movieid')
    movies_list = Movies.objects.filter(id__in=films_in_genre)
    number_of_movies = films_in_genre.count()

    genres = Genres.objects.distinct('genre')

    paginator = Paginator(movies_list, 18)
    page = request.GET.get('page')
    
    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        movies = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        movies = paginator.page(paginator.num_pages)

    template = get_template('index.html')
    context = RequestContext(request, {
        'sessionid' : checkSessionId(request),
        'user_id': ensureUserId(request),
        'number_of_movies': number_of_movies,
        'movies': movies,
        'genres' : genres,
        'genre_name' : genre_name,
    })
    return HttpResponse(template.render(context))

def ensureUserId(request): 
    if not "user_id" in request.session:
        request.session['user_id'] = random.randint(1000000000000, 9000000000000)    
    
    print("ensured id: ", request.session['user_id'] )    
    return request.session['user_id']
    
def checkSessionId(request):
    if not "session_id" in request.session:
        request.session["session_id"] = str(uuid.uuid1())
        
    return request.session["session_id"]