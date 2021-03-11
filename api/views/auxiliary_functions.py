def get_fields_as_list(model):
    fields = []
    for field in model._meta.get_fields():
        fields.append(field.name)
    for property_name in list(model._meta._property_names):
        fields.append(property_name)
    return fields