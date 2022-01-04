from django.contrib.auth import get_user_model

User = get_user_model()


def create_test_user():
    auth_data = {
        'username': 'chuck_norris',
        'password': 'roundhousekick'
    }

    user_data = {
        'username': auth_data['username'],
        'password': auth_data['password'],
        'email': 'norris@awst.at',
        'first_name': 'Chuck',
        'last_name': 'Norris',
        'organisation': 'Texas Rangers',
        'country': 'US',
        'orcid': '0000-0002-1825-0097',
    }
    User.objects.filter(email=user_data['email']).delete()
    test_user = User.objects.create_user(**user_data)
    return auth_data, test_user
