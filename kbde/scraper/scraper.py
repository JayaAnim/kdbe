import time, bs4


class Base:
    page_ready_check_interval = 1
    
    def __init__(self, auth_credentials=None):
        self.auth_credentials = auth_credentials
        self.device = self.get_device()

    def get_device(self):
        """
        Returns a device which will be getting data from a web page
        This could be a requests.Session() instance or a Selenium instance
        """
        raise NotImplementedError

    def get_data(self):
        # Log in
        self.login(self.device, self.auth_credentials)

        # Get the starting url
        page_url = self.get_start_page_url(self.device)

        while True:

            # Get the HTML for the current page
            page_html = self.get_page_html(self.device, page_url)

            for obj in self.get_data_from_page(page_html):
                yield obj

            # Get the next page url
            page_url = self.get_next_page_url(self.device, page_html)

            if page_url is None:
                break

    def login(self, device, auth_credentials):
        """
        Authenticate the device with the auth_credentials
        By default this does nothing
        """
        return None

    def get_start_page_url(self, device):
        """
        Retun the url of the starting page for scraping
        """
        raise NotImplementedError

    def get_page_html(self, device, url):
        """
        Takes a url and returns the HTML from that web page
        """
        raise NotImplementedError

    def get_data_from_page(self, device, page_html):
        """
        Returns a list of dictionaries, created from the given html
        """
        raise NotImplementedError

    def get_next_page_url(self, device, page_html):
        """
        Takes page_html and returns the next url
        Returns None if there is no next page
        """
        raise NotImplementedError


class Static(Base):
    """
    Scraper which processes static HTML web pages
    """
    
    def get_device(self):
        import requests

        return requests.Session()

    def login(self, device, auth_credentials):
        """
        Implements basic authentication for static sites.
        Override this for more specific login flows, such as cookie auth
        """

        if auth_credentials is None:
            return None

        assert (
            isinstance(auth_credentials, tuple),
            "auth_credentials must be a tuple",
        )
        assert (
            len(auth_credentials) == 2,
            "auth_credentials must have a length of 2: (username, password)",
        )

        device.auth = auth_credentials

    def get_page_html(self, device, url):
        response = device.get(url)

        assert response.status_code == 200

        return bs4.BeautifulSoup(response.text, features="html.parser")
