#!/usr/bin/env python3
"""
Script de test pour le Map-Reduce avec un gros volume de texte
Usage: python test_map_reduce_real.py
"""

import os
import time
from src.summarize import summarize_text

def generate_large_text(num_paragraphs=100):
    """Génère un texte très long pour tester le Map-Reduce"""
    paragraphs = [
        "L'intelligence artificielle révolutionne notre façon de travailler et de penser. Les modèles de langage comme GPT et Claude transforment la création de contenu, l'analyse de données et l'automatisation des tâches. Cette technologie ouvre de nouvelles possibilités dans de nombreux domaines, de la médecine à l'éducation en passant par la finance et l'art.",
        "Le développement durable est devenu une priorité mondiale. Les entreprises et les gouvernements s'efforcent de réduire leur empreinte carbone et d'adopter des pratiques plus respectueuses de l'environnement. Les énergies renouvelables, l'économie circulaire et la mobilité verte sont au cœur de cette transformation.",
        "La cybersécurité est un enjeu majeur à l'ère du numérique. Les cyberattaques se multiplient et deviennent plus sophistiquées. Les organisations doivent investir dans des solutions de protection avancées et former leurs employés aux bonnes pratiques de sécurité informatique.",
        "L'éducation numérique transforme l'apprentissage traditionnel. Les plateformes en ligne, les cours hybrides et les outils d'apprentissage adaptatif permettent une personnalisation de l'éducation. Cette évolution nécessite de repenser les méthodes pédagogiques et l'évaluation des compétences.",
        "La santé connectée améliore le suivi médical et la prévention. Les objets connectés, les applications de santé et la télémédecine facilitent l'accès aux soins et permettent un meilleur suivi des patients. Cette approche préventive peut réduire les coûts de santé et améliorer la qualité de vie."
    ]
    
    # Répéter les paragraphes pour créer un texte très long
    full_text = ""
    for i in range(num_paragraphs):
        full_text += paragraphs[i % len(paragraphs)] + " "
        if i % 10 == 0:  # Ajouter un saut de ligne tous les 10 paragraphes
            full_text += "\n\n"
    
    return full_text

def test_map_reduce_performance():
    """Teste les performances du Map-Reduce avec différents volumes de texte"""
    
    print("🧪 Test de performance Map-Reduce")
    print("=" * 50)
    
    # Vérifier la configuration
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Erreur: OPENROUTER_API_KEY non définie")
        print("Ajoutez votre clé API dans le fichier .env")
        return
    
    # Test avec différents volumes
    test_cases = [
        ("Court", 10, "~5k caractères"),
        ("Moyen", 50, "~25k caractères"),
        ("Long", 100, "~50k caractères"),
        ("Très long", 200, "~100k caractères"),
        ("Massif", 500, "~250k caractères")
    ]
    
    for test_name, paragraphs, expected_size in test_cases:
        print(f"\n📝 Test {test_name} ({expected_size})")
        print("-" * 30)
        
        # Générer le texte
        start_time = time.time()
        text = generate_large_text(paragraphs)
        generation_time = time.time() - start_time
        
        print(f"📊 Taille du texte: {len(text):,} caractères")
        print(f"⏱️  Génération: {generation_time:.2f}s")
        
        # Tester le résumé
        start_time = time.time()
        summary, error = summarize_text(text)
        processing_time = time.time() - start_time
        
        if error:
            print(f"❌ Erreur: {error}")
        else:
            if summary:
                print(f"✅ Résumé généré: {len(summary):,} caractères")
                print(f"⏱️  Traitement: {processing_time:.2f}s")
                print(f"📈 Ratio compression: {len(text)/len(summary):.1f}:1")
                
                # Afficher un aperçu du résumé
                preview = summary[:200] + "..." if len(summary) > 200 else summary
                print(f"📄 Aperçu: {preview}")
            else:
                print("❌ Résumé vide")
        
        print(f"⏱️  Temps total: {generation_time + processing_time:.2f}s")

if __name__ == "__main__":
    test_map_reduce_performance() 