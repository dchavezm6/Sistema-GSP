from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML
from .models import TaskAssignment, TaskUpdate
from apps.authentication.models import User


class TaskAssignmentForm(forms.ModelForm):
    """Formulario para crear asignaciones"""

    class Meta:
        model = TaskAssignment
        fields = ['assigned_to', 'priority', 'estimated_completion', 'estimated_hours', 'instructions']

        widgets = {
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'estimated_completion': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'estimated_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Instrucciones especiales para el técnico...'
            }),
        }

        labels = {
            'assigned_to': 'Asignar a Técnico',
            'priority': 'Prioridad',
            'estimated_completion': 'Fecha Estimada de Finalización',
            'estimated_hours': 'Horas Estimadas',
            'instructions': 'Instrucciones Especiales',
        }

    def __init__(self, *args, **kwargs):
        self.request_obj = kwargs.pop('request_obj', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filtrar solo técnicos activos
        self.fields['assigned_to'].queryset = User.objects.filter(
            role='TECHNICIAN',
            is_active=True
        )

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('assigned_to', css_class='col-md-6'),
                Column('priority', css_class='col-md-6'),
            ),
            Row(
                Column('estimated_completion', css_class='col-md-6'),
                Column('estimated_hours', css_class='col-md-6'),
            ),
            'instructions',
            HTML('<div class="d-grid mt-3">'),
            Submit('submit', 'Asignar Tarea', css_class='btn btn-primary btn-lg'),
            HTML('</div>'),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.request_obj:
            instance.request = self.request_obj
        if self.user:
            instance.assigned_by = self.user
        if commit:
            instance.save()
            # Actualizar estado de la solicitud
            self.request_obj.status = 'IN_PROGRESS'
            self.request_obj.assigned_to = instance.assigned_to
            self.request_obj.save()
        return instance


class TaskUpdateForm(forms.ModelForm):
    """Formulario para actualizar progreso de tareas"""

    class Meta:
        model = TaskUpdate
        fields = ['status', 'progress_percentage', 'description', 'hours_worked']

        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'progress_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '5'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describa el progreso realizado...'
            }),
            'hours_worked': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0'
            }),
        }

        labels = {
            'status': 'Estado Actual',
            'progress_percentage': 'Porcentaje de Progreso (%)',
            'description': 'Descripción del Progreso',
            'hours_worked': 'Horas Trabajadas',
        }

    def __init__(self, *args, **kwargs):
        self.assignment = kwargs.pop('assignment', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('status', css_class='col-md-6'),
                Column('progress_percentage', css_class='col-md-6'),
            ),
            'description',
            'hours_worked',
            HTML('<div class="d-grid mt-3">'),
            Submit('submit', 'Registrar Actualización', css_class='btn btn-success'),
            HTML('</div>'),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.assignment:
            instance.assignment = self.assignment
        if self.user:
            instance.updated_by = self.user
        if commit:
            instance.save()
            # Actualizar el estado de la asignación
            self.assignment.status = instance.status
            self.assignment.save()
        return instance


class TaskAcceptForm(forms.Form):
    """Formulario simple para aceptar tareas"""
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notas adicionales (opcional)...'
        }),
        label='Notas'
    )


class TaskCompleteForm(forms.Form):
    """Formulario para completar tareas"""
    actual_hours = forms.DecimalField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5',
            'min': '0'
        }),
        label='Horas Trabajadas'
    )

    materials_used = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ej: Tubo PVC 2", Codo 90°, Cemento PVC, etc.'
        }),
        label='Materiales Utilizados'
    )

    notes = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Resumen detallado del trabajo realizado...'
        }),
        label='Descripción del Trabajo Realizado'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'actual_hours',
            'materials_used',
            'notes',
            HTML('<div class="d-grid mt-3">'),
            Submit('submit', 'Completar Tarea', css_class='btn btn-success btn-lg'),
            HTML('</div>'),
        )