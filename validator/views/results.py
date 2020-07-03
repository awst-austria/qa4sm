from json import dumps as json_dumps

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import QueryDict
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from validator.models import ValidationRun
from validator.validation.globals import METRICS
from validator.validation.graphics import get_dataset_pairs


@login_required(login_url='/login/')
def user_runs(request):
    current_user = request.user
    page = request.GET.get('page', 1)

    cur_user_runs = ValidationRun.objects.filter(user=current_user).order_by('-start_time')

    paginator = Paginator(cur_user_runs, 10)
    try:
        paginated_runs = paginator.page(page)
    except PageNotAnInteger:
        paginated_runs = paginator.page(1)
    except EmptyPage:
        paginated_runs = paginator.page(paginator.num_pages)

    context = {
        'myruns' : paginated_runs,
        }
    return render(request, 'validator/user_runs.html', context)


@login_required(login_url='/login/')
def result(request, result_uuid):
    val_run = get_object_or_404(ValidationRun, pk=result_uuid)

    if(request.method == 'DELETE'):
        ## make sure only the owner of a validation can delete it (others are allowed to GET it, though)
        if(val_run.user != request.user):
            return HttpResponse(status=403)

        val_run.delete()
        return HttpResponse("Deleted.", status=200)

    elif(request.method == 'PATCH'):
        ## make sure only the owner of a validation can change it (others are allowed to GET it, though)
        if(val_run.user != request.user):
            return HttpResponse(status=403)

        patch_params = QueryDict(request.body)

        if 'archive' in patch_params:
            archive_mode = patch_params['archive']

            if not ((archive_mode == 'true') or (archive_mode == 'false')):
                return HttpResponse("Wrong parameter.", status=400)

            val_run.archive(unarchive = (archive_mode == 'false'))
            return HttpResponse("Changed.", status=200)

        if 'extend' in patch_params:
            extend = patch_params['extend']

            if extend != 'true':
                return HttpResponse("Wrong parameter.", status=400)

            val_run.extend_lifespan()
            return HttpResponse(val_run.expiry_date, status=200)

        return HttpResponse("Wrong parameter.", status=400)

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

        pairs = get_dataset_pairs(val_run)

        context = {
            'is_owner': is_owner,
            'val' : val_run,
            'error_rate' : error_rate,
            'run_time': run_time,
            'metrics': METRICS,
            'pairs': pairs,
            'json_metrics': json_dumps(METRICS),
            }

        return render(request, 'validator/result.html', context)
