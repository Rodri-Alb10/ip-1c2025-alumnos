from django import forms

class SubscribeForm(forms.Form):
    username = forms.CharField(label="Nombre de usuario")
    name = forms.CharField(label="Nombre")
    surname = forms.CharField(label="Apellido")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    email = forms.EmailField(label="Correo electrónico")
