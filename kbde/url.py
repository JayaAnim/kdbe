def getUrl(data):
    """
    Takes a dictionary
    Returns a url querystring
    """
    arg_list = ["{0}={1}".format(key,data[key]) for key in data]
    url = "&".join(arg_list)
    return url
