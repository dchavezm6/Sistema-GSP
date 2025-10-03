from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML, Field, Div
from .models import ServiceRequest, RequestImage, RequestComment, ServiceType, ServiceArea


class ServiceRequestForm(forms.ModelForm):
    """Formulario para crear solicitudes de servicio"""

    class Meta:
        model = ServiceRequest
        fields = [
            'service_type', 'service_area', 'request_type', 'title',
            'description', 'address', 'priority', 'citizen_phone',
            'citizen_email', 'notes'
        ]

        widgets = {
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'service_area': forms.Select(attrs={'class': 'form-control'}),
            'request_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título descriptivo de la solicitud'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describa detalladamente el problema o solicitud',
                'rows': 4
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección exacta donde se presenta el problema',
                'rows': 3
            }),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'citizen_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+502 1234-5678'
            }),
            'citizen_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Información adicional (opcional)',
                'rows': 2
            }),
        }

        labels = {
            'service_type': 'Tipo de Servicio',
            'service_area': 'Área/Zona',
            'request_type': 'Tipo de Solicitud',
            'title': 'Título',
            'description': 'Descripción Detallada',
            'address': 'Dirección',
            'priority': 'Prioridad',
            'citizen_phone': 'Teléfono de Contacto',
            'citizen_email': 'Email de Contacto',
            'notes': 'Notas Adicionales',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Pre-llenar campos del usuario si están disponibles
        if self.user and not self.instance.pk:
            self.fields['citizen_phone'].initial = self.user.phone
            self.fields['citizen_email'].initial = self.user.email

        # Filtrar solo tipos de servicios activos
        self.fields['service_type'].queryset = ServiceType.objects.filter(is_active=True)
        self.fields['service_area'].queryset = ServiceArea.objects.filter(is_active=True)

        # Configurar Crispy Forms
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('service_type', css_class='col-md-6'),
                Column('service_area', css_class='col-md-6'),
            ),
            Row(
                Column('request_type', css_class='col-md-6'),
                Column('priority', css_class='col-md-6'),
            ),
            'title',
            'description',
            'address',
            Row(
                Column('citizen_phone', css_class='col-md-6'),
                Column('citizen_email', css_class='col-md-6'),
            ),
            'notes',
            HTML('<div class="alert alert-info mt-3">'),
            HTML(
                '<i class="bi bi-info-circle"></i> <strong>Importante:</strong> Después de crear la solicitud podrás subir fotografías como evidencia.'),
            HTML('</div>'),
            HTML('<div class="d-grid mt-4">'),
            Submit('submit', 'Crear Solicitud', css_class='btn btn-primary btn-lg'),
            HTML('</div>'),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.citizen = self.user
        if commit:
            instance.save()
        return instance


class RequestImageForm(forms.ModelForm):
    """Formulario para subir imágenes a solicitudes"""

    class Meta:
        model = RequestImage
        fields = ['image', 'description', 'is_before']

        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la imagen'
            }),
            'is_before': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'image': 'Imagen',
            'description': 'Descripción',
            'is_before': 'Es imagen antes del trabajo',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.request_obj = kwargs.pop('request_obj', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'image',
            'description',
            Field('is_before', wrapper_class='form-check'),
            HTML('<div class="d-grid mt-3">'),
            Submit('submit', 'Subir Imagen', css_class='btn btn-success'),
            HTML('</div>'),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.uploaded_by = self.user
        if self.request_obj:
            instance.request = self.request_obj
        if commit:
            instance.save()
        return instance


class RequestCommentForm(forms.ModelForm):
    """Formulario para agregar comentarios a solicitudes"""

    class Meta:
        model = RequestComment
        fields = ['comment', 'is_internal']

        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escriba su comentario...',
                'rows': 3
            }),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'comment': 'Comentario',
            'is_internal': 'Comentario interno (solo personal municipal)',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.request_obj = kwargs.pop('request_obj', None)
        super().__init__(*args, **kwargs)

        # Si el usuario es ciudadano, no mostrar opción de comentario interno
        if self.user and self.user.role == 'CITIZEN':
            self.fields['is_internal'].widget = forms.HiddenInput()
            self.fields['is_internal'].initial = False

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'comment',
            Field('is_internal', wrapper_class='form-check') if self.user and self.user.role != 'CITIZEN' else HTML(''),
            HTML('<div class="d-grid mt-3">'),
            Submit('submit', 'Agregar Comentario', css_class='btn btn-primary'),
            HTML('</div>'),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if self.request_obj:
            instance.request = self.request_obj
        if commit:
            instance.save()
        return instance


class RequestStatusForm(forms.ModelForm):
    """Formulario para que el personal municipal actualice el estado"""

    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Motivo del cambio de estado',
            'rows': 3
        }),
        label='Motivo del Cambio',
        required=True
    )

    class Meta:
        model = ServiceRequest
        fields = ['status', 'assigned_to', 'expected_completion']

        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'expected_completion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'estimated_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }

        labels = {
            'status': 'Estado',
            'assigned_to': 'Asignar a',
            'expected_completion': 'Fecha Estimada de Finalización',
            'estimated_cost': 'Costo Estimado (Q)',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filtrar usuarios técnicos y encargados para asignación
        from apps.authentication.models import User
        self.fields['assigned_to'].queryset = User.objects.filter(
            role__in=['TECHNICIAN', 'MANAGER']
        ).filter(is_active=True)
        self.fields['assigned_to'].empty_label = "Sin asignar"

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('status', css_class='col-md-6'),
                Column('assigned_to', css_class='col-md-6'),
            ),
            Row(
                Column('expected_completion', css_class='col-md-6'),
            ),
            'reason',
            HTML('<div class="d-grid mt-3">'),
            Submit('submit', 'Actualizar Estado', css_class='btn btn-warning'),
            HTML('</div>'),
        )


class RequestSearchForm(forms.Form):
    """Formulario para buscar solicitudes"""

    SEARCH_CHOICES = [
        ('', 'Todos los estados'),
        ('PENDING', 'Pendiente'),
        ('IN_REVIEW', 'En Revisión'),
        ('APPROVED', 'Aprobada'),
        ('IN_PROGRESS', 'En Proceso'),
        ('COMPLETED', 'Completada'),
        ('REJECTED', 'Rechazada'),
        ('CANCELLED', 'Cancelada'),
    ]

    search_term = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por ticket, título o descripción...'
        }),
        label='Buscar'
    )

    status = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Estado'
    )

    service_type = forms.ModelChoiceField(
        queryset=ServiceType.objects.filter(is_active=True),
        required=False,
        empty_label='Todos los servicios',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de Servicio'
    )

    service_area = forms.ModelChoiceField(
        queryset=ServiceArea.objects.filter(is_active=True),
        required=False,
        empty_label='Todas las áreas',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Área'
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Desde'
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Hasta'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Row(
                Column('search_term', css_class='col-md-4'),
                Column('status', css_class='col-md-2'),
                Column('service_type', css_class='col-md-3'),
                Column('service_area', css_class='col-md-3'),
            ),
            Row(
                Column('date_from', css_class='col-md-6'),
                Column('date_to', css_class='col-md-6'),
            ),
            HTML('<div class="d-grid mt-3">'),
            Submit('submit', 'Buscar', css_class='btn btn-outline-primary'),
            HTML('</div>'),
        )