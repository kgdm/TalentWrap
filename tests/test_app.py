import unittest
import os
import io
from app import app

class TalentWrapTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['UPLOAD_FOLDER'] = 'tests/uploads'
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        self.app = app.test_client()

    def tearDown(self):
        # Cleanup uploaded files in tests/uploads
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
        os.rmdir(app.config['UPLOAD_FOLDER'])

    def login(self, password):
        return self.app.post('/login', data=dict(
            password=password
        ), follow_redirects=True)

    def logout(self):
        # We don't have a logout route, but we can clear session by not sending cookie
        # Or just rely on setUp creating a fresh client
        pass

    def test_index_redirects_to_login(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_login_page_loads(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome Back', response.data)

    def test_login_success(self):
        response = self.login('admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Candidate Profile', response.data) # Should be on form page

    def test_login_failure(self):
        response = self.login('wrongpassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid password', response.data)

    def test_form_access_protected(self):
        response = self.app.get('/form')
        self.assertEqual(response.status_code, 302) # Redirects to login
        self.assertIn('/login', response.location)

    def test_form_submission(self):
        self.login('admin')
        
        # Create a dummy PDF file to upload
        data = {
            'resume_file': (io.BytesIO(b"%PDF-1.5..."), 'test_resume.pdf'),
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'role': 'Tester'
        }
        
        # We need to mock the PDF generation/merging to avoid actual file processing overhead 
        # or just let it run if it's fast enough. 
        # Since we are using 'test_resume.pdf' content as bytes, the converter might fail if it expects valid PDF.
        # Let's use a valid minimal PDF byte string.
        minimal_pdf = b'%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000060 00000 n\n0000000111 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF'
        
        data['resume_file'] = (io.BytesIO(minimal_pdf), 'test_resume.pdf')

        response = self.app.post('/form', data=data, content_type='multipart/form-data', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Ready to Download', response.data)

if __name__ == '__main__':
    unittest.main()
