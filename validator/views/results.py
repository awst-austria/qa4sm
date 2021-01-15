import os
from json import dumps as json_dumps

import netCDF4
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import QueryDict
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render

from validator.doi import get_doi_for_validation
from validator.forms import PublishingForm, ResultsSortingForm
from validator.models import ValidationRun, CopiedValidations
from validator.validation.globals import METRICS
from validator.validation.graphics import get_dataset_combis_and_metrics_from_files

from collections import OrderedDict
from validator.validation.util import mkdir_if_not_exists
from validator.validation.globals import OUTPUT_FOLDER
from shutil import copy2
from dateutil.tz import tzlocal
from datetime import datetime
from django.conf import settings
from django.urls.base import reverse

def _copy_validationrun(run_to_copy, new_user):
    # checking if the new validation belongs to the same user:
    if run_to_copy.user == new_user:
        run_id = run_to_copy.id
        # belongs_to_user = True
    else:
        # copying validation
        valrun_user = CopiedValidations(used_by_user=new_user, original_run=run_to_copy)
        valrun_user.save()

        # old info which is needed then
        old_scaling_ref_id = run_to_copy.scaling_ref_id
        old_val_id = str(run_to_copy.id)

        dataset_conf = run_to_copy.dataset_configurations.all()

        run_to_copy.user = new_user
        run_to_copy.id = None
        run_to_copy.start_time = datetime.now(tzlocal())
        run_to_copy.end_time = datetime.now(tzlocal())
        run_to_copy.save()
        run_id = run_to_copy.id

        # adding the copied validation to the copied validation list
        valrun_user.copied_run = run_to_copy
        valrun_user.save()

        # new configuration
        for conf in dataset_conf:
            old_id = conf.id
            old_filters = conf.filters.all()
            old_param_filters = conf.parametrisedfilter_set.all()

            # setting new scaling reference id
            if old_id == old_scaling_ref_id:
                run_to_copy.scaling_ref_id = conf.id

            new_conf = conf
            new_conf.pk = None
            new_conf.validation = run_to_copy
            new_conf.save()

            # setting filters
            new_conf.filters.set(old_filters)
            if len(old_param_filters) != 0:
                for param_filter in old_param_filters:
                    param_filter.id = None
                    param_filter.dataset_config = new_conf
                    param_filter.save()

        # the reference configuration is always the last one:
        try:
            run_to_copy.reference_configuration_id = conf.id
            run_to_copy.save()
        except:
            pass

        # copying files
        # new directory -> creating if doesn't exist
        new_dir = os.path.join(OUTPUT_FOLDER, str(run_id))
        mkdir_if_not_exists(new_dir)
        # old directory and all files there
        old_dir = os.path.join(OUTPUT_FOLDER, old_val_id)
        old_files = os.listdir(old_dir)

        if len(old_files) != 0:
            for file_name in old_files:
                new_file = new_dir + '/' + file_name
                old_file = old_dir + '/' + file_name
                copy2(old_file, new_file)
                if '.nc' in new_file:
                    run_to_copy.output_file = str(run_id) + '/' + file_name
                    run_to_copy.save()
                    file = netCDF4.Dataset(new_file, mode='a', format="NETCDF4")

                    # with netCDF4.Dataset(new_file, mode='a', format="NETCDF4") as file:
                    new_url = settings.SITE_URL + reverse('result', kwargs={'result_uuid': run_to_copy.id})
                    file.setncattr('url', new_url)
                    file.setncattr('date_copied', run_to_copy.start_time.strftime('%Y-%m-%d %H:%M'))
                    file.close()

    response = {
        'run_id': run_id,
    }
    return response
  

@login_required(login_url='/login/')
def user_runs(request):
    current_user = request.user


    cur_user_runs = ValidationRun.objects.filter(user=current_user).order_by('-start_time')
    tracked_runs = current_user.copied_runs.exclude(doi='')
    sorting_form, order = ResultsSortingForm.get_sorting(request)
    page = request.GET.get('page', 1)
    cur_user_runs = (
        ValidationRun.objects.filter(user=current_user)
        .order_by(order)
    )


    paginator = Paginator(cur_user_runs, 10)
    try:
        paginated_runs = paginator.page(page)
    except PageNotAnInteger:
        paginated_runs = paginator.page(1)
    except EmptyPage:
        paginated_runs = paginator.page(paginator.num_pages)
    context = {
        'myruns': paginated_runs,
        'tracked_runs': tracked_runs,
        'sorting_form': sorting_form,
        }
    
    return render(request, 'validator/user_runs.html', context)


