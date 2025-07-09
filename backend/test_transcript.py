from src.video_tools import get_video_transcript, extract_video_id

# Une vidéo YouTube avec des sous-titres (TEDx Talk en français)
test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
video_id = extract_video_id(test_url)

print(f"Test de récupération de transcription pour la vidéo : {test_url}")
print(f"ID de la vidéo : {video_id}")

if video_id:
    transcript, error = get_video_transcript(video_id)

    if transcript:
        print("\nTranscription récupérée avec succès !")
        print("Premiers 200 caractères de la transcription :")
        print(transcript[:200] + "...")
    else:
        print("\nErreur lors de la récupération de la transcription :")
        print(error)
else:
    print("\nErreur : Impossible d'extraire l'ID de la vidéo de l'URL") 