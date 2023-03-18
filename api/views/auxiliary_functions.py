from validator.models import Dataset


def get_fields_as_list(model):
    fields = []
    for field in model._meta.get_fields():
        fields.append(field.name)
    for property_name in list(model._meta._property_names):
        fields.append(property_name)
    return fields


# def clean_redundant_datasets(user):
#     user_datasets_without_file = Dataset.objects.filter(user=user).filter(user_dataset__isnull=True)
#     print(user_datasets_without_file)
#     for dataset in user_datasets_without_file:
#         print(dataset)
#         versions = dataset.versions.all()
#         variables = dataset.variables.all()
#         dataset.versions.clear()
#         dataset.variables.clear()
#         dataset.delete()
#         print(versions, variables)
#         for version in versions:
#             print('version: ', version)
#             version.delete()
#         for variable in variables:
#             print('variable: ', variables)
#             variable.delete()
