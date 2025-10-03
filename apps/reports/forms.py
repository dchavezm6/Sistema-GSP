from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML
from .models import CitizenSatisfaction

class ReportFilterForm(forms.Form):
    """Formulario para filtrar reportes"""
    
    REPORT_TYPE_CHOICES = [
        ('', 'Seleccione un tipo de reporte'),
        ('GENERAL', 'Reporte General'),
        ('SERVICE_TYPE', 'Por Tipo de Servicio'),
        ('AREA', 'Por Área'),
        ('TECHNICIAN', 'Rendimiento de Técnicos'),
        ('SATISFACTION', 'Satisfacción Ciudadana'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de Reporte'
    )
    
    date_from = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha Desde'
    )
    
    date_to = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha Hasta'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Valores por defecto (último mes)
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.initial.get('date_to'):
            self.initial['date_to'] = timezone.now().date()
        if not self.initial.get('date_from'):
            self.initial['date_from'] = (timezone.now() - timedelta(days=30)).date()
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'report_type',
            Row(
                Column('date_from', css_class='col-md-6'),
                Column('date_to', css_class='col-md-6'),
            ),
            HTML('<div class="d-grid mt-3">'),
            Submit('submit', 'Generar Reporte', css_class='btn btn-primary btn-lg'),
            HTML('</div>'),
        )

class SatisfactionSurveyForm(forms.ModelForm):
    """Formulario de encuesta de satisfacción"""
    
    class Meta:
        model = CitizenSatisfaction
        fields = [
            'rating', 'response_time_rating', 'quality_rating', 
            'technician_rating', 'comments', 'would_recommend'
        ]
        
        widgets = {
            'rating': forms.RadioSelect(choices=CitizenSatisfaction.RATING_CHOICES),
            'response_time_rating': forms.RadioSelect(choices=CitizenSatisfaction.RATING_CHOICES),
            'quality_rating': forms.RadioSelect(choices=CitizenSatisfaction.RATING_CHOICES),
            'technician_rating': forms.RadioSelect(choices=CitizenSatisfaction.RATING_CHOICES),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Comparta sus comentarios y sugerencias...'
            }),
            'would_recommend': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        labels = {
            'rating': 'Calificación General del Servicio',
            'response_time_rating': 'Tiempo de Respuesta',
            'quality_rating': 'Calidad del Trabajo',
            'technician_rating': 'Desempeño del Técnico',
            'comments': 'Comentarios Adicionales',
            'would_recommend': '¿Recomendaría este servicio?',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<div class="mb-4">'),
            HTML('<h5>Calificación General</h5>'),
            'rating',
            HTML('</div>'),
            HTML('<div class="mb-4">'),
            HTML('<h5>Tiempo de Respuesta</h5>'),
            'response_time_rating',
            HTML('</div>'),
            HTML('<div class="mb-4">'),
            HTML('<h5>Calidad del Trabajo Realizado</h5>'),
            'quality_rating',
            HTML('</div>'),
            HTML('<div class="mb-4">'),
            HTML('<h5>Desempeño del Técnico</h5>'),
            'technician_rating',
            HTML('</div>'),
            'comments',
            HTML('<div class="form-check mb-3">'),
            'would_recommend',
            HTML('</div>'),
            HTML('<div class="d-grid">'),
            Submit('submit', 'Enviar Evaluación', css_class='btn btn-success btn-lg'),
            HTML('</div>'),
        )