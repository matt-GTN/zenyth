import unittest
from unittest.mock import patch, MagicMock
from src.summarize import summarize_text

class TestSummarize(unittest.TestCase):
    
    def test_summarize_short_text(self):
        """Test de résumé pour un texte court"""
        short_text = "Ceci est un texte court pour tester le résumé."
        
        with patch('src.summarize.ChatOpenAI') as mock_llm:
            # Simuler une réponse du LLM
            mock_response = MagicMock()
            mock_response.content = "Résumé du texte court"
            mock_llm.return_value.invoke.return_value = mock_response
            
            summary, error = summarize_text(short_text)
            
            self.assertIsNone(error)
            self.assertEqual(summary, "Résumé du texte court")
    
    def test_summarize_empty_text(self):
        """Test avec un texte vide"""
        summary, error = summarize_text("")
        self.assertIsNotNone(error)
        self.assertIsNone(summary)
    
    def test_summarize_long_text(self):
        """Test de résumé pour un texte long (Map-Reduce)"""
        # Créer un texte long pour déclencher Map-Reduce
        long_text = "Lorem ipsum " * 5000  # ~60k caractères
        
        with patch('src.summarize.load_summarize_chain') as mock_chain:
            mock_chain_instance = MagicMock()
            mock_chain_instance.invoke.return_value = {'output_text': 'Résumé long'}
            mock_chain.return_value = mock_chain_instance
            
            summary, error = summarize_text(long_text)
            
            self.assertIsNone(error)
            self.assertEqual(summary, 'Résumé long')
    
    def test_summarize_very_long_text(self):
        """Test de résumé pour un texte très long (Map-Reduce avec beaucoup de chunks)"""
        # Créer un texte très long pour tester avec beaucoup de chunks
        # Chaque chunk fait ~20k caractères, créons 10+ chunks
        very_long_text = "Ceci est un paragraphe de test très long qui va être découpé en plusieurs morceaux. " * 10000  # ~500k caractères
        
        with patch('src.summarize.load_summarize_chain') as mock_chain:
            mock_chain_instance = MagicMock()
            mock_chain_instance.invoke.return_value = {'output_text': 'Résumé très long avec Map-Reduce'}
            mock_chain.return_value = mock_chain_instance
            
            summary, error = summarize_text(very_long_text)
            
            self.assertIsNone(error)
            self.assertEqual(summary, 'Résumé très long avec Map-Reduce')
    
    def test_summarize_api_error(self):
        """Test de gestion d'erreur API"""
        with patch('src.summarize.ChatOpenAI') as mock_llm:
            mock_llm.side_effect = Exception("Erreur API")
            
            summary, error = summarize_text("Test")
            
            self.assertIsNotNone(error)
            self.assertIsNone(summary)
            if error:
                self.assertIn("Erreur lors de la génération du résumé", error)

if __name__ == '__main__':
    unittest.main() 