# capa de servicio/lógica de negocio

from ..transport import transport
from ...config import config
from ..persistence import repositories
from ..utilities import translator
from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.contrib import messages

# función que devuelve un listado de cards. Cada card representa una imagen de la API de Pokemon
def getAllImages():
    # debe ejecutar los siguientes pasos:
    # 1) traer un listado de imágenes crudas desde la API (ver transport.py)
    # 2) convertir cada img. en una card.
    # 3) añadirlas a un nuevo listado que, finalmente, se retornará con todas las card encontradas.
    
    json_collection = transport.getAllImages()

    cards = []
    
    for pokemon in json_collection:
        card = translator.fromRequestIntoCard(pokemon)
        cards.append(card)


    return cards

# función que filtra según el nombre del pokemon.
def filterByCharacter(name):
    filtered_cards = []

    for card in getAllImages():
        # debe verificar si el name está contenido en el nombre de la card, antes de agregarlo al listado de filtered_cards.
        if name.lower() in card.name.lower():
            filtered_cards.append(card)

    return filtered_cards

# función que filtra las cards según su tipo.
def filterByType(type_filter):
    filtered_cards = []

    for card in getAllImages():
        for type in card.types:
            if type_filter in type.lower():
                filtered_cards.append(card)

    return filtered_cards

# añadir favoritos (usado desde el template 'home.html')
def saveFavourite(request):
    fav = translator.fromTemplateIntoCard(request) # transformamos un request en una Card (ver translator.py)

    fav.user = request.user # le asignamos el usuario correspondiente.

    return repositories.save_favourite(fav) # lo guardamos en la BD.

# usados desde el template 'favourites.html'
def getAllFavourites(request):
    if not request.user.is_authenticated:
        return []
    else:
        user = get_user(request)

        favourite_list = repositories.get_all_favourites(user) # buscamos desde el repositories.py TODOS Los favoritos del usuario (variable 'user').
        
        mapped_favourites = []

        for pokemon in favourite_list:
            card = translator.fromRepositoryIntoCard(pokemon)
            mapped_favourites.append(card)
        return mapped_favourites

def deleteFavourite(request):
    favId = request.POST.get('id')
    return repositories.delete_favourite(favId) # borramos un favorito por su ID

#obtenemos de TYPE_ID_MAP el id correspondiente a un tipo segun su nombre
def get_type_icon_url_by_name(type_name):
    type_id = config.TYPE_ID_MAP.get(type_name.lower())
    if not type_id:
        return None
    return transport.get_type_icon_url_by_id(type_id)

#verifica nombre de usuario y email y se crea un nuevo usuario en la base de datos 
def register_user(usuario):
    username = usuario['username']
    email = usuario['email']
    password = usuario['password']
    name = usuario['name']
    surname = usuario['surname']

    errores = []
                               
    if User.objects.filter(username = usuario['username']).exists():
        errores.append("Ese nombre de usuario ya esta en uso.")
            
    if User.objects.filter(email = usuario['email']).exists():
        errores.append("Esa dirección de correo electrónico ya está asociada a otra cuenta.")

    if errores:
        return errores
    

    User.objects.create_user(
        username = username,
        email = email,
        password = password,
        first_name = name,
        last_name = surname,
    )     

    return []
def get_type_icon_url_by_name(type_name):
    type_id = config.TYPE_ID_MAP.get(type_name.lower())
    if not type_id:
        return None
    return transport.get_type_icon_url_by_id(type_id)
