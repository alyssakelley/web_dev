import unittest
from address_book_api import app, userdb

class FlaskTestCase(unittest.TestCase):
    ''' Ensure the page is hosting correctly, the login works with correct credentials and does not work with incorrect credentials, 
    and ensures the user is logged out.
    '''
    
    #Testing that flask initiates page
    def test_flask_initiates(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        
    #Ensures the correct message is shown when using incorrect login credectials    
    def test_login_incorrect(self):
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(username="blank", password="blank"), follow_redirects=True)
        self.assertIn(b'Invalid username or password', response.data)

    #Ensures the home page is shown after using correct credentials
    def test_login_correct(self):
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(username="team3", password="team3"), follow_redirects=True)
        self.assertIn(b'Create Your Own Address Book', response.data)
        #self.assertTrue(b'Create Your Own Address Book.' in response.data)
    
    #Tests that the logout works correctly    
    def test_logout(self):
       tester = app.test_client(self)
       tester.post('/login', data=dict(username="team3", password="team3"), follow_redirects=True)
       response = tester.get('/logout', follow_redirects=True)
       self.assertIn(b'New User?', response.data)
       
    #Testing that user is redirected to login page to continue to the website
    def test_main_page_requires_login(self):
        tester = app.test_client(self)
        response = tester.get('/', follow_redirects=True)
        self.assertTrue(b'Please log in to access this page.' in response.data)
        
if __name__ == '__main__':
    unittest.main()
        