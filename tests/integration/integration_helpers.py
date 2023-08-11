from datetime import datetime, timedelta
from typing import Any, Dict

from etsyv3 import EtsyAPI
from etsyv3.enums import WhoMade, WhenMade, ListingType
from etsyv3.models.listing_request import CreateDraftListingRequest
import json


def open_cred_file() -> Any:
    creds = json.load(open("creds.json", "r"))
    return creds


def get_api_client() -> EtsyAPI:
    creds = open_cred_file()
    ks = creds["ks"]
    token = creds["token"]
    refresh_token = "testrefreshtoken"
    api = EtsyAPI(ks, token, refresh_token, datetime.utcnow() + timedelta(hours=1))
    return api


def create_test_listing(api: EtsyAPI, shop_id: int) -> Any:
    d_listing = CreateDraftListingRequest(
        quantity=1,
        price=10000.00,
        title="Test don't buy",
        description="Just a test item",
        who_made=WhoMade.I_DID,
        when_made=WhenMade.TWENTY_TWENTIES,
        listing_type=ListingType.DOWNLOAD,
        taxonomy_id=60,
    )
    response = api.create_draft_listing(shop_id, d_listing)
    return response["listing_id"]


def delete_test_listing(api: EtsyAPI, shop_id: int, listing_id: int) -> Any:
    response = api.delete_listing(listing_id)
