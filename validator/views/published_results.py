from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from validator.models import ValidationRun


def published_results(request):
    current_user = request.user
    copied_runs = current_user.copied_runs.all() if current_user.username else []

    page = request.GET.get('page', 1)

    published = ValidationRun.objects.filter(doi__isnull=False).exclude(doi__exact='').order_by('-start_time')

    paginator = Paginator(published, 10)
    try:
        paginated_runs = paginator.page(page)
    except PageNotAnInteger:
        paginated_runs = paginator.page(1)
    except EmptyPage:
        paginated_runs = paginator.page(paginator.num_pages)

    context = {
        'current_user': current_user.username,
        'copied_runs': copied_runs,
        'validations': paginated_runs,
        }
    return render(request, 'validator/published_results.html', context)
