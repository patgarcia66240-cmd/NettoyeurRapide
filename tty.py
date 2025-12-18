import requests
import os
import time

ELEVENLABS_API_KEY = "sk_25d7e9a8061625eef2b8f143cb394c7f394e2ec7101d9a44"
#rachel="EXAVITQu4vr4xnSDxMaL"

# Liste de voix masculines standard à tester
MALE_VOICES = [
    "pNInz6obpgDQGcFmaJgB",  # Adam
    "pqHfZKP75CvOl18yl7RD",  # Sam
    "21m00Tcm4TlvDq8ikWAM",  # Adam (préréglage)
    "AZnzlk1XvdvUeBnXmlld",  # Arnold
    "CYw3yjEWRBKyiXAS3LzZ",  # Domi
]

# Voice masculine par défaut
VOICE_ID = MALE_VOICES[0]  # Adam - première voix masculine par défaut  

OUTPUT_DIR = "tts_output"


def test_voice_available(voice_id: str) -> bool:
    """Teste si une voix est disponible avec l'API"""
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": ELEVENLABS_API_KEY}
        response = requests.get(url + "/settings", headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False

def get_working_voice_id() -> str:
    """Retourne un ID de voix masculine qui fonctionne"""
    for voice_id in MALE_VOICES:
        if test_voice_available(voice_id):
            print(f"✅ Utilisation de la voix: {voice_id}")
            return voice_id

    # Si aucune voix masculine ne fonctionne, on utilise la première par défaut
    print(f"⚠️ Aucune voix masculine testée n'a fonctionné, utilisation de: {MALE_VOICES[0]}")
    return MALE_VOICES[0]

def generate_astuce(num: int) -> str:
    """
    Génère un fichier audio ElevenLabs contenant la phrase :
    'astuce numéro {num}'

    Retourne le chemin du fichier généré.
    """
    global VOICE_ID

    # S'assurer qu'on utilise une voix qui fonctionne
    if not hasattr(generate_astuce, 'voice_tested'):
        VOICE_ID = get_working_voice_id()
        generate_astuce.voice_tested = True

    # Préparation
    text = f"Astuce numéro {num}"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?optimize_streaming_latency=0"

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.8
        }
    }

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    # Requête API
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    # Création dossier si besoin
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    filename = os.path.join(OUTPUT_DIR, f"astuce_{num}.mp3")

    # Écriture fichier
    with open(filename, "wb") as f:
        f.write(response.content)

    return filename


def generate_astuces_range(start: int, end: int, tempo: float = 0.5):
    """
    Génère des fichiers audio pour une plage de numéros avec tempo personnalisé

    Args:
        start: numéro de départ
        end: numéro de fin (inclus)
        tempo: délai en secondes entre chaque génération (défaut: 0.5)
    """
    total_files = end - start + 1
    print(f"Génération de {total_files} fichiers audio (de {start} à {end})...")
    print(f"Tempo: {tempo}s entre chaque génération")

    successful_files = []
    failed_files = []

    for i in range(start, end + 1):
        try:
            print(f"Génération de l'astuce {i}... ", end="")
            filename = generate_astuce(i)
            successful_files.append(filename)
            print(f"✓ {os.path.basename(filename)}")

            # Pause personnalisée pour éviter de surcharger l'API
            if tempo > 0:
                time.sleep(tempo)

        except Exception as e:
            print(f"✗ Erreur: {e}")
            failed_files.append((i, str(e)))

    # Résumé
    print("\n" + "="*50)
    print("RÉSUMÉ DE LA GÉNÉRATION:")
    print(f"✓ Fichiers générés avec succès: {len(successful_files)}/{total_files}")
    print(f"✗ Échecs: {len(failed_files)}")

    if successful_files:
        print(f"\nFichiers créés dans '{OUTPUT_DIR}':")
        for file in successful_files[-5:]:  # Affiche les 5 derniers fichiers
            print(f"  • {os.path.basename(file)}")
        if len(successful_files) > 5:
            print(f"  ... et {len(successful_files) - 5} autres fichiers")

    if failed_files:
        print(f"\nErreurs:")
        for num, error in failed_files:
            print(f"  • Astuce {num}: {error}")


if __name__ == "__main__":
    print("=== Générateur d'Astuces Audio (Voix Masculine) ===")

    # Saisie utilisateur pour la plage
    try:
        start_input = input("Début du numéro d'astuce : ")
        start = int(start_input)

        end_input = input("Fin du numéro d'astuce : ")
        end = int(end_input)

        if start > end:
            print("Erreur: le numéro de départ doit être inférieur ou égal au numéro de fin")
            exit(1)

        if start < 0:
            print("Erreur: les numéros doivent être positifs")
            exit(1)

        # Saisie du tempo (délai entre chaque génération)
        tempo_input = input("Tempo en secondes entre chaque génération (défaut: 0.5) : ")
        if tempo_input.strip() == "":
            tempo = 0.5
        else:
            tempo = float(tempo_input)
            if tempo < 0:
                print("Erreur: le tempo doit être positif")
                exit(1)

    except ValueError:
        print("Erreur: veuillez entrer des nombres valides")
        exit(1)

    print(f"\nConfiguration: Plage {start}-{end}, Tempo: {tempo}s")
    print("-" * 50)

    # Lancement de la génération
    if start == end:
        # Un seul fichier
        try:
            fichier = generate_astuce(start)
            print(f"\n✅ Fichier généré: {fichier}")
        except Exception as e:
            print(f"❌ Erreur lors de la génération: {e}")
    else:
        # Plusieurs fichiers avec tempo
        generate_astuces_range(start, end, tempo)
