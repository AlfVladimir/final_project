from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.forms.widgets import NumberInput

from tmapp.models import Project, Sprint, Status, Task


class NewSprintForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        date_start = cleaned_data.get("date_start")
        date_end = cleaned_data.get("date_end")

        if date_start > date_end:
            raise ValidationError("Дата начала должна быть больше даты окончания!")

        return cleaned_data

    class Meta:
        model = Sprint
        fields = (
            "name",
            "date_start",
            "date_end",
            "project",
        )

    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    date_start = forms.DateField(
        widget=NumberInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        )
    )

    date_end = forms.DateField(
        widget=NumberInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        )
    )


class EditSprintForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        date_start = cleaned_data.get("date_start")
        date_end = cleaned_data.get("date_end")

        if date_start > date_end:
            raise ValidationError("Дата начала должна быть больше даты окончания!")

        return cleaned_data

    class Meta:
        model = Sprint
        fields = (
            "name",
            "date_start",
            "date_end",
        )

    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    date_start = forms.DateField(
        widget=NumberInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        )
    )

    date_end = forms.DateField(
        widget=NumberInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        )
    )


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            "name",
            "content",
            "is_complete",
        )

    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": "5",
                "class": "form-control",
            }
        )
    )


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = (
            "name",
            "parent_status",
        )

    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    parent_status = forms.ModelChoiceField(
        queryset=Status.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "name",
            "content",
            "is_complete",
            "status",
            "executor",
            "project",
            "sprint",
        )

    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": "5",
                "class": "form-control",
            }
        )
    )

    status = forms.ModelChoiceField(
        queryset=Status.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    is_complete = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

    executor = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    sprint = forms.ModelChoiceField(
        queryset=Sprint.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Пользователь", "class": "form-control"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Пароль", "class": "form-control"}
        )
    )


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Ваше имя", "class": "form-control"}
        )
    )
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "E-mail",
                "class": "form-control",
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Пароль", "class": "form-control"}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Повторите пароль", "class": "form-control"}
        )
    )
