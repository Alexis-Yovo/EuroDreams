import random
from datetime import datetime, timedelta
import requests
import numpy as np
from scipy.integrate import odeint

# Constante gravitationnelle
g = 9.81

# Fonction pour simuler le double pendule
def simulate_double_pendulum(L1, L2, m1, m2, tmax, dt, y0):
    """
    Simule un double pendule avec des paramètres donnés.
    
    Paramètres :
        L1, L2 : Longueurs des deux segments du pendule
        m1, m2 : Masses des deux segments du pendule
        tmax : Durée totale de la simulation (en secondes)
        dt : Pas de temps pour la simulation
        y0 : Conditions initiales [theta1, z1, theta2, z2]
    
    Retourne :
        theta1, theta2 : Angles des deux segments du pendule au fil du temps
    """
    def deriv(y, t, L1, L2, m1, m2):
        theta1, z1, theta2, z2 = y
        c, s = np.cos(theta1 - theta2), np.sin(theta1 - theta2)

        theta1_dot = z1
        z1_dot = (m2 * g * np.sin(theta2) * c - m2 * s * (L1 * z1**2 * c + L2 * z2**2) -
                  (m1 + m2) * g * np.sin(theta1)) / L1 / (m1 + m2 * s**2)

        theta2_dot = z2
        z2_dot = ((m1 + m2) * (L1 * z1**2 * s - g * np.sin(theta2) + g * np.sin(theta1) * c) +
                  m2 * L2 * z2**2 * s * c) / L2 / (m1 + m2 * s**2)

        return theta1_dot, z1_dot, theta2_dot, z2_dot

    t = np.arange(0, tmax, dt)
    sol = odeint(deriv, y0, t, args=(L1, L2, m1, m2))
    theta1, theta2 = sol[:, 0], sol[:, 2]
    return theta1, theta2

# Extraction d'une valeur chaotique du double pendule
def get_chaotic_value_from_pendulum(L1=1.0, L2=1.0, m1=1.0, m2=1.0, tmax=10, dt=0.01, y0=[np.pi - 0.1, 0.0, np.pi - 0.2, 0.0]):
    """
    Extrait une valeur chaotique de la simulation du double pendule.
    
    Retourne :
        float : Dernière valeur de l'angle theta2 comme source de chaos.
    """
    _, theta2 = simulate_double_pendulum(L1, L2, m1, m2, tmax, dt, y0)
    chaotic_value = theta2[-1]  # Utiliser la dernière valeur de theta2
    return chaotic_value

# Fonction pour générer les numéros Eurodreams
def generate_eurodreams_numbers(seed):
    """
    Génère les numéros Eurodreams à partir d'une graine donnée.
    Retourne une liste triée des 6 numéros principaux (1-40) et un numéro bonus (1-5).
    """
    random.seed(seed)
    main_numbers = sorted(random.sample(range(1, 41), 6))  # Tirage sans doublons
    bonus_number = random.randint(1, 5)
    return main_numbers, [bonus_number]

# Création de la seed combinée
def create_combined_seed(current_time_seed, weather_seed):
    """
    Crée une seed combinée en intégrant la valeur chaotique du double pendule.
    
    Retourne :
        int : Seed finale pour le générateur aléatoire.
    """
    chaotic_value = get_chaotic_value_from_pendulum()  # Valeur chaotique du double pendule
    combined_seed = hash(weather_seed) + current_time_seed + int(abs(chaotic_value) * 1e6)  # Conversion en entier
    return combined_seed

