from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def is_recent(date_ajoutee, days=2):
    """Vérifie si une date est récente (dans les X derniers jours) - par défaut 2 jours"""
    if not date_ajoutee:
        return False
    
    # Convertir en datetime si c'est une date
    if hasattr(date_ajoutee, 'date'):
        date_ajoutee = date_ajoutee
    
    # Calculer la différence avec maintenant
    maintenant = timezone.now()
    if hasattr(date_ajoutee, 'tzinfo') and date_ajoutee.tzinfo:
        delta = maintenant - date_ajoutee
    else:
        # Si pas de timezone, utiliser la date
        from datetime import date
        if isinstance(date_ajoutee, date):
            delta = timezone.now().date() - date_ajoutee
        else:
            delta = maintenant - date_ajoutee
    
    # Vérifier si c'est dans les X derniers jours
    if hasattr(delta, 'days'):
        return delta.days <= days
    return False

