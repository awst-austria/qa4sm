import json

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from validator.doi import get_doi_for_validation
from validator.forms import PublishingForm
from validator.models import ValidationRun, CopiedValidations
from validator.validation.validation import stop_running_validation
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from validator.validation.validation import copy_validationrun
import logging

from django.db import connections
from multiprocessing.context import Process

__logger = logging.getLogger(__name__)


def get_doi_process(validation, publish_form):
    connections.close_all()
    p = Process(target=get_doi_for_validation, kwargs={"val": validation,
                                                       "metadata": publish_form.pub_metadata})
    p.start()
    return


__logger = logging.getLogger(__name__)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def stop_validation(request, result_uuid):
    if request.method == "DELETE":
        validation_run = get_object_or_404(ValidationRun, pk=result_uuid)
        if validation_run.user != request.user:
            return HttpResponse(status=403)

        stop_running_validation(result_uuid)
        return HttpResponse(status=200)

    return HttpResponse(status=405)  # if we're not DELETing, send back "Method not Allowed"


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def change_name(request, result_uuid):
    val_run = get_object_or_404(ValidationRun, pk=result_uuid)

    if val_run.user != request.user:
        return HttpResponse(status=403)

    if not val_run.is_unpublished:
        return HttpResponse('Validation has been published', status=405)

    patch_params = request.data
    save_mode = patch_params['save_name']

    if not save_mode:
        return HttpResponse("Wrong action parameter.", status=400)

    val_run.name_tag = patch_params['new_name']
    val_run.save()

    return HttpResponse("Changed.", status=200)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def archive_result(request, result_uuid):
    val_run = get_object_or_404(ValidationRun, pk=result_uuid)

    if val_run.user != request.user:
        return HttpResponse(status=403)

    if not val_run.is_unpublished:
        return HttpResponse('Validation has been published', status=405)

    patch_params = request.data

    archive_mode = patch_params['archive']

    if not type(archive_mode) is bool:
        return HttpResponse("Wrong action parameter.", status=400)

    val_run.archive(unarchive=(not archive_mode))
    return HttpResponse(val_run.expiry_date, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def archive_multiple_results(request):
    id_list = request.GET.getlist('id')
    archive_mode = json.loads(request.GET.get('archive'))

    validations_to_archive = (ValidationRun.objects.filter(id__in=id_list)
                              .filter(doi='')
                              .exclude(is_archived=archive_mode)
                              .filter(user=request.user))

    if not type(archive_mode) is bool:
        return HttpResponse("Wrong action parameter.", status=400)

    for validation in validations_to_archive:
        validation.archive(unarchive=(not archive_mode))

    return HttpResponse(status=200)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def extend_result(request, result_uuid):
    val_run = get_object_or_404(ValidationRun, pk=result_uuid)

    if val_run.user != request.user:
        return HttpResponse(status=403)

    if not val_run.is_unpublished:
        return HttpResponse('Validation has been published', status=405)

    patch_params = request.data
    extend = patch_params['extend']

    if type(extend) != bool or not extend:
        return HttpResponse("Wrong action parameter.", status=400)

    val_run.extend_lifespan()
    return HttpResponse(val_run.expiry_date, status=200)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def publish_result(request, result_uuid):
    val_run = get_object_or_404(ValidationRun, pk=result_uuid)

    if val_run.user != request.user:
        return JsonResponse({'message': 'Wrong user'}, status=403)

    if not val_run.is_unpublished:
        return JsonResponse({'message': 'Validation has been published'}, status=405)

    if not val_run.output_file:
        return JsonResponse({'message': 'There is no result to be published'}, status=405)

    if not val_run.id or not val_run.output_file or not val_run.output_file.path or not val_run.user:
        return JsonResponse({'message': "'Can't create DOI for broken validation'"}, status=405)

    if (val_run.publishing_in_progress):
        return JsonResponse({'message': "Publishing already in progress"}, status=405)

    patch_params = request.data

    publish = patch_params['publish']
    publishing_form = patch_params['publishing_form']

    # check we've got the action set correctly
    if type(publish) != bool or not publish:
        return HttpResponse("Wrong action parameter.", status=400)

    # check that the publication parameters are valid
    pub_form = PublishingForm(data=publishing_form, validation=val_run)
    if not pub_form.is_valid():
        errors = pub_form.errors.get_json_data()
        response = JsonResponse(errors, status=400, safe=False)
        # if not, send back an updated publication form with errors set and http code 420 (picked up in javascript)
        return response

    try:
        get_doi_process(val_run, pub_form)
        response = JsonResponse({'response': 'Publishing in progress'}, status=200)
    except Exception as e:
        __logger.debug(e, repr(e))
        m = getattr(e, 'message', repr(e))
        response = JsonResponse({'response': m}, status=400)
        return response

    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_validation(request, result_uuid):
    val_run = get_object_or_404(ValidationRun, pk=result_uuid)
    post_params = request.data

    user = request.user
    if post_params['add_validation']:
        if val_run not in user.copied_runs.all():
            valrun_user = CopiedValidations(used_by_user=user, original_run=val_run, copied_run=val_run)
            valrun_user.save()
            response = HttpResponse("Validation added to your list", status=200)
        else:
            response = HttpResponse("You have already added this validation to your list", status=200)

    else:
        response = HttpResponse("Wrong action parameter.", status=400)

    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_validation(request, result_uuid):
    val_run = get_object_or_404(ValidationRun, pk=result_uuid)
    post_params = request.data

    user = request.user
    if post_params['remove_validation']:
        user.copied_runs.remove(val_run)
        response = HttpResponse("Validation has been removed from your list", status=200)
    else:
        response = HttpResponse("Wrong action parameter.", status=400)

    return response


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_result(request, result_uuid):
    val_run = get_object_or_404(ValidationRun, pk=result_uuid)

    ## make sure only the owner of a validation can delete it (others are allowed to GET it, though)
    if (val_run.user != request.user):
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    ## check that our validation can be deleted; it can't if it already has a DOI
    if not val_run.is_unpublished or val_run.is_archived:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)  # 405

    val_run.delete()
    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_multiple_result(request):
    id_list = request.GET.getlist('id')
    validations_to_remove = (ValidationRun.objects.filter(id__in=id_list)
                             .filter(doi='')
                             .filter(is_archived=False)
                             .filter(user=request.user))

    for validation in validations_to_remove:
        validation.delete()

    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_publishing_form(request):
    validation_id = request.query_params.get('id', None)
    validation = get_object_or_404(ValidationRun, id=validation_id)
    if request.user == validation.user:
        publishing_form = PublishingForm(validation=validation)
        response = JsonResponse(publishing_form.data, status=200)
    else:
        response = JsonResponse({'message': 'Validation does not belong to the current user'}, status=403)

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def copy_validation_results(request):
    validation_id = request.query_params.get('validation_id', None)
    validation = get_object_or_404(ValidationRun, id=validation_id)
    current_user = request.user

    new_validation = copy_validationrun(validation, current_user)

    return JsonResponse(new_validation, status=200)
