# capa de vista/presentación

from django.shortcuts import redirect, render
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .layers.services import services
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import SubscribeForm
from app.layers.services.services import register_user

import requests # Importa la librería requests para hacer peticiones HTTP

# Vista para la página de inicio (index)
def index_page(request):
    return render(request, 'index.html')

# Esta función obtiene dos listados: uno de las imágenes de la API y otro de favoritos, ambos en formato Card, y los dibuja en el template 'home.html'.
def home(request):
    images = []
    favourite_list = []
    favourite_list_name = []

    images = services.getAllImages() # Obtiene todas las imágenes de Pokémon (probablemente un set por defecto)
    favourite_list = services.getAllFavourites(request) # Obtiene la lista de favoritos del usuario
    for pokemon in favourite_list:
        favourite_list_name.append(pokemon.name) # Guarda solo los nombres de los favoritos
    return render(request, 'home.html', { 'images': images, 'favourite_list_name': favourite_list_name })
        
# Esta función envía un mail al usuario al registrarse
def subscribe(request):
    form = SubscribeForm()
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data
            errores = register_user(form.cleaned_data) # Intenta registrar el usuario

            if errores:
                for error in errores:
                    messages.error(request,error) # Muestra errores si los hay
            else:
                # Si el registro fue exitoso, envía un mail con las credenciales
                username = usuario['username']
                email = usuario['email']
                password = usuario['password']
                subject = 'Registro exitoso'
                message = f'¡Gracias por registrarte {username}!\nEstas son tus credenciales de inicio de sesión:\nUsuario:{username}\nContraseña:{password}'
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)     
    return render(request, 'registration/register.html', {'form': form})

# Función utilizada en el buscador de Pokémon
def search(request):
    query = request.POST.get('query', '').lower().strip() # Obtiene el texto de búsqueda, lo pasa a minúsculas y quita espacios

    images = [] # Lista de resultados de búsqueda
    favourite_list_name = [] # Lista de nombres de favoritos para el contexto del template

    if query: # Si hay texto de búsqueda
        api_url = f"https://pokeapi.co/api/v2/pokemon/{query}/"
        try:
            response = requests.get(api_url) # Hace la petición a la API de PokeAPI
            response.raise_for_status() # Lanza excepción si la respuesta es errónea
            pokemon_data = response.json()

            # Extrae los tipos del Pokémon
            pokemon_types = [t['type']['name'].capitalize() for t in pokemon_data['types']]

            # Extrae los datos necesarios para el template
            pokemon_info = {
                'name': pokemon_data['name'].capitalize(),
                'id': pokemon_data['id'],
                'image': pokemon_data['sprites']['other']['official-artwork']['front_default'],
                'height': pokemon_data['height'],
                'weight': pokemon_data['weight'],
                'base': pokemon_data['base_experience'],
                'types': pokemon_types # Tipos del Pokémon
            }
            images.append(pokemon_info) # Agrega el Pokémon encontrado a la lista

        except requests.exceptions.RequestException as e:
            print(f"Error fetching Pokémon '{query}' from PokeAPI: {e}")
            messages.info(request, f"No se encontró ningún Pokémon con el nombre o ID: '{query}'.")
            # Si hay error, la lista 'images' queda vacía y se muestra mensaje en el template

    # Si el usuario está autenticado, obtiene su lista de favoritos
    if request.user.is_authenticated:
        favourite_list = services.getAllFavourites(request)
        for pokemon in favourite_list:
            favourite_list_name.append(pokemon.name)

    return render(request, 'home.html', { 'images': images, 'favourite_list_name': favourite_list_name })

# Función utilizada para filtrar por el tipo del Pokémon
def filter_by_type(request):
    type = request.POST.get('type', '') # Obtiene el tipo seleccionado

    images = []
    favourite_list_name = [] # Lista de nombres de favoritos para el contexto

    if type != '':
        images = services.filterByType(type) # Trae un listado filtrado de imágenes según el tipo
    
    # Si el usuario está autenticado, obtiene su lista de favoritos
    if request.user.is_authenticated:
        favourite_list = services.getAllFavourites(request)
        for pokemon in favourite_list:
            favourite_list_name.append(pokemon.name)

    return render(request, 'home.html', { 'images': images, 'favourite_list_name': favourite_list_name }) # Devuelve el template con los datos
    
# Estas funciones se usan cuando el usuario está logueado en la aplicación.

# Muestra la lista de favoritos del usuario
@login_required
def getAllFavouritesByUser(request):
    favourite_list = []     
    images = [] # Puede usarse para mostrar detalles de los favoritos
    favourite_list = services.getAllFavourites(request)

    return render(request, 'favourites.html', { 'images': images, 'favourite_list': favourite_list })
    
# Guarda un Pokémon como favorito
@login_required
def saveFavourite(request):
    services.saveFavourite(request)
    return redirect('favoritos')

# Elimina un Pokémon de favoritos
@login_required
def deleteFavourite(request):
    services.deleteFavourite(request)
    return redirect('favoritos')

# Cierra la sesión del usuario
@login_required
def exit(request):
    logout(request)
    return redirect('home')
