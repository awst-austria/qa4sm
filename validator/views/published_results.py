from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from validator.forms import ResultsSortingForm
from validator.models import ValidationRun


def published_results(request):
    page = request.GET.get('page', 1)

    # get sorting key and order
    sorting_form, order = ResultsSortingForm.get_sorting(request)

    published = (
        ValidationRun.objects.filter(doi__isnull=False)
        .exclude(doi__exact='')
        .order_by(order)
    )

    paginator = Paginator(published, 10)
    try:
        paginated_runs = paginator.page(page)
    except PageNotAnInteger:
        paginated_runs = paginator.page(1)
    except EmptyPage:
        paginated_runs = paginator.page(paginator.num_pages)

    context = {
        'validations': paginated_runs,
        'sorting_form': sorting_form,
    }
    return render(request, 'validator/published_results.html', context)
