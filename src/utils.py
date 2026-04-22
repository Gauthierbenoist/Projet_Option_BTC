import numpy as np

def calculate_d1_d2(S, K, T, r, sigma):
    """
    Calcule d1 et d2 selon le modèle Black-Scholes
    
    Paramètres:
        S (float): Prix actuel de l'actif
        K (float): Prix d'exercice (strike)
        T (float): Temps jusqu'à l'expiration (en années)
        r (float): Taux d'intérêt sans risque (annuel)
        sigma (float): Volatilité de l'actif (annuelle)
    
    Retour:
        tuple: (d1, d2)
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    return d1, d2
