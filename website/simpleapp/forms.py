from django import forms

class UploadImageForm(forms.Form):
	gender = forms.ChoiceField(widget=forms.RadioSelect, choices=(('m','male'),('f','female')))
	file = forms.ImageField()
