
from django.core.exceptions import ValidationError
import re

class PasswordComplexityValidator:
    """Enforce at least one uppercase, one lowercase, one digit and one special char."""
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError('La contraseña debe incluir al menos una letra mayúscula.')
        if not re.search(r'[a-z]', password):
            raise ValidationError('La contraseña debe incluir al menos una letra minúscula.')
        if not re.search(r'\d', password):
            raise ValidationError('La contraseña debe incluir al menos un número.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>\-_=+\[\]\\/;\']', password):
            raise ValidationError('La contraseña debe incluir al menos un carácter especial.')
    def get_help_text(self):
        return 'Debe tener mínimo 10 caracteres con mayúsculas, minúsculas, números y un carácter especial.'
