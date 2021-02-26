def get_fields_as_list(model):
    fields = []
    for field in model._meta.get_fields():
        fields.append(field.name)
    return fields