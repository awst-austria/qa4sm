from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from validator.models import ValidationRun, CopiedValidations
from validator.validation.validation import stop_running_validation
from django.http.response import HttpResponse
from django.http.response import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response


def stop_validation(request, result_uuid):
    if request.method == "DELETE":
        validation_run = get_object_or_404(ValidationRun, pk=result_uuid)
        if validation_run.user != request.user:
            return JsonResponse('Not your validation' ,status=403)

        stop_running_validation(result_uuid)
        return JsonResponse("Validation stopped.", status=200)

    return JsonResponse('Method not Allowed', status=405)  # if we're not DELETEing, send back "Method not Allowed"


@api_view(['POST', 'GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def modify_result(request, result_uuid):
    val_run = get_object_or_404(ValidationRun, pk=result_uuid)
    current_user = request.user
    print('Monika', request.method)

    # copied_runs = current_user.copiedvalidations_set.all() if current_user.username else CopiedValidations.objects.none()
    # is_copied = val_run.id in copied_runs.values_list('copied_run', flat=True)

    # if is_copied and val_run.doi == '':
    #     original_start = copied_runs.get(copied_run=val_run).original_run.start_time
    #     original_end = copied_runs.get(copied_run=val_run).original_run.end_time
    # else:
    #     original_start = None
    #     original_end = None

    if request.method == 'DELETE':
        ## make sure only the owner of a validation can delete it (others are allowed to GET it, though)
        if(val_run.user != request.user):
            return HttpResponse(status = status.HTTP_403_FORBIDDEN)

        ## check that our validation can be deleted; it can't if it already has a DOI
        if(not val_run.is_unpublished):
            return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED) #405

        val_run.delete()
        return HttpResponse(status=status.HTTP_200_OK)