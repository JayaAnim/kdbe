def convert_to_underscore_case(string):
    new_string = ""
    string_len = len(string)
    for index,char in enumerate(string):

        if index < string_len - 1:
            #We are not on the last string
            next_char = string[index+1]
        else:
            next_char = None
        if index > 0:
            previous_char = string[index-1]
        else:
            previous_char = None

        converted = False

        if char.isupper():
            char = char.lower()
            converted = True

        if char.isdigit() and \
           previous_char is not None and \
           not previous_char.isdigit():
            converted = True

        if converted and new_string:
            char = "_" + char

        new_string += char

    return new_string
