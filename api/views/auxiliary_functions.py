from validator.models import Dataset
from django.db.models.fields.related import ManyToManyRel, OneToOneField

def get_fields_as_list(model):
    fields = []
    for field in model._meta.get_fields():
        if isinstance(field, ManyToManyRel):
            fields.append(field.related_name)
        elif not isinstance(field, OneToOneField):
            fields.append(field.name)
    for property_name in list(model._meta._property_names):
        fields.append(property_name)
    return fields


def clean_redundant_datasets(user_datasets_without_file):
    for dataset in user_datasets_without_file:
        versions = dataset.versions.all()
        variables = dataset.variables.all()
        for version in versions:
            version.delete()
        for variable in variables:
            variable.delete()

        dataset.delete()
