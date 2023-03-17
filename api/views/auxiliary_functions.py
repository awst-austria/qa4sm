from validator.models import Dataset

def get_fields_as_list(model):
    fields = []
    for field in model._meta.get_fields():
        fields.append(field.name)
    for property_name in list(model._meta._property_names):
        fields.append(property_name)
    return fields


def clean_redundant_datasets(user):
    user_datasets_without_file = Dataset.objects.filter(user=user).filter(user_dataset__isnull=True)
    print(user_datasets_without_file)
    for dataset in user_datasets_without_file:
        if len(dataset.user_dataset.all()) == 0:
            versions = dataset.versions.all()
            variables = dataset.variables.all()
            dataset.versions.clear()
            dataset.variables.clear()
            dataset.delete()
            for version in versions:
                version.delete()
            for variable in variables:
                variable.delete()
