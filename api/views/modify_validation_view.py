from django.http import QueryDict
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from validator.doi import get_doi_for_validation
from validator.forms import PublishingForm
from validator.models import ValidationRun, CopiedValidations
from validator.validation.validation import stop_running_validation
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import status

# from validator.views.results import _copy_validationrun
from api.views.validation_run_view import _copy_validationrun

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def stop_validation(request, result_uuid):
    if request.method == "DELETE":
        validation_run = get_object_or_404(ValidationRun, pk=result_uuid)
        if validation_run.user != request.user:
            return HttpResponse(status=403)

        stop_running_validation(result_uuid)
        return HttpResponse(status=200)

    return HttpResponse(status=405)  # if we're not DELETEing, send back "Method not Allowed"


@api_view(['POST', 'GET', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
def modify_result(request, result_uuid):
    val_run = get_object_or_404(ValidationRun, pk=result_uuid)
    current_user = request.user

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

    elif (request.method == 'PATCH'):
        ## make sure only the owner of a validation can change it (others are allowed to GET it, though)

        if (val_run.user != request.user):
            return HttpResponse(status=403)

        patch_params = request.data
        patch_params_keys = patch_params.keys()

        if 'save_name' in patch_params_keys:
            ## check that our validation's name can be changed'; it can't if it already has a DOI
            if (not val_run.is_unpublished):
                return HttpResponse('Validation has been published', status=405)

            save_mode = patch_params['save_name']

            if not save_mode:
                return HttpResponse("Wrong action parameter.", status=400)

            val_run.name_tag = patch_params['new_name']
            val_run.save()

            return HttpResponse("Changed.", status=200)

        if 'archive' in patch_params_keys:
            archive_mode = patch_params['archive']

            if not type(archive_mode) is bool:
                return HttpResponse("Wrong action parameter.", status=400)

            val_run.archive(unarchive=(not archive_mode))
            return HttpResponse("Changed.", status=200)

        if 'extend' in patch_params_keys:
            extend = patch_params['extend']
            if type(extend) != bool or not extend:
                return HttpResponse("Wrong action parameter.", status=400)

            val_run.extend_lifespan()
            return HttpResponse(val_run.expiry_date, status=200)

        if 'publish' in patch_params_keys:
            publish = patch_params['publish']
            publishing_form = patch_params['publishing_form']

            # check we've got the action set correctly
            if type(publish) != bool:
                return HttpResponse("Wrong action parameter.", status=400)

            # check that the publication parameters are valid
            pub_form = PublishingForm(data=publishing_form, validation=val_run)
            if not pub_form.is_valid():
                errors = pub_form.errors.get_json_data()
                print(errors)
                response = JsonResponse(errors, status=400, safe=False)
                # if not, send back an updated publication form with errors set and http code 420 (picked up in javascript)
                return response

            try:
                get_doi_for_validation(val_run, pub_form.pub_metadata)
            except Exception as e:
                m = getattr(e, 'message', repr(e))
                response = JsonResponse({'response': m}, status=400)
                return response

            response = JsonResponse({'response': 'Published'}, status=200)
            return response

        response = JsonResponse({'response': 'Wrong action parameter.'}, status=400)
        return response

    elif request.method == 'POST':
        post_params = request.data
        post_params_keys = post_params.keys()

        user = request.user
        if 'add_validation' in post_params_keys and post_params['add_validation']:
            if val_run not in user.copied_runs.all():
                valrun_user = CopiedValidations(used_by_user=user, original_run=val_run, copied_run=val_run)
                valrun_user.save()
                response = HttpResponse("Validation added to your list", status=200)
            else:
                response = HttpResponse("You have already added this validation to your list", status=200)
        elif 'remove_validation' in post_params_keys and post_params['remove_validation']:
            user.copied_runs.remove(val_run)
            response = HttpResponse("Validation has been removed from your list", status=200)

        elif 'copy_validation' in post_params and post_params['copy_validation'] == 'true':
            resp = _copy_validationrun(val_run, request.user)
            response = JsonResponse(resp)

        else:
            response = HttpResponse("Wrong action parameter.", status=400)

        return response
