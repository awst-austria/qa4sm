from json import dumps as json_dumps

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import QueryDict
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render

from validator.doi import get_doi_for_validation
from validator.forms import PublishingForm
from validator.forms.custom_widgets import ResultsSortingForm
from validator.models import ValidationRun
from validator.validation.globals import METRICS, TC_METRICS
from validator.validation.graphics import get_dataset_combis_and_metrics_from_files

from collections import OrderedDict

@login_required(login_url='/login/')
def user_runs(request):
    current_user = request.user

    sort_key = request.GET.get("sort_key", "start_time")
    sort_order = request.GET.get("sort_order", "-")
    sorting_form = ResultsSortingForm(
        initial={"sort_key": sort_key, "sort_order": sort_order},
    )

    page = request.GET.get('page', 1)
    cur_user_runs = (
        ValidationRun.objects.filter(user=current_user)
        .order_by(sort_order + sort_key)
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
        'sorting_form': sorting_form,
        }
    return render(request, 'validator/user_runs.html', context)


def result(request, result_uuid):
    val_run = get_object_or_404(ValidationRun, pk=result_uuid)
    if(request.method == 'DELETE'):
        ## make sure only the owner of a validation can delete it (others are allowed to GET it, though)
        if(val_run.user != request.user):
            return HttpResponse(status=403)

        ## check that our validation can be deleted; it can't if it already has a DOI
        if(not val_run.is_unpublished):
            return HttpResponse(status=405) #405

        val_run.delete()
        return HttpResponse("Deleted.", status=200)

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
            'is_owner': is_owner,
            'val' : val_run,
            'error_rate' : error_rate,
            'run_time': run_time,
            'metrics': metrics,
            'combis': combis,
            'json_metrics': json_dumps(METRICS),
            'publishing_form': pub_form
            }

        return render(request, 'validator/result.html', context)
