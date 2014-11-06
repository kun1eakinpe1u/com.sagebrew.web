from django import forms


class PostForm(forms.Form):
    content = forms.CharField()
    current_pleb = forms.EmailField()


class SavePostForm(PostForm):
    wall_pleb = forms.EmailField()


class DeletePostForm(forms.Form):
    pleb = forms.CharField()
    post_uuid = forms.CharField()


class GetPostForm(forms.Form):
    current_user = forms.EmailField()
    email = forms.EmailField()
    range_end = forms.IntegerField()
    range_start = forms.IntegerField()
