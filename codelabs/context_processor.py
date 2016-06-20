from django.conf import settings
import codelabs.config as config

def configurations(request):
    return {
            'DISCOURSE_FLAG': config.DISCOURSE_FLAG,
            'DISCOURSE_URL' : config.DISCOURSE_URL
            }
