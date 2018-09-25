import unittest
from .api_client import ApiClient


class ApiClientTest(unittest.TestCase):
    
    def setUp(self):
        class TestClient(ApiClient):
            base_path = "https://jsonplaceholder.typicode.com"
            object_name = "posts"
        self.TestClient = TestClient

        class BadHost(self.TestClient):
            base_path = "https://badurl.notld"
        self.BadHost = BadHost

        class BadResource(self.TestClient):
            object_name = "bananas"
        self.BadResource = BadResource

        class BadServer(ApiClient):
            base_path = "http://httpstat.us"
            object_name = "500"
        self.BadServer = BadServer


    def testConstruct(self):
        self.TestClient()


    #Get functions

    def testGet(self):
        client = self.TestClient()
        data = client.get()

    def testBadHostGet(self):
        client = self.BadHost()
        with self.assertRaises(client.ConnectionException):
            client.get()

    def testBadResourceGet(self):
        client = self.BadResource()
        with self.assertRaises(client.NotFoundException):
            client.get()

    def testBadServerGet(self):
        client = self.BadServer()
        with self.assertRaises(client.ServerException):
            client.get()


    #Post functions

    def testPost(self):
        client = self.TestClient()
        data = client.post(title='foo',
                           body='bar',
                           userId=1)

    def testBadHostPost(self):
        client = self.BadHost()
        with self.assertRaises(client.ConnectionException):
            client.post()

    def testBadResourcePost(self):
        client = self.BadResource()
        with self.assertRaises(client.NotFoundException):
            client.post()

    def testBadServerPost(self):
        client = self.BadServer()
        with self.assertRaises(client.ServerException):
            client.post()
