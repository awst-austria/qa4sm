from django.shortcuts import redirect
from django.conf import settings

from valentina.settings_conf import SITE_URL

angular_paths = [
    {'path': 'home', 'name': 'home'},
    {'path': 'login', 'name': 'login'},
    {'path': 'validate', 'name': 'validate'},
    {'path': 'validation-result/:validationId', 'name': 'result'},
    {'path': 'my-validations', 'name': 'validations'},
    {'path': 'user-profile', 'name': 'user_profile'},
    {'path': 'published-validations', 'name': 'published_validations'},
    {'path': 'about', 'name': 'about'},
    {'path': 'help', 'name': 'help'},
    {'path': 'contact-us', 'name': 'contact-us'},
    {'path': 'terms', 'name': 'terms'},
    {'path': 'datasets', 'name': 'datasets'},
    {'path': 'signup', 'name': 'signup'},
    {'path': 'signup-complete', 'name': 'signup_complete'},
    {'path': 'deactivate-user-complete', 'name': 'deactivate_user_complete'},
    {'path': 'password-reset', 'name': 'password-reset'},
    {'path': 'password-reset-done', 'name': 'password-reset-done'},
    {'path': 'password-reset/:token', 'name': 'validate-token'},
    {'path': 'set-password', 'name': 'set-password'},
    {'path': 'my-datasets', 'name': 'my-datasets'}
]


def get_angular_url(url_name, parameter=None):
    """
    This function returns an angular route based on the name assigned. We need it for example for assigning an url to a
    netCDF file. Paths come from UI/src/app/app-routing.module.ts.
    Parameters
    ----------
    url_name: name of a url, as defined above
    parameter: usually it refers to the validation id

    Returns
    -------
    url

    """
    searched_element = next(path_item for path_item in angular_paths if path_item['name'] == url_name)
    if '/' in searched_element['path'] and parameter:
        first_element = searched_element['path'].split('/')[0]
        searched_path = first_element + '/' + str(parameter)
    elif searched_element['path'] == 'validate' and parameter:
        searched_path = 'validate?validation_id=' + str(parameter)
    else:
        searched_path = searched_element['path']

    if settings.DEBUG:
        return '/' + searched_path

    return '/ui/' + searched_path


def redirect_result_page(request, result_uuid):
    new_url = SITE_URL + get_angular_url('result', result_uuid)
    return redirect(new_url)