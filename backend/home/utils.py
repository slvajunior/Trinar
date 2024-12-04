# home/utils.py

from django.utils import timezone
from datetime import timedelta


def time_diff_in_words(created_at):
    now = timezone.now()
    diff = now - created_at  # Calcula a diferença de tempo

    # Se a diferença for menor que 60 segundos, consideramos "agora"
    if diff < timedelta(seconds=60):
        return "Postado agora"

    # Se a diferença for menor que 1 minuto, mostramos "há 1m"
    elif diff < timedelta(minutes=1):
        return f"Postado há {int(diff.total_seconds() // 60)}m"

    # Se a diferença for menor que 1 hora, mostramos "há Xm"
    elif diff < timedelta(hours=1):
        return f"Postado há {int(diff.total_seconds() // 60)}m"

    # Se a diferença for menor que 24 horas, mostramos "há Xh"
    elif diff < timedelta(days=1):
        return f"Postado há {int(diff.total_seconds() // 3600)}h"

    # Se a diferença for maior que 24h, mostramos em dias
    else:
        return f"Postado há {int(diff.total_seconds() // 86400)}d"
