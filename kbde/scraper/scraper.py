import time, bs4, urllib

from . import mixins


class Base:
    page_ready_check_interval = 1
    
    def __init__(self, auth_credentials=None, start_page_url=None):
        self.auth_credentials = auth_credentials
        self.start_page_url = start_page_url

        self.device = self.get_device()
        self.page_stack = []

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
            
            # Save the url to the page_stack for this scraper
            self.page_stack.append(page_url)

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
        assert self.start_page_url, (
            f"{self.__class__.__name__} must be instantiated with "
             "`start_page_url` or override .get_start_page_url()"
        )

        return self.start_page_url

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

    def get_start_page_host(self):
        return self.get_host_from_url(self.start_page_url)

    def get_current_host(self):
        return self.get_host_from_url(self.get_current_url())
        
    def get_host_from_url(self, url):
        parsed_url = urllib.parse.urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"

    def get_current_url(self):
        if not self.page_stack:
            return None
        else:
            return self.page_stack[-1]


class Static(mixins.RequestsDevice, Base):
    """
    Scraper which processes static HTML web pages
    """

    def login(self, device, auth_credentials):
        """
        Implements basic authentication for static sites.
        Override this for more specific login flows, such as cookie auth
        """

        if auth_credentials is None:
            return None

        assert isinstance(auth_credentials, tuple), (
            "auth_credentials must be a tuple"
        )
        assert len(auth_credentials) == 2, (
            "auth_credentials must have a length of 2: (username, password)"
        )

        device.auth = auth_credentials

    def get_page_html(self, device, url):
        response = device.get(url)

        assert response.status_code == 200

        return bs4.BeautifulSoup(response.text, features="html.parser")


class JsonApi(mixins.RequestsDevice, Base):
    """
    Scraper to process json from an API endpoint
    """

    def get_page_html(self, device, url):
        response = device.get(url)

        assert response.status_code == 200

        return response.json()
