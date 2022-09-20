import unittest
from datetime import datetime, timedelta
from unittest import mock

import tests.mock_helpers
from etsyv3 import EtsyAPI
from etsyv3.etsy_api import ETSY_API_BASEURL, Unauthorised

EXPIRY_FUTURE = datetime.utcnow() + timedelta(hours=1)
EXPIRY_PAST = datetime.utcnow() - timedelta(hours=1)
KEYSTRING = ""
TOKEN = ""
REFRESH_TOKEN = ""


def fn_save(one, two, three):
    pass


class TestEtsyAPI(unittest.TestCase):
    def test__generate_get_uri_one_value(self):
        test_dict = {"limit": None, "offset": 100}
        url = EtsyAPI._generate_get_uri(ETSY_API_BASEURL, **test_dict)
        expect_url = f"{ETSY_API_BASEURL}?offset=100"
        self.assertEqual(expect_url, url)

    def test__generate_get_uri_two_values(self):
        test_dict = {"limit": 100, "offset": 100}
        url = EtsyAPI._generate_get_uri(ETSY_API_BASEURL, **test_dict)
        expect_url = f"{ETSY_API_BASEURL}?limit=100&offset=100"
        self.assertEqual(expect_url, url)

    def test__generate_get_uri_none_values_in_kwargs(self):
        test_dict = {"limit": None, "offset": None}
        url = EtsyAPI._generate_get_uri(ETSY_API_BASEURL, **test_dict)
        expect_url = f"{ETSY_API_BASEURL}"
        self.assertEqual(expect_url, url)

    def test__generate_get_uri_no_kwargs(self):
        url = EtsyAPI._generate_get_uri(ETSY_API_BASEURL)
        expect_url = f"{ETSY_API_BASEURL}"
        self.assertEqual(expect_url, url)

    @mock.patch(
        "requests.Session.get", side_effect=tests.mock_helpers.mocked_requests_get
    )
    def test_get_user_unauthorised(self, mock_get):
        etsy = EtsyAPI(KEYSTRING, TOKEN, REFRESH_TOKEN, EXPIRY_FUTURE, fn_save)
        with self.assertRaises(Unauthorised) as context:
            etsy.get_user("UNAUTHORIZED")

    @mock.patch(
        "requests.Session.get", side_effect=tests.mock_helpers.mocked_requests_get
    )
    def test_get_self(self, mock_get):
        etsy = EtsyAPI(KEYSTRING, TOKEN, REFRESH_TOKEN, EXPIRY_FUTURE, fn_save)
        etsy.get_authenticated_user()
        mock_get.assert_called()
