from django import forms
from .models import CustomUser


class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password2 = forms.CharField(
        widget=forms.PasswordInput(),
        label="Confirmar Senha")

    class Meta:
        model = CustomUser
        fields = ["username", "full_name", "email", "password", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Apelido"
        self.fields["full_name"].label = "Nome completo"

    def clean_password2(self):
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem.")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Criptografa a senha

        full_name = self.cleaned_data.get("full_name")

        if full_name:
            name_parts = full_name.split(" ", 1)
            user.first_name = name_parts[0]
            user.last_name = " ".join(name_parts[1:])

        if commit:
            user.save()
        return user
