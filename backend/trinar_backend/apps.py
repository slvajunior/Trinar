# backend/trinar_backend/apps.py
from django.apps import AppConfig
# Ignora a advertência do Flake8 para importações não utilizadas
# flake8: noqa

class TrinarBackendConfig(AppConfig):
    name = 'trinar_backend'

    def ready(self):
        import trinar_backend.signals  # Garante que os sinais sejam carregados
