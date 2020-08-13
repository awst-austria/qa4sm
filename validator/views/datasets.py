from django.shortcuts import render
from validator.models import Dataset

def datasets(request):
    datasets = Dataset.objects.all().order_by('pretty_name')
    context = {
        'ref_flags' : [False, True], ## push a list of literal booleans into the template to separate datasets and reference datasets
        'datasets' : datasets,
        }
    return render(request, 'validator/datasets.html', context)
