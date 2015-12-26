__author__ = 'monica'

import urllib2


def request_content_from_http(url):
    f = urllib2.urlopen(url)
    return f.read()


def return_value_via_key(data_list, key_name):
    return_value = None
    for name, value in data_list:
        if key_name == name:
            return_value = value
            break
    return return_value


def read_file_content(file, mode="r"):
    content = ""
    file_handle = open(file, mode)
    if file_handle is not None:
        content = file_handle.read()
        file_handle.close()
    return content


def write_to_file(file, content, mode="w"):
    file_handle = open(file, mode)
    if file_handle is not None:
        file_handle.write(content)
        file_handle.close()
