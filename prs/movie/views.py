import uuid
import random

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.template import RequestContext
from django.template.context import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

from movie.models import Movies
from movie.models import Genres
from movie.models import UserProfile

from movie.forms import UserForm
from movie.forms import UserProfileForm

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
    genres = Genres.objects.distinct('genre')
    template = get_template('details.html')
    context = RequestContext(request, {
	  'sessionid' : checkSessionId(request),
        'genres' : genres,
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
        'sessionid': checkSessionId(request),
        'user_id': ensureUserId(request),
        'number_of_movies': number_of_movies,
        'movies': movies,
        'genres': genres,
        'genre_name': genre_name,
    })
    return HttpResponse(template.render(context))


def user_login(request):

    if request.method == 'POST': 					#A
        username = request.POST.get('username')			#B
        password = request.POST.get('password')			#B

        user = authenticate(username=username, password=password)#C
        if user:							#D
            if user.is_active:					#E
                login(request, user)				#F
                user_profile = user.profile
                request.session['user_id'] = user_profile.externalUserId #G
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("Your MovieGEEKs account is disabled.")
        else:
            print ("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'login.html', {})       		#H

def user_logout(request):						#C
    logout(request)
    return HttpResponseRedirect('/')


def register(request):

    registered = False

    if request.method == 'POST':

        user_form = UserForm(data=request.POST)				#A
        profile_form = UserProfileForm(data=request.POST)		#B

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()							#C

            profile = profile_form.save(commit=False)
            profile.user = user						#D

            profile.save()							#E

            registered = True

        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                  'register.html',
                  {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})



def ensureUserId(request): 
    if not "user_id" in request.session:
        request.session['user_id'] = random.randint(1000000000000, 9000000000000)    
    
    print("ensured id: ", request.session['user_id'] )    
    return request.session['user_id']
    
def checkSessionId(request):
    if not "session_id" in request.session:
        request.session["session_id"] = str(uuid.uuid1())
        
    return request.session["session_id"]