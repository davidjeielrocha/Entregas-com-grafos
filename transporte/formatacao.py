"""Funções auxiliares de formatação."""


def brl(valor):
    """Formata número no padrão monetário brasileiro: 860.0 -> 'R$ 860,00'."""
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def num(valor):
    """Exibe 8.0 como '8' e 7.5 como '7,5'."""
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    return str(valor).replace(".", ",")
