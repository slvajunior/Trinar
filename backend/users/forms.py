from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        min_length=8,
        required=True,
        label="Password"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(), required=True, label="Confirm Password"
    )
    profile_picture = forms.ImageField(
        required=False,  # Tornando a imagem de perfil não obrigatória
        widget=forms.ClearableFileInput(attrs={"multiple": False}),
        label="Profile Picture",
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name"]  # Usando 'first_name'
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Full Name"}),
        }

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise ValidationError("Passwords do not match!")
        return password_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        # Criar o UserProfile com o novo usuário
        user_profile = UserProfile.objects.create(user=user)

        # Salvar a foto de perfil, se fornecida
        if self.cleaned_data.get("profile_picture"):
            user_profile.profile_picture = self.cleaned_data["profile_picture"]
            user_profile.save()

        return user


class UserProfileEditForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        label="E-mail",
        widget=forms.EmailInput(attrs={'placeholder': 'E-mail'})
    )

    class Meta:
        model = UserProfile
        fields = [
            'profile_picture', 'full_name', 'bio', 'locale', 'born'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Tell us about yourself'}),
            'locale': forms.TextInput(attrs={'placeholder': 'Location'}),
            'born': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # Permitir inicializar o e-mail do usuário
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        # Atualiza o perfil e o e-mail do usuário
        instance = super().save(commit=False)
        user = instance.user  # Obtém o usuário relacionado
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            instance.save()
        return instance


class PostForm(forms.Form):
    # Defina os campos do formulário aqui
    field_name = forms.CharField(max_length=100)
