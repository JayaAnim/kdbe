def make_url(*args, **kwargs):
    """
    Returns a url with querystring
    """
    url = "/".join(args)

    if kwargs:
        query_list = ["{}={}".format(key, value) for key, value in kwargs.items()]
        query = "&".join(query_list)
        url += "?" + query

    return url
