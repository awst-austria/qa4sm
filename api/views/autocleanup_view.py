from datetime import timedelta

from django.http import JsonResponse
from django.utils import timezone

from django.conf import settings
from rest_framework import status

from validator.mailer import send_val_expiry_notification
from validator.models import ValidationRun, CeleryTask, User

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from validator.mailer import send_autocleanup_failed


def auto_cleanup():
    '''
    Iterate over all users and checks if their validations are expired/near expiry. 
    Furthermore check if user has been inactive, if so send notification.
    '''

    users = User.objects.all()

    validations_cleaned = []
    validations_warned = []

    userAccounts_cleaned = []

    for user in users:
        #### validation cleanup ####

        # Filter out removed, archived or published validations
        validations = ValidationRun.objects.filter(user=user).filter(isRemoved=False).filter(is_archived=False).filter(doi__exact = '')
        validations_near_expiring = []

        for validation in validations:

            # notify user about upcoming expiry if not already done
            if validation.is_near_expiry and not validation.expiry_notified:

                # if already a quarter of the warning period has passed without a notification
                # being sent (could happen when service is down),
                # extend the validation so that the user gets the full warning period
                ''' 
                if timezone.now() + timedelta(
                        days=settings.VALIDATION_EXPIRY_WARNING_DAYS / 4) > validation.expiry_date:
                    validation.last_extended = timezone.now() - timedelta(
                        days=settings.VALIDATION_EXPIRY_DAYS - settings.VALIDATION_EXPIRY_WARNING_DAYS)
                    validation.save()
                '''
                # Do we not want to just set the last_extended to the current time as we only enter this loop if near expiry but not notified?
                validation.last_extended = timezone.now()
                validation.save()

                validations_near_expiring.append(validation)
                validations_warned.append(str(validation.id))
                continue

            # if validation is expired and user was notified, get rid of it
            elif validation.is_expired and validation.expiry_notified:

                celery_tasks = CeleryTask.objects.filter(validation_id=validation.id)
                for task in celery_tasks:
                    task.delete()

                #validation.isRemoved = True
                #validation.save()
                validations_cleaned.append(str(validation.id))

        if len(validations_near_expiring) != 0:
            send_val_expiry_notification(validations_near_expiring)
        
    #### cleanup validations with no user ####
    no_user_validations = ValidationRun.objects.filter(user=None)
    for no_user_val in no_user_validations:
        
        celery_tasks = CeleryTask.objects.filter(validation_id=no_user_val.id)
        for task in celery_tasks:
            task.delete()

        no_user_val.isRemoved = True    
        no_user_val.save()
        validations_cleaned.append(str(no_user_val.id))

    print('Cleaned validations: ' + ', '.join(validations_cleaned))
    print('warned validations: ' + ', '.join(validations_warned))

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@authentication_classes([TokenAuthentication])
def run_auto_cleanup_script(request): 
    if str(request.user.auth_token) == settings.ADMIN_ACCESS_TOKEN:
        try:
            auto_cleanup()
        except Exception as e:
            send_autocleanup_failed(str(e))
            return JsonResponse({'message': 'something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return JsonResponse({'message': 'success'}, status=status.HTTP_200_OK, safe=False)
    else:
        send_autocleanup_failed('provided token does not belong to the admin user.')
        return JsonResponse({'message': 'Provided token does not belong to the admin user.'},
                            status=status.HTTP_401_UNAUTHORIZED)