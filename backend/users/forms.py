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
