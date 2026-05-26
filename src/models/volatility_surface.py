"""
Module pour calculer la surface de volatilité implicite (Volatility Surface)
à partir des données d'options nettoyées.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from scipy.optimize import brentq
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from models.black_scholes import BlackScholes
from models.utils import calculate_d1_d2


def black_scholes_call(S, K, T, r, sigma):
    """
    Calcule le prix d'un call avec Black-Scholes
    """
    if T <= 0 or sigma <= 0:
        return None
    
    bs = BlackScholes(S, K, T, r, sigma)
    return bs.call_price()


def black_scholes_put(S, K, T, r, sigma):
    """
    Calcule le prix d'un put avec Black-Scholes
    """
    if T <= 0 or sigma <= 0:
        return None
    
    bs = BlackScholes(S, K, T, r, sigma)
    return bs.put_price()


def implied_volatility(market_price, S, K, T, r, option_type='call'):
    """
    Calcule la volatilité implicite en inversant Black-Scholes
    
    Paramètres:
        market_price (float): Prix de marché de l'option
        S (float): Prix du sous-jacent
        K (float): Prix d'exercice
        T (float): Temps jusqu'à l'expiration (en années)
        r (float): Taux sans risque
        option_type (str): 'call' ou 'put'
    
    Retour:
        float: Volatilité implicite
    """
    if T <= 0 or market_price <= 0:
        return None
    
    # Prix intrinsèque
    intrinsic = max(0, S - K) if option_type == 'call' else max(0, K - S)
    
    # Si le prix est inférieur au prix intrinsique, impossible à pricing
    if market_price < intrinsic * 0.95:
        return None
    
    def objective(sigma):
        if option_type == 'call':
            return black_scholes_call(S, K, T, r, sigma) - market_price
        else:
            return black_scholes_put(S, K, T, r, sigma) - market_price
    
    try:
        # Recherche de la volatilité implicite entre 1% et 500%
        iv = brentq(objective, 0.01, 5.0, xtol=1e-6)
        return iv
    except (ValueError, RuntimeError):
        return None


def load_clean_options(date_filter=None):
    """
    Charge les données d'options nettoyées
    
    Paramètres:
        date_filter (str): Filtre optionnel sur la date (ex: '2017-02-02')
    
    Retour:
        DataFrame: Données d'options
    """
    df = pd.read_csv(r"c:\Users\gauth\Desktop\Projets python\src\data\clean_options.csv")
    
    if date_filter:
        df = df[df['datetime'].str.contains(date_filter)]
    
    return df


def compute_volatility_surface(df, r=0.02):
    """
    Calcule la surface de volatilité implicite (version optimisée)
    
    Paramètres:
        df (DataFrame): Données d'options avec colonnes datetime, maturity_date, strike, index_price, iv, option_type, T
        r (float): Taux sans risque
    
    Retour:
        DataFrame: Surface de volatilité avec strike, T, iv
    """
    # Filtrer les données invalides
    df_clean = df[(df['iv'] > 0) & (df['T'] > 0)].copy()
    
    # Normaliser le strike par rapport au prix du sous-jacent (moneyness)
    df_clean['moneyness'] = df_clean['strike'] / df_clean['index_price']
    
    # Calculer le log-moneyness
    df_clean['log_moneyness'] = np.log(df_clean['moneyness'])
    
    # Supprimer les outliers:
    # - Moneyness trop éloigné du spot (0.5 à 2.0)
    # - IV aberrante (> 200% ou < 1%)
    df_clean = df_clean[(df_clean['moneyness'] >= 0.5) & (df_clean['moneyness'] <= 2.0)]
    df_clean = df_clean[(df_clean['iv'] >= 0.01) & (df_clean['iv'] <= 2.0)]
    
    # Supprimer les T trop petits (moins d'une semaine)
    df_clean = df_clean[df_clean['T'] >= 7/365]
    
    print(f"Après suppression des outliers: {len(df_clean)} options")
    
    # Grouper par strike et T pour obtenir une IV moyenne
    vol_surface = df_clean.groupby(['strike', 'T']).agg({
        'iv': 'mean',
        'maturity_date': 'first',
        'option_type': 'first',
        'index_price': 'first',
        'moneyness': 'mean',
        'log_moneyness': 'mean'
    }).reset_index()
    
    vol_surface.columns = ['strike', 'T', 'iv', 'maturity_date', 'option_type', 'S', 'moneyness', 'log_moneyness']
    
    return vol_surface


def plot_volatility_surface(vol_surface, title="Volatility Surface"):
    """
    Affiche la surface de volatilité implicite en 3D
    
    Paramètres:
        vol_surface (DataFrame): Surface de volatilité
        title (str): Titre du graphique
    """
    # Grouper les maturités en buckets (par semaine)
    vol_surface = vol_surface.copy()
    vol_surface['T_bucket'] = (vol_surface['T'] * 52).round() / 52  # Arrondir à la semaine près
    
    # Grouper par moneyness et T_bucket pour avoir une surface
    pivot = vol_surface.pivot_table(values='iv', index='moneyness', columns='T_bucket', aggfunc='mean')
    
    # Trier et remplir les valeurs manquantes
    pivot = pivot.sort_index().sort_index(axis=1)
    pivot = pivot.ffill().bfill()
    
    # Filtrer pour avoir une surface avec suffisamment de données
    min_strikes = 5
    valid_cols = pivot.columns[pivot.notna().sum() >= min_strikes]
    pivot = pivot[valid_cols]
    
    # Limiter le nombre de maturités pour un affichage propre
    pivot = pivot.iloc[:, :20]  # Prendre les 20 premières maturités
    
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    K_vals = pivot.index.values
    T_vals = pivot.columns.values
    K_mesh, T_mesh = np.meshgrid(T_vals, K_vals)
    IV_mesh = pivot.values
    
    surf = ax.plot_surface(K_mesh, T_mesh, IV_mesh, cmap='viridis', alpha=0.9, edgecolor='none')
    
    ax.set_xlabel('Temps jusqu\'à maturité (années)')
    ax.set_ylabel('Moneyness (K/S)')
    ax.set_zlabel('Volatilité Implicite')
    ax.set_title(title)
    
    # Ajuster l'angle de vue
    ax.view_init(elev=25, azim=45)
    
    fig.colorbar(surf, shrink=0.5, aspect=10, label='IV')
    plt.tight_layout()
    plt.show()


def plot_vol_smile(vol_surface, T_value, title="Vol Smile"):
    """
    Affiche le vol smile pour une maturité donnée
    
    Paramètres:
        vol_surface (DataFrame): Surface de volatilité
        T_value (float): Maturité souhaitée
        title (str): Titre du graphique
    """
    # Trouver la maturité la plus proche
    closest_T = min(vol_surface['T'].unique(), key=lambda x: abs(x - T_value))
    
    data = vol_surface[abs(vol_surface['T'] - closest_T) < 0.01]
    
    plt.figure(figsize=(10, 6))
    plt.plot(data['strike'], data['iv'], 'bo-', label=f'T ≈ {closest_T:.4f} ans')
    plt.xlabel('Strike')
    plt.ylabel('Volatilité Implicite')
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    # Charger toutes les données d'options (pas de filtre de date)
    print("Chargement de toutes les données d'options...")
    df = load_clean_options()
    
    print(f"Nombre d'options total: {len(df)}")
    print(f"Strike min: {df['strike'].min()}, max: {df['strike'].max()}")
    print(f"Nombre de dates uniques: {df['datetime'].str[:10].nunique()}")
    print(f"Nombre de maturités uniques: {df['maturity_date'].nunique()}")
    
    # Calculer la surface de volatilité
    print("\nCalcul de la surface de volatilité...")
    vol_surface = compute_volatility_surface(df)
    
    print(f"Surface calculée: {len(vol_surface)} points")
    print(f"Nombre de strikes uniques: {vol_surface['strike'].nunique()}")
    print(f"Nombre de maturités uniques: {vol_surface['T'].nunique()}")
    print(vol_surface.head(10))
    
    # Afficher la surface 3D
    print("\nAffichage de la surface de volatilité...")
    plot_volatility_surface(vol_surface, "Surface de Volatilité Implicite")