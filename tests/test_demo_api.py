"""Contract tests for the browser demo; speech-model tests run separately."""
import io
import unittest
from unittest.mock import patch

import imv_api
from demo import web_routes


class DemoApiTests(unittest.TestCase):
    def setUp(self):
        self.client = imv_api.app.test_client()

    def test_known_question_and_unrelated_question(self):
        known = self.client.post('/demo/answer', json={'text': 'What is Sky?'})
        self.assertEqual(known.status_code, 200)
        self.assertFalse(known.json['fallback'])
        self.assertIn('Sky', known.json['answer'])
        unknown = self.client.post('/demo/answer', json={'text': 'How much is tuition?'})
        self.assertTrue(unknown.json['fallback'])
        self.assertNotIn('connect', unknown.json['answer'])

    def test_validation(self):
        for payload in [None, [], {}, {'text': 2}, {'text': ''}, {'text': 'Sky', 'language': []}]:
            response = self.client.post('/demo/answer', json=payload)
            self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.post('/demo/transcribe').status_code, 400)
        self.assertEqual(self.client.post('/tts', json=[]).status_code, 400)

    def test_pages_and_spanish_answer(self):
        for route in ['/', '/demo', '/studio']:
            with self.client.get(route) as response:
                self.assertEqual(response.status_code, 200)
        response = self.client.post('/demo/answer', json={'text': 'What is Sky?', 'language': 'es'})
        self.assertEqual(response.json['language'], 'es')
        self.assertIn('Soy Sky', response.json['answer'])

    def test_empty_and_unsupported_uploads(self):
        for filename, content in [('sample.wav', b''), ('sample.txt', b'hello')]:
            response = self.client.post('/demo/transcribe', data={'file': (io.BytesIO(content), filename)})
            self.assertEqual(response.status_code, 400)

    def test_generation_busy_and_lock_release(self):
        imv_api.generation_lock.acquire()
        try:
            response = self.client.post('/tts', json={'username': 'default', 'text': 'Hello'})
            self.assertEqual(response.status_code, 429)
        finally:
            imv_api.generation_lock.release()
        with patch.object(imv_api.subprocess, 'run', side_effect=OSError('Test failure')):
            response = self.client.post('/tts', json={'username': 'default', 'text': 'Hello'})
            self.assertEqual(response.status_code, 500)
        self.assertFalse(imv_api.generation_lock.locked())


if __name__ == '__main__':
    unittest.main()
