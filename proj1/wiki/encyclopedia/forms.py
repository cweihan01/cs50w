from django import forms


class NewPageForm(forms.Form):
    """ Form containing `title` and `contents` field to create a new page. """
    title = forms.CharField(label="Title of page:", max_length=32)
    contents = forms.CharField(label="Contents of page: ", widget=forms.Textarea)


class EditForm(forms.Form):
    """ Form containing `contents` field to edit an existing page. """
    contents = forms.CharField(label="Edit contents: ", widget=forms.Textarea)
