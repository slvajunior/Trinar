from django import template
import re
from django.utils.safestring import mark_safe
from django.urls import reverse

register = template.Library()


@register.filter
def hashtagize(text):
    """
    Transforma palavras iniciadas com '#' em links para a página de hashtag.
    """
    hashtag_pattern = r'(?P<hashtag>#\w+)'

    def replace(match):
        hashtag = match.group('hashtag')[1:]  # Remove o símbolo '#'
        url = reverse('home:hashtag_search', kwargs={'hashtag': hashtag})
        return f'<a href="{url}" class="hashtag">{match.group("hashtag")}</a>'

    return mark_safe(re.sub(hashtag_pattern, replace, text))


@register.filter
def mentionize(value):
    """
    Substitui as menções (@usuário) por links para o perfil do usuário.
    """
    mention_pattern = r'@(\w+)'  # Regex para encontrar @username
    value = re.sub(mention_pattern, r'<a href="/users/profile/\1">@\1</a>', value)
    return mark_safe(value)  # Retorna como HTML seguro
