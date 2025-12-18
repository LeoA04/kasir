import unittest
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def test_login_page(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_signup_page(self):
        response = self.client.get("/signup")
        self.assertEqual(response.status_code, 200)

    def test_index_redirect_when_not_logged_in(self):
        response = self.client.get("/", follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # redirect ke login

if __name__ == '__main__':
    unittest.main()