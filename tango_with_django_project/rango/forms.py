from django import forms
from rango.models import Tapa

class TapaForm(forms.ModelForm):
    nombre = forms.CharField(max_length=128, help_text="Por favor introduzca el nombre de la tapa")
    votos = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    class Meta:
		# Provide an association between the ModelForm and a model
        model = Tapa

		# What fields do we want to include in our form?
		# This way we don't need every field in the model present.
		# Some fields may allow NULL values, so we may not want to include them...
		# Here, we are hiding the foreign key.
		# we can either exclude the category field from the form,
        exclude = ('bar',)
		#or specify the fields to include (i.e. not include the category field)
        fields = ('nombre','votos')

    def __init__(self, *args, **kwargs):
        super(TapaForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].label = "Nombre de la tapa:"
        self.fields['nombre'].widget.attrs.update({'class' : 'form-control'})
