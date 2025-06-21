# capa de vista/presentación

from django.shortcuts import redirect, render
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .layers.services import services
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .forms import SubscribeForm
from app.layers.services.services import register_user

def index_page(request):
    return render(request, 'index.html')

# esta función obtiene 2 listados: uno de las imágenes de la API y otro de favoritos, ambos en formato Card, y los dibuja en el template 'home.html'.
def home(request):
    images = []
    favourite_list = []
    favourite_list_name = []

    images = services.getAllImages()
    favourite_list = services.getAllFavourites(request)
    for pokemon in favourite_list:
        favourite_list_name.append(pokemon.name)
    return render(request, 'home.html', { 'images': images, 'favourite_list_name': favourite_list_name })
       
# esta funcion envía un mail al usuario al registrarse

def subscribe(request):
    form = SubscribeForm()
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data
            errores = register_user(form.cleaned_data)

            if errores:
                for error in errores:
                    messages.error(request,error)
            else:
                username = usuario['username']
                email = usuario['email']
                password = usuario['password']
                subject = 'Registro exitoso'
                message = f'¡Gracias por registrarte {username}!\nEstas son tus credenciales de inicio de sesión:\nUsuario:{username}\nContraseña:{password}'
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
                return redirect('home')           
    return render(request, 'registration/register.html', {'form': form})

    
# función utilizada en el buscador.
def search(request):
    name = request.POST.get('query', '')

    # si el usuario ingresó algo en el buscador, se deben filtrar las imágenes por dicho ingreso.
    if (name != ''):
        images = services.filterByCharacter(name)
        favourite_list = []

        return render(request, 'home.html', { 'images': images, 'favourite_list': favourite_list })
    else:
        return redirect('home')

# función utilizada para filtrar por el tipo del Pokemon
def filter_by_type(request):
    type = request.POST.get('type', '')

    if type != '':
        images = services.filterByType(type) # debe traer un listado filtrado de imágenes, segun si es o contiene ese tipo.
        favourite_list = []

        return render(request, 'home.html', { 'images': images, 'favourite_list': favourite_list })
    else:
        return redirect('home')

# Estas funciones se usan cuando el usuario está logueado en la aplicación.
@login_required
def getAllFavouritesByUser(request):
    favourite_list = []    
    images = []
    favourite_list = services.getAllFavourites(request)


    return render(request, 'favourites.html', { 'images': images, 'favourite_list': favourite_list })
     

@login_required
def saveFavourite(request):
    services.saveFavourite(request)
    return redirect('favoritos')

@login_required
def deleteFavourite(request):
    services.deleteFavourite(request)
    return redirect('favoritos')

@login_required
def exit(request):
    logout(request)
    return redirect('home')
