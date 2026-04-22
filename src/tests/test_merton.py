from pricers.monte_carlo import MonteCarloJumpDiffusionPricer

# Paramètres de l'option et du modèle
S = 100           # Prix actuel de l'actif
K = 100           # Prix d'exercice (strike)
T = 1             # Temps jusqu'à l'expiration (1 an)
r = 0.05          # Taux d'intérêt sans risque
sigma = 0.2       # Volatilité (diffusion)
lambda_ = 1       # Intensité des sauts (1 saut par an en moyenne)
mu_J = -0.1       # Moyenne des sauts (lognormale)
sigma_J = 0.3     # Volatilité des sauts (lognormale)

# Créer une instance du pricer
pricer = MonteCarloJumpDiffusionPricer(
    S=S, 
    K=K, 
    T=T, 
    r=r, 
    sigma=sigma, 
    lambda_=lambda_, 
    mu_J=mu_J, 
    sigma_J=sigma_J,
    num_simulations=100,
    num_steps=252
)

# Effectuer la simulation et la comparaison
print("=" * 60)
print("Simulation du mod�le de Merton (Diffusion avec Sauts)")
print("=" * 60)
print(f"Param�tres:")
print(f"  Spot (S):              {S}")
print(f"  Strike (K):            {K}")
print(f"  Temps (T):             {T} an")
print(f"  Taux sans risque (r):  {r}")
print(f"  Volatilit� (sigma):    {sigma}")
print(f"  Intensit� sauts (?):   {lambda_}")
print(f"  Moyenne sauts (�J):    {mu_J}")
print(f"  Vol. sauts (sJ):       {sigma_J}")
print("=" * 60)

results = pricer.compare_prices()

print(f"\nR�sultats:")
print(f"  Prix Monte Carlo (Merton):   ${results['monte_carlo_price']:.4f}")
print(f"  Prix Black-Scholes:          ${results['black_scholes_price']:.4f}")
print(f"  Diff�rence:                  ${results['difference']:.4f}")
print(f"  �cart relatif:               {(results['difference'] / results['black_scholes_price'] * 100):.2f}%")
print("=" * 60)
