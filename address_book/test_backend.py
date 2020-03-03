import unittest
from address_book_api import app, userdb

class FlaskTestCase(unittest.TestCase):
    
    def test_create_new(self):
        tester = app.test_client(self)
        tester.post('/login', data=dict(username="team3", password="team3"), follow_redirects=True)
        #tester.post('/addnew', data ={'title': "I HATE THIS"} , follow_redirects=True)
        
        
        # x = 1
        # y = 2
        #
        # tester.post('/_addContact', data = {'first_name': '{}'.format(x),
        # 'last_name': '{}'.format(x),
        # 'phone_num': '{}{}{}{}{}{}{}{}{}{}'.format(x,x,x,x,x,x,x,x,x,y),
        # 'address': '{}'.format(x),
        # 'city': '{}'.format(x),
        # 'state': '{}'.format(x),
        # 'zipcode':'{}{}{}{}{}'.format(x,x,x,x,y),
        # 'id':'{}'.format(x+y)}
        # )
        # tester.post('/_addContact', follow_redirects=True)
        # tester.post('/addnew/save', data= dict(book_name="Backend testing"), follow_redirects=True)
        tester.post('/openExisting/backendtesting', follow_redirects=True)
        for y in range(2):
            for x in range(10):

                 tester.post('/_addContact', data = {'first_name': '{}'.format(x),
                 'last_name': '{}'.format(x),
                 'phone_num': '{}{}{}{}{}{}{}{}{}{}'.format(x,x,x,x,x,x,x,x,x,y),
                 'address': '{}'.format(x),
                 'city': '{}'.format(x),
                 'state': '{}'.format(x),
                 'zipcode':'{}{}{}{}{}'.format(x,x,x,x,y),
                 'id':'{}'.format(x+y)}
                 )
                 tester.post('/_addContact', follow_redirects=True)
        #print("RUNNING")
        
        tester.post('/addnew/save', data= dict(book_name="Backend testing"), follow_redirects=True)
            
    def test_pulling_from_database(self):
        tester = app.test_client(self)
        tester.post('/login', data=dict(username="team3", password="team3"), follow_redirects=True)
        count = 0
        pass
        
    def test_deleting(self):
        pass
        
        
        
if __name__ == '__main__':
    unittest.main()
        