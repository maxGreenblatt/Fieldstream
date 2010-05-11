from django import forms

class LoginForm(forms.Form):
  username = forms.CharField(max_length=30)
  password = forms.CharField(max_length=30)

class UserRegistrationForm(forms.Form):
  username = forms.CharField(max_length=30)
  password = forms.CharField(max_length=30, widget=forms.PasswordInput(render_value=False))
  confirm_Password = forms.CharField(max_length=30, widget=forms.PasswordInput(render_value=False))
  first_Name = forms.CharField(max_length=30, required=False)
  last_Name = forms.CharField(max_length=30, required=False)
  email = forms.EmailField(max_length=30)

class UserProfUpdateForm(forms.Form):
  old_Password = forms.CharField(max_length=30, widget=forms.PasswordInput(render_value=False))
  new_Password = forms.CharField(max_length=30, widget=forms.PasswordInput(render_value=False))
  confirm_Password = forms.CharField(max_length=30, widget=forms.PasswordInput(render_value=False))
  first_Name = forms.CharField(max_length=30, required=False)
  last_Name = forms.CharField(max_length=30, required=False)
  email = forms.EmailField(max_length=30)

class SensorNodeForm(forms.Form):
  sensor_Name = forms.CharField(max_length=30)
  hidden_id = forms.CharField(max_length=30, required = False, widget=forms.HiddenInput())

class WSSForm(forms.Form):
  wave_Segment_Series_Name = forms.CharField(max_length=30)
  hidden_id = forms.CharField(max_length=30, required = False, widget=forms.HiddenInput())

class SensorChannelForm(forms.Form):
  channel_Name = forms.CharField(max_length=30)
  sensor_Node = forms.ChoiceField()
  channel_Placement = forms.ChoiceField(required=False)
  non_Numeric = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'onClick': 'showHideField()'}))
  non_Numeric_Options = forms.CharField(max_length=1024, required=False)
  hidden_id = forms.CharField(max_length=30, required = False, widget=forms.HiddenInput())

class SeriesChannelMapForm(forms.Form):
  wave_Segment_Series = forms.ChoiceField()
  sensor_Channel = forms.ChoiceField()
  hidden_id = forms.CharField(max_length=30, required = False, widget=forms.HiddenInput())

class RulesForm(forms.Form):
  hidden_id = forms.CharField(max_length=30, required = False, widget=forms.HiddenInput())
  condition = forms.CharField(required=True, widget=forms.Textarea())
  action = forms.ChoiceField(choices=(('Allow', 'Allow'), ('Deny', 'Deny'), ('Transform', 'Transform'), ('Mapping', 'Mapping'), ('Perturb', 'Perturb'), ('Drop', 'Drop')), widget=forms.Select(attrs={'onChange': 'showHideField()'}))
  form_Type = forms.ChoiceField(choices=((0, 'Simple'), (1, 'Robust')), widget=forms.RadioSelect(attrs={'onClick': 'showHideForm()'}))
  calculation = forms.CharField(required = False, widget=forms.Textarea())
