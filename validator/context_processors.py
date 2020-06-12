from django.conf import settings

## inject this into every django template so that it can always be used.
def globals_processor(request):
    return {
        'admin_mail': settings.EMAIL_FROM.replace('@', ' (at) '),
        'doi_prefix': settings.DOI_URL_PREFIX
        }