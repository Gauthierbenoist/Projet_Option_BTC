import numpy as np
from scipy.stats import norm
from models.utils import calculate_d1_d2


class BlackScholes:
    """
    Classe pour calculer les prix et greeks des options call et put selon le modèle Black-Scholes
    """
    
    def __init__(self, S, K, T, r, sigma):
        """
        Initialise les paramètres de l'option
        
        Paramètres:
            S (float): Prix actuel de l'actif
            K (float): Prix d'exercice (strike)
            T (float): Temps jusqu'à l'expiration (en années)
            r (float): Taux d'intérêt sans risque (annuel)
            sigma (float): Volatilité de l'actif (annuelle)
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.d1, self.d2 = calculate_d1_d2(S, K, T, r, sigma)
    
    def call_price(self):
        """
        Calcule le prix d'un call option
        
        Retour:
            float: Prix du call
        """
        call_price = self.S * norm.cdf(self.d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2)
        return call_price
    
    def put_price(self):
        """
        Calcule le prix d'un put option
        
        Retour:
            float: Prix du put
        """
        put_price = self.K * np.exp(-self.r * self.T) * norm.cdf(-self.d2) - self.S * norm.cdf(-self.d1)
        return put_price
    
    def greeks(self):
        """
        Calcule les greeks (sensibilités) des options
        
        Retour:
            dict: Dictionnaire contenant delta, gamma, vega, theta, rho
        """
        # Densité de probabilité normale standard
        pdf_d1 = norm.pdf(self.d1)
        
        # Delta : sensibilité au prix de l'actif
        delta = norm.cdf(self.d1)
        
        # Gamma : sensibilité au delta (courbure)
        gamma = pdf_d1 / (self.S * self.sigma * np.sqrt(self.T))
        
        # Vega : sensibilité à la volatilité (en points de volatilité = /100)
        vega = self.S * pdf_d1 * np.sqrt(self.T) / 100
        
        # Theta : sensibilité au temps (décroissance temporelle, par jour)
        theta = (-self.S * pdf_d1 * self.sigma / (2 * np.sqrt(self.T)) - self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2)) / 365
        
        # Rho : sensibilité au taux d'intérêt (en points de taux = /100)
        rho = self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(self.d2) / 100
        
        return {
            "delta": delta,
            "gamma": gamma,
            "vega": vega,
            "theta": theta,
            "rho": rho
        }
