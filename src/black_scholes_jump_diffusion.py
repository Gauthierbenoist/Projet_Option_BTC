# -*- coding: utf-8 -*-
import numpy as np
from scipy.stats import norm, poisson
from utils import calculate_d1_d2


class MertonJumpDiffusion:
    """
    Classe pour simuler des options européennes call selon le modèle de diffusion avec sauts de Merton
    en utilisant des simulations Monte Carlo
    """

    def __init__(self, S, K, T, r, sigma, lambda_, mu_J, sigma_J, num_simulations=10000, num_steps=252):
        """
        Initialise les paramètres de l'option et de la simulation

        Paramètres:
            S (float): Prix actuel de l'actif
            K (float): Prix d'exercice (strike)
            T (float): Temps jusqu'à l'expiration (en années)
            r (float): Taux d'intérêt sans risque (annuel)
            sigma (float): Volatilité de l'actif (annuelle)
            lambda_ (float): Intensité des sauts (nombre de sauts par unité de temps)
            mu_J (float): Moyenne des sauts (lognormale)
            sigma_J (float): Volatilité des sauts (lognormale)
            num_simulations (int): Nombre de simulations Monte Carlo
            num_steps (int): Nombre d'étapes temporelles par simulation
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.lambda_ = lambda_
        self.mu_J = mu_J
        self.sigma_J = sigma_J
        self.num_simulations = num_simulations
        self.num_steps = num_steps
        self.dt = T / num_steps

    def simulate_paths(self):
        """
        Simule les trajectoires du prix de l'actif selon le modèle de Merton

        Retour:
            np.ndarray: Matrice des trajectoires (num_simulations x num_steps+1)
        """
        paths = np.zeros((self.num_simulations, self.num_steps + 1))
        paths[:, 0] = self.S

        # Ajustement de la dérive pour compenser les sauts
        expected_jump = np.exp(self.mu_J + 0.5 * self.sigma_J**2) - 1
        drift_adjusted = (self.r - self.lambda_ * expected_jump - 0.5 * self.sigma**2) * self.dt

        for t in range(1, self.num_steps + 1):
            # Mouvement brownien
            Z = np.random.normal(0, 1, self.num_simulations)
            diffusion = self.sigma * np.sqrt(self.dt) * Z

            # Composante de sauts
            jump_sizes = np.zeros(self.num_simulations)
            num_jumps = poisson.rvs(self.lambda_ * self.dt, size=self.num_simulations)

            for i in range(self.num_simulations):
                if num_jumps[i] > 0:
                    # Taille des sauts lognormaux
                    jumps = np.random.lognormal(self.mu_J, self.sigma_J, num_jumps[i])
                    # Produit des sauts (multiplicatif)
                    jump_sizes[i] = np.prod(jumps) - 1

            # Evolution du prix
            paths[:, t] = paths[:, t-1] * np.exp(drift_adjusted + diffusion + jump_sizes)

        return paths

    def call_price_mc(self):
        """
        Calcule le prix du call europeen par Monte Carlo

        Retour:
            float: Prix estime du call
        """
        paths = self.simulate_paths()
        payoffs = np.maximum(paths[:, -1] - self.K, 0)
        price = np.exp(-self.r * self.T) * np.mean(payoffs)
        return price

    def bs_price(self):
        """
        Calcule le prix du call selon Black-Scholes pour comparaison

        Retour:
            float: Prix du call selon BS
        """
        from black_scholes import BlackScholes
        return BlackScholes(self.S, self.K, self.T, self.r, self.sigma).call_price()

    def simulate_and_compare(self):
        """
        Effectue la simulation et compare avec Black-Scholes

        Retour:
            dict: Prix MC et BS
        """
        mc_price = self.call_price_mc()
        bs_price = self.bs_price()
        return {
            "monte_carlo_price": mc_price,
            "black_scholes_price": bs_price,
            "difference": mc_price - bs_price
        }