def result(request, result_uuid):
    val_run = get_object_or_404(ValidationRun, pk=result_uuid)
    current_user = request.user
    copied_runs = current_user.copiedvalidations_set.all() if current_user.username else []
    is_copied = val_run.id in copied_runs.values_list('copied_run', flat=True)

    if is_copied and val_run.doi == '':
        original_start = copied_runs.get(copied_run=val_run).original_run.start_time
        original_end = copied_runs.get(copied_run=val_run).original_run.end_time
    else:
        original_start = None
        original_end = None


    if(request.method == 'DELETE'):
        ## make sure only the owner of a validation can delete it (others are allowed to GET it, though)
        if(val_run.user != request.user):
            return HttpResponse(status=403)

        ## check that our validation can be deleted; it can't if it already has a DOI
        if(not val_run.is_unpublished):
            return HttpResponse(status=405) #405

        val_run.delete()
        return HttpResponse("Deleted.", status=200)

    elif request.method == 'POST':
        post_params = QueryDict(request.body)
        user = request.user
        if 'add_validation' in post_params and post_params['add_validation'] == 'true':
            if val_run not in user.copied_runs.all():
                valrun_user = CopiedValidations(used_by_user=user, original_run=val_run, copied_run=val_run)
                valrun_user.save()
                response = HttpResponse("Validation added to your list", status=200)
            else:
                response = HttpResponse("You have already added this validation to your list", status=200)

        elif 'remove_validation' in post_params and post_params['remove_validation'] == 'true':
            user.copied_runs.remove(val_run)
            response = HttpResponse("Validation has been removed from your list", status=200)

        elif 'copy_validation' in post_params and post_params['copy_validation'] == 'true':
            resp = _copy_validationrun(val_run, request.user)
            response = JsonResponse(resp)

        else:
            response = HttpResponse("Wrong action parameter.", status=400)

        return response

    elif(request.method == 'PATCH'):
        ## make sure only the owner of a validation can change it (others are allowed to GET it, though)

        if(val_run.user != request.user):
            return HttpResponse(status=403)

        patch_params = QueryDict(request.body)

        if 'save_name' in patch_params:
            ## check that our validation's name can be changed'; it can't if it already has a DOI
            if (not val_run.is_unpublished):
                return HttpResponse('Validation has been published', status=405)

            save_mode = patch_params['save_name']

            if save_mode != 'true':
                return HttpResponse("Wrong action parameter.", status=400)

            val_run.name_tag = patch_params['new_name']
            val_run.save()

            return HttpResponse("Changed.", status=200)


        if 'archive' in patch_params:
            archive_mode = patch_params['archive']

            if not ((archive_mode == 'true') or (archive_mode == 'false')):
                return HttpResponse("Wrong action parameter.", status=400)

            val_run.archive(unarchive = (archive_mode == 'false'))
            return HttpResponse("Changed.", status=200)

        if 'extend' in patch_params:
            extend = patch_params['extend']

            if extend != 'true':
                return HttpResponse("Wrong action parameter.", status=400)

            val_run.extend_lifespan()
            return HttpResponse(val_run.expiry_date, status=200)

        if 'publish' in patch_params:
            publish = patch_params['publish']

            # check we've got the action set correctly
            if publish != 'true':
                return HttpResponse("Wrong action parameter.", status=400)

            # check that the publication parameters are valid
            pub_form = PublishingForm(data=patch_params, validation=val_run)
            if not pub_form.is_valid():
                # if not, send back an updated publication form with errors set and http code 420 (picked up in javascript)
                return render(request, 'validator/publishing_dialog.html', {'publishing_form': pub_form, 'val': val_run}, status=420)

            try:
                get_doi_for_validation(val_run, pub_form.pub_metadata)
            except Exception as e:
                m = getattr(e, 'message', repr(e))
                return HttpResponse(m, status=400)

            return HttpResponse("Published.", status=200)

        return HttpResponse("Wrong action parameter.", status=400)

    # by default, show page
    else:
        ## tell template whether it's the owner of the validation - to show action buttons
        is_owner = (val_run.user == request.user)

        ## TODO: get time in format like '2 minutes', '5 hours'
        run_time = None
        if val_run.end_time is not None:
            run_time = val_run.end_time - val_run.start_time
            run_time = (run_time.days * 1440) + (run_time.seconds // 60)

        error_rate = 1
        if val_run.total_points != 0:
            error_rate = (val_run.total_points - val_run.ok_points) / val_run.total_points

        pairs, triples, metrics, ref0_config = get_dataset_combis_and_metrics_from_files(val_run)
        combis = OrderedDict(sorted({**pairs, **triples}.items()))
        # the publication form is only needed by the owner; if we're displaying for another user, avoid leaking user data
        pub_form = PublishingForm(validation=val_run) if is_owner else None

        metrics = OrderedDict(sorted([(v, k) for k, v in metrics.items()]))

        context = {
            'current_user': current_user.username,
            'is_owner': is_owner,
            'val' : val_run,
            'is_copied': is_copied,
            'original_start': original_start,
            'original_end': original_end,
            'error_rate' : error_rate,
            'run_time': run_time,
            'metrics': metrics,
            'combis': combis,
            'json_metrics': json_dumps(METRICS),
            'publishing_form': pub_form
            }

        return render(request, 'validator/result.html', context)

