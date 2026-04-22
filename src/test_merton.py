from black_scholes_jump_diffusion import MertonJumpDiffusion

# Param�tres de l'option et du mod�le
S = 100           # Prix actuel de l'actif
K = 100           # Prix d'exercice (strike)
T = 1             # Temps jusqu'� l'expiration (1 an)
r = 0.05          # Taux d'int�r�t sans risque
sigma = 0.2       # Volatilit� (diffusion)
lambda_ = 1       # Intensit� des sauts (1 saut par an en moyenne)
mu_J = -0.1       # Moyenne des sauts (lognormale)
sigma_J = 0.3     # Volatilit� des sauts (lognormale)

# Cr�er une instance du mod�le
merton = MertonJumpDiffusion(
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

results = merton.simulate_and_compare()

print(f"\nR�sultats:")
print(f"  Prix Monte Carlo (Merton):   ${results['monte_carlo_price']:.4f}")
print(f"  Prix Black-Scholes:          ${results['black_scholes_price']:.4f}")
print(f"  Diff�rence:                  ${results['difference']:.4f}")
print(f"  �cart relatif:               {(results['difference'] / results['black_scholes_price'] * 100):.2f}%")
print("=" * 60)
