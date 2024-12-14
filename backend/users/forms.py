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
            "username": forms.TextInput(attrs={"placeholder": ""}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Fullname"}),
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
    username = forms.CharField(
        required=True,
        label="Username",
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    full_name = forms.CharField(
        required=False,
        label="Full Name",
        widget=forms.TextInput(attrs={'placeholder': 'Full Name'})
    )

    class Meta:
        model = UserProfile
        fields = [
            'profile_picture', 'bio', 'locale', 'born'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'placeholder': 'Tell us about yourself'}),
            'locale': forms.TextInput(attrs={'placeholder': 'Location'}),
            'born': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # Permitir inicializar o e-mail, username e full_name do usuário
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email
            self.fields['username'].initial = user.username
            self.fields['full_name'].initial = user.get_full_name()  # Use get_full_name se estiver no CustomUser

    def save(self, commit=True):
        # Atualiza o perfil, e-mail, username e full_name do usuário
        instance = super().save(commit=False)
        user = instance.user  # Obtém o usuário relacionado
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        user.full_name = self.cleaned_data['full_name']  # Atualiza o campo full_name
        if commit:
            user.save()
            instance.save()
        return instance


class PostForm(forms.Form):
    # Defina os campos do formulário aqui
    field_name = forms.CharField(max_length=100)
