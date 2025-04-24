from django import template

register = template.Library()

@register.filter
def format_montant(value):
    """
    Formate un montant avec des points comme séparateurs des milliers et une seule décimale après la virgule.
    """
    try:
        value = float(value)  # Convertit la valeur en flottant
        formatted = f"{value:,.2f}"  # Formate avec des séparateurs de milliers (,) et une décimale
        # Séparer les parties des milliers et des décimales
        parts = formatted.split(".")
        parts[0] = parts[0].replace(",", ".")  # Remplace les ',' dans la partie des milliers par des '.'
        return ",".join(parts)  # Rejoindre avec ',' pour les décimales
    except (ValueError, TypeError):
        return value  # Retourne la valeur brute si elle n'est pas valide
