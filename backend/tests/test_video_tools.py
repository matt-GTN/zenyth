import unittest
from src.video_tools import extract_video_id, get_video_transcript

class TestVideoTools(unittest.TestCase):
    
    def test_extract_video_id_standard_url(self):
        """Test d'extraction d'ID depuis une URL YouTube standard"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = extract_video_id(url)
        self.assertEqual(video_id, "dQw4w9WgXcQ")
    
    def test_extract_video_id_short_url(self):
        """Test d'extraction d'ID depuis une URL YouTube courte"""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = extract_video_id(url)
        self.assertEqual(video_id, "dQw4w9WgXcQ")
    
    def test_extract_video_id_with_params(self):
        """Test d'extraction d'ID avec paramètres supplémentaires"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s&feature=share"
        video_id = extract_video_id(url)
        self.assertEqual(video_id, "dQw4w9WgXcQ")
    
    def test_extract_video_id_invalid_url(self):
        """Test avec une URL invalide"""
        url = "https://example.com/video"
        video_id = extract_video_id(url)
        self.assertIsNone(video_id)
    
    def test_extract_video_id_empty_string(self):
        """Test avec une chaîne vide"""
        url = ""
        video_id = extract_video_id(url)
        self.assertIsNone(video_id)

if __name__ == '__main__':
    unittest.main() 