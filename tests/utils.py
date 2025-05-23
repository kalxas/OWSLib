import logging
import os
import sys
import requests
from owslib.etree import etree, ElementType
from urllib.parse import urlparse


def setup_logging(loglevel='INFO'):
    """Helper function to setup logging for tests"""
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, loglevel))
    sh = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger


def resource_file(filepath):
    return os.path.join(test_directory(), 'resources', filepath)


def test_directory():
    """Helper function to return path to the tests directory"""
    return os.path.dirname(__file__)


def scratch_directory():
    """Helper function to return path to the tests scratch directory"""
    return os.path.join(test_directory(), 'scratch')


def scratch_file(filename):
    """Helper function to return file path in the tests scratch directory"""
    return os.path.join(scratch_directory(), filename)


def compare_xml(a, b):
    if not isinstance(a, ElementType):
        a = etree.fromstring(a)
    if not isinstance(b, ElementType):
        b = etree.fromstring(b)

    return compare_elements(a, b)


def compare_elements(a, b):
    # Tag
    if a.tag != b.tag:
        return False
    # Value
    if a.text != b.text:
        return False
    # Attributes
    if sorted(a.items()) != sorted(b.items()):
        return False
    # Children
    if len(list(a)) != len(list(b)):
        return False
    # Recurse
    for ac, bc in zip(list(a), list(b)):
        if not compare_elements(ac, bc):
            return False

    return True


def cast_tuple_int_list(tup):
    """Set tuple float values to int for more predictable test results"""
    return [int(a) for a in tup]


def cast_tuple_int_list_srs(tup):
    tup2 = cast_tuple_int_list(tup[:4])
    tup2.append(tup[-1])
    return tup2


def sorted_url_query(url):
    return sorted(urlparse(url).query.split("&"))


def service_ok(url, timeout=5):
    try:
        resp = requests.get(url, allow_redirects=True, timeout=timeout, stream=True)
        if 'html' in resp.headers.get('content-type', '').lower():
            resp.close()
            return False
        ok = resp.ok
        resp.close()
        return ok
    except requests.exceptions.ReadTimeout:
        ok = False
    except requests.exceptions.ConnectTimeout:
        ok = False
    except Exception:
        ok = False
    return ok