# Fonction pour obtenir les données météorologiques via l'API OpenWeatherMap
def get_weather_data(city, postal_code, api_key):
    """
    Récupère les données météo d'une ville via l'API OpenWeatherMap.
    Retourne les données sous forme de dictionnaire.
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&zip={postal_code},fr&appid={api_key}&units=metric&lang=fr"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erreur lors de la récupération des données météo : {response.status_code}")

# Fonction pour récupérer l'état de vigilance via un input
def get_vigilance_status():
    """
    Demande à l'utilisateur s'il se trouve en zone de vigilance.
    Retourne une chaîne descriptive ou "Pas de vigilance."
    """
    vigilance = input("Êtes-vous en zone de vigilance (oui/non)? ").lower()
    if vigilance == 'oui':
        color = input("Quelle est la couleur de la vigilance (Jaune, Orange, Rouge)? ").capitalize()
        alert_type = input("Quel type de vigilance (vent violent, orages, etc.)? ").lower()
        return f"Zone de vigilance : {color}, Type : {alert_type}"
    return "Pas de vigilance."

# Fonction pour obtenir le jour de la semaine
def get_weekday():
    """
    Retourne le jour de la semaine actuel au format abrégé (Lun, Mar, Mer, etc.).
    """
    weekdays = {
        "Monday": "Lun",
        "Tuesday": "Mar",
        "Wednesday": "Mer",
        "Thursday": "Jeu",
        "Friday": "Ven",
        "Saturday": "Sam",
        "Sunday": "Dim"
    }
    return weekdays.get(datetime.now().strftime("%A"), "Inconnu")

# Fonction pour calculer le prochain tirage
def next_weekday(target_weekday):
    """
    Calcule la date du prochain tirage Eurodreams (lundi ou jeudi).
    Retourne un objet datetime représentant cette date.
    """
    today = datetime.now()
    days_ahead = target_weekday - today.weekday()
    if days_ahead <= 0:  # Si le jour est déjà passé cette semaine
        days_ahead += 7
    next_draw_day = today + timedelta(days=days_ahead)
    return next_draw_day.replace(hour=20, minute=30, second=0, microsecond=0)

# Programme principal
if __name__ == "__main__":
    try:
        # Demander à l'utilisateur la ville, le code postal et l'API key
        city = input("Entrez la ville : ")
        postal_code = input("Entrez le code postal : ")
        api_key = "ecec2c207dd869ef770284f8efd147b2"  # Remplacez ceci par votre clé API OpenWeatherMap
        
        # Obtenir les données météo une seule fois
        weather_data = get_weather_data(city, postal_code, api_key)
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        precipitation = weather_data.get('rain', {}).get('1h', 0)  # Précipitations sur la dernière heure (en mm)
        weather_condition = weather_data['weather'][0]['description']  # Condition météo
        
        # Créer une graine unique à partir des données météo
        weather_seed = f"{temperature:.0f}{humidity}{precipitation}{weather_condition}".encode('utf-8')
        
        # Demander à l'utilisateur s'il veut jouer le lundi ou le jeudi
        day_of_week = input("Voulez-vous jouer le lundi ou le jeudi ? (lundi/jeudi) : ").strip().lower()
        if day_of_week not in ['lundi', 'jeudi']:
            print("Choix invalide. Veuillez entrer 'lundi' ou 'jeudi'.")
            exit()
        
        # Calculer la date du prochain lundi ou jeudi
        target_weekday = 0 if day_of_week == 'lundi' else 3  # 0 pour Lundi, 3 pour Jeudi
        next_draw_date = next_weekday(target_weekday)
        
        # Obtenir l'heure actuelle au format hh:mm:ss
        current_datetime = datetime.now()
        current_date = current_datetime.strftime("%d/%m/%Y")
        current_time = current_datetime.strftime("%H:%M:%S")
        
        # Afficher les informations générales
        print(f"""
---------------------------------------------------------------------------------------------
Jour de la semaine     : {get_weekday()}
Date du jour           : {current_date}
Heure actuelle         : {current_time}
Prochain tirage        : {day_of_week.capitalize()} {next_draw_date.strftime('%d/%m/%Y')} à 20:30
---------------------------------------------------------------------------------------------
Ville                  : {city}, Code Postal : {postal_code}
Conditions météo       : {weather_condition.capitalize()}
Température            : {temperature}°C
Humidité               : {humidity}%
Précipitations         : {precipitation} mm
{get_vigilance_status()}
---------------------------------------------------------------------------------------------
""")
        
        # Répéter les tirages d'essai 47 fois
        all_trial_results = []
        for i in range(47):
            # Graine basée sur la date et l'heure actuelles + itération
            current_time_seed = int(current_datetime.strftime("%d%H%M%S%f")) + i  # Ajout de l'itération
            
            # Créer la seed combinée avec le double pendule
            combined_seed = create_combined_seed(current_time_seed, weather_seed)
            
            # Générer les numéros de loterie
            main_numbers, bonus_numbers = generate_eurodreams_numbers(combined_seed)
            
            # Stocker les résultats
            all_trial_results.append((main_numbers, bonus_numbers))
        
        # Afficher tous les résultats des tirages d'essai
        print("\nRésultats des 47 tirages d'essai :")
        for idx, (main_numbers, bonus_numbers) in enumerate(all_trial_results, start=1):
            print(f"Tirage d'essai #{idx:02} - Numéros principaux : {main_numbers}, Bonus : {bonus_numbers}")
        
        # Générer le tirage officiel après les essais
        official_time_seed = int(current_datetime.strftime("%d%H%M%S%f")) + 47  # Une graine différente pour le tirage officiel
        official_seed = create_combined_seed(official_time_seed, weather_seed)
        official_main_numbers, official_bonus_numbers = generate_eurodreams_numbers(official_seed)
        
        # Afficher le tirage officiel
        print("\nTIRAGE OFFICIEL EURODREAMS :")
        print(f"Tirage officiel - Numéros principaux : {official_main_numbers}, Bonus : {official_bonus_numbers}")
    
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
