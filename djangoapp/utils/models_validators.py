from django.core.exceptions import ValidationError

def validate_png(value):
    if not value.name.lower().endswith('.png'):
        raise ValidationError('Imagem precisa ser PNG')