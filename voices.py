import requests

API_KEY = "sk_V2_hgu_kDPM2XYZAuJ_0n8MQd6MjF25tZfPPg18WIzYfN6LDhNr"
BASE_URL = "https://api.heygen.com/v2/voices"

def list_voices():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.get(BASE_URL, headers=headers)
    response.raise_for_status()

    data = response.json()

    voices = data.get("data", [])
    if isinstance(voices, dict):
        voices = voices.get("voices", [])
    result = []

    if isinstance(voices, list) and voices and isinstance(voices[0], dict):
        # Standard case: voices is a list of dicts
        for voice in voices:
            result.append({
                "id": voice.get("voice_id"),
                "name": voice.get("name"),
                "style": voice.get("style"),
                "language": voice.get("language")
            })
    elif isinstance(voices, list) and voices and isinstance(voices[0], str):
        # Edge case: voices is a list of voice IDs (strings)
        for voice_id in voices:
            result.append({
                "id": voice_id,
                "name": voice_id,
                "style": None,
                "language": None
            })

    return result


if __name__ == "__main__":
    voices = list_voices()

    if not voices:
        print("Aucune voix trouvée.")
    else:
        print("Toutes les voix :\n")
        for v in voices:
            print(f"- {v['name']}  |  ID : {v['id']}  | Langue : {v['language']}  | style : {v['style']}")
