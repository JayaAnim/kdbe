def getUniqueList(l):
    """
    Returns a version of list
    Preserves order of items
    """
    unique_list = []
    for item in l:
        if item in unique_list:
            continue
        unique_list.append(item)

    return unique_list
