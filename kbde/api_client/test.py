import unittest
from .api_client import ApiClient


class ApiClientTest(unittest.TestCase):
    
    def setUp(self):
        class TestClient(ApiClient):
            BASE_PATH = "https://jsonplaceholder.typicode.com"
            OBJECT_NAME = "posts"
        self.TestClient = TestClient

        class BadHost(self.TestClient):
            BASE_PATH = "https://badurl.notld"
        self.BadHost = BadHost

        class BadResource(self.TestClient):
            OBJECT_NAME = "bananas"
        self.BadResource = BadResource

        class BadServer(ApiClient):
            BASE_PATH = "http://httpstat.us"
            OBJECT_NAME = "500"
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
