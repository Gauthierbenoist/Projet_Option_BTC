from src.black_scholes import BlackScholes

if __name__ == "__main__":
    # Paramètres
    S = 100        # Prix actuel de l'actif
    K = 105        # Prix d'exercice
    T = 1          # Temps jusqu'à l'expiration (1 an)
    r = 0.05       # Taux d'intérêt sans risque (5%)
    sigma = 0.2    # Volatilité (20%)
    
    # Créer une instance de BlackScholes
    bs = BlackScholes(S, K, T, r, sigma)
    
    # Calcul du prix du call et du put
    prix_call = bs.call_price()
    prix_put = bs.put_price()
    
    # Calcul des greeks
    greeks = bs.greeks()
    
    # Affichage
    print("=" * 50)
    print("MODÈLE BLACK-SCHOLES - PRICING DES OPTIONS")
    print("=" * 50)
    print(f"Prix actuel de l'actif (S):     {S}")
    print(f"Prix d'exercice (K):             {K}")
    print(f"Temps jusqu'à expiration (T):    {T} an(s)")
    print(f"Taux d'intérêt sans risque (r):  {r*100}%")
    print(f"Volatilité (σ):                  {sigma*100}%")
    print("=" * 50)
    print(f"Prix du CALL:                    ${prix_call:.2f}")
    print(f"Prix du PUT:                     ${prix_put:.2f}")
    print("=" * 50)
    
    print("\n")
    
    print("=" * 50)
    print("GREEKS - SENSIBILITÉS DES OPTIONS")
    print("=" * 50)
    print(f"Delta (Δ):    {greeks['delta']:.4f}")
    print(f"Gamma (Γ):    {greeks['gamma']:.4f}")
    print(f"Vega (ν):     {greeks['vega']:.4f}")
    print(f"Theta (Θ):    {greeks['theta']:.4f}")
    print(f"Rho (ρ):      {greeks['rho']:.4f}")
    print("=" * 50)
