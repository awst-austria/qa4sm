import django.forms as forms


class ResultsSortingForm(forms.Form):
    """Allows the user to select a key and ordering for sorting results."""

    sort_key = forms.fields.ChoiceField(
        choices=[
            ("start_time", "Date"),
            ("name_tag", "Name"),
            ("progress", "Status"),
            ("spatial_reference_configuration_id__dataset__pretty_name",
             "Reference dataset"),
        ],
        required=False,
    )
    sort_order = forms.fields.ChoiceField(
        choices=[
            ("desc", "descending"),
            ("asc", "ascending"),
        ],
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set initial values on field level too
        for field in self.fields:
            self.fields[field].initial = self.get_initial_for_field(
                self.fields[field], field
            )

    def clean(self):
        """Clean the data and replace missing by initial."""
        cleaned_data = super().clean()
        # replace missing/invalid values with initial values
        for field in self.fields:
            if field not in self.data or field not in cleaned_data:
                cleaned_data[field] = self.get_initial_for_field(
                    self.fields[field], field
                )

    @classmethod
    def get_sorting(
            cls,
            request,
            initial_key="start_time",
            initial_order="desc"
    ):
        """
        Create a sorting form from the given request.

        Parameters
        ----------
        request : request
        initial_key : str, optional
            Options are: "start_time" (default), "name_tag", "progress",
            "spatial_reference_configuration_id__dataset__pretty_name".
        initial_order : str, optional
            Options are: "desc" (default), "asc"

        Returns
        -------
        sorting_form : ResultsSortingForm
        order : str
            String for use in ``order_by``, including key and ordering
            direction.
        """
        key, order = initial_key, initial_order
        form = cls(
            request.GET,
            initial={"sort_key": initial_key, "sort_order": initial_order}
        )
        if form.is_valid():
            key = form.cleaned_data["sort_key"]
            order = form.cleaned_data["sort_order"]
        order_string = {"asc": "", "desc": "-"}[order] + key
        # set attributes on form to access in html
        form.key = key
        form.order = order

        return form, order_string
