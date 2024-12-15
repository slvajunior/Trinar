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
