# -*- coding: utf-8 -*-
import numpy as np
from models.jump_diffusion import MertonJumpDiffusion
from models.black_scholes import BlackScholes


class MonteCarloJumpDiffusionPricer:
    """
    Pricer pour les options utilisant Monte Carlo avec le modele de Merton
    """

    def __init__(self, S, K, T, r, sigma, lambda_, mu_J, sigma_J, num_simulations=10000, num_steps=252):
        """
        Initialise le pricer

        Parametres:
            S (float): Prix actuel de l'actif
            K (float): Prix d'exercice (strike)
            T (float): Temps jusqu'a l'expiration (en annees)
            r (float): Taux d'interet sans risque (annuel)
            sigma (float): Volatilite de l'actif (annuelle)
            lambda_ (float): Intensite des sauts
            mu_J (float): Moyenne des sauts
            sigma_J (float): Volatilite des sauts
            num_simulations (int): Nombre de simulations Monte Carlo
            num_steps (int): Nombre d'etapes temporelles
        """
        self.merton_model = MertonJumpDiffusion(
            S, K, T, r, sigma, lambda_, mu_J, sigma_J, 
            num_simulations, num_steps
        )
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma

    def price_call_mc(self):
        """
        Calcule le prix du call europeen par Monte Carlo

        Retour:
            float: Prix estime du call
        """
        paths = self.merton_model.simulate_paths()
        payoffs = np.maximum(paths[:, -1] - self.K, 0)
        price = np.exp(-self.r * self.T) * np.mean(payoffs)
        return price

    def price_call_bs(self):
        """
        Calcule le prix du call selon Black-Scholes pour comparaison

        Retour:
            float: Prix du call selon BS
        """
        bs = BlackScholes(self.S, self.K, self.T, self.r, self.sigma)
        return bs.call_price()

    def compare_prices(self):
        """
        Compare les prix Monte Carlo et Black-Scholes

        Retour:
            dict: Prix MC, BS et difference
        """
        mc_price = self.price_call_mc()
        bs_price = self.price_call_bs()
        return {
            "monte_carlo_price": mc_price,
            "black_scholes_price": bs_price,
            "difference": mc_price - bs_price
        }
