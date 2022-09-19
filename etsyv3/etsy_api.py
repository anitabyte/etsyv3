from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Callable, List

import requests

from etsyv3.models import ListingFile, ListingProperty, Request, UpdateListingRequest
from etsyv3.models.listing_request import (
    CreateDraftListingRequest,
    UpdateListingInventoryRequest,
    UpdateVariationImagesRequest,
)

ETSY_API_BASEURL = "https://openapi.etsy.com/v3/application/"


class ExpiredToken(Exception):
    pass


class BadRequest(Exception):
    pass


class Unauthorised(Exception):
    pass


class NotFound(Exception):
    pass


class InternalError(Exception):
    pass


class Forbidden(Exception):
    pass


class Conflict(Exception):
    pass


class SortOn(Enum):
    CREATED = "created"
    PRICE = "price"
    UPDATED = "updated"
    SCORE = "score"


class SortOrder(Enum):
    ASC = "asc"
    ASCENDING = "ascending"
    DESC = "desc"
    DESCENDING = "descending"
    UP = "up"
    DOWN = "down"


class Includes(Enum):
    SHIPPING = "Shipping"
    IMAGES = "Images"
    SHOP = "Shop"
    USER = "User"
    TRANSLATIONS = "Translations"
    INVENTORY = "Inventory"


class ListingState(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SOLD_OUT = "sold_out"
    DRAFT = "draft"
    EXPIRED = "expired"


class Method(Enum):
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4


class EtsyAPI:
    def __init__(
        self,
        keystring: str,
        token: str,
        refresh_token: str,
        expiry: datetime,
        refresh_save: Callable[[str, str, datetime], None] = None,
    ):
        self.session = requests.Session()
        self.token = token
        self.user_id = token.split(".")[0]
        self.refresh_token = refresh_token
        self.keystring = keystring
        self.session.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": keystring,
            "Authorization": "Bearer " + self.token,
        }
        self.expiry = expiry.replace(tzinfo=timezone.utc).astimezone(tz=None)
        self.refresh_save = refresh_save

    @staticmethod
    def _generate_get_uri(uri, **kwargs):
        if kwargs == {} or kwargs is None:
            return uri
        params = "&".join(
            [f"{key}={value}" for key, value in kwargs.items() if value is not None]
        )
        uri = f"{uri}?{params}" if params != "" else uri
        return uri

    def _issue_request(
        self,
        uri,
        method: Method = Method.GET,
        request_payload: Request = None,
        **kwargs,
    ):
        if (
            method != Method.GET and method != Method.DELETE
        ) and request_payload is None:
            raise ValueError
        if (
            datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=None)
            < self.expiry
        ):
            if method == Method.GET:
                uri_full = EtsyAPI._generate_get_uri(uri, **kwargs)
                return_val = self.session.get(uri_full)
            elif method == method.PUT:
                return_val = self.session.put(uri, json=request_payload.get_dict())
            elif method == method.POST:
                return_val = self.session.post(uri, json=request_payload.get_dict())
            else:
                return_val = self.session.delete(uri)
            if return_val.status_code == 400:
                raise BadRequest(return_val.json())
            elif return_val.status_code == 401:
                raise Unauthorised(return_val.json())
            elif return_val.status_code == 403:
                raise Forbidden(return_val.json())
            elif return_val.status_code == 409:
                raise Conflict(return_val.json())
            elif return_val.status_code == 404:
                raise NotFound(return_val.json())
            elif return_val.status_code == 500:
                raise InternalError(return_val.json())
            return return_val.json()

        else:
            self.refresh()
            return self._issue_request(uri, **kwargs)

    def get_buyer_taxonomy_nodes(self):
        uri = f"{ETSY_API_BASEURL}/buyer-taxonomy/nodes"
        return self._issue_request(uri)

    def get_properties_by_buyer_taxonomy_id(self, taxonomy_id):
        uri = f"{ETSY_API_BASEURL}/buyer-taxonomy/nodes/{taxonomy_id}/properties"
        return self._issue_request(uri)

    def get_seller_taxonomy_nodes(self):
        uri = f"{ETSY_API_BASEURL}/seller-taxonomy/nodes"
        return self._issue_request(uri)

    def get_properties_by_taxonomy_id(self, taxonomy_id):
        uri = f"{ETSY_API_BASEURL}/seller-taxonomy/nodes/{taxonomy_id}/properties"
        return self._issue_request(uri)

    def create_draft_listing(self, shop_id, listing: CreateDraftListingRequest):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings"
        return self._issue_request(uri, method=Method.POST, request_payload=listing)

    def get_listings_by_shop(
        self,
        shop_id,
        state: ListingState = None,
        limit: int = None,
        offset: int = None,
        sort_on: SortOn = None,
        sort_order: SortOrder = None,
        includes: List[Includes] = None,
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings"
        kwargs = {
            "state": state.value if state is not None else None,
            "limit": limit,
            "offset": offset,
            "sort_on": sort_on.value if sort_on is not None else None,
            "sort_order": sort_order.value if sort_order is not None else None,
            "includes": [x.value for x in includes] if includes is not None else None,
        }
        return self._issue_request(uri, **kwargs)

    def delete_listing(self, listing_id: int):
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def get_listing(self, listing_id: int, includes: List[Includes] = None):
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}"
        kwargs = {
            "includes": [x.value for x in includes] if includes is not None else None
        }
        return self._issue_request(uri, **kwargs)

    def find_all_listings_active(
        self,
        limit: int = None,
        offset: int = None,
        keywords: str = None,
        sort_on: SortOn = None,
        sort_order: SortOrder = None,
        min_price: float = None,
        max_price: float = None,
        shop_location: str = None,
    ):
        # not implementing taxonomy ids because I don't know what they are
        uri = f"{ETSY_API_BASEURL}/listings/active"
        kwargs = {
            "limit": limit,
            "offset": offset,
            "keywords": keywords,
            "sort_on": sort_on.value if sort_on is not None else None,
            "sort_order": sort_order.value if sort_order is not None else None,
            "min_price": min_price,
            "max_price": max_price,
            "shop_location": shop_location,
        }
        return self._issue_request(uri, **kwargs)

    def find_all_active_listings_by_shop(
        self,
        shop_id,
        limit: int = None,
        sort_on: SortOn = None,
        sort_order: SortOrder = None,
        offset: int = None,
        keywords: str = None,
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/active"
        kwargs = {
            "limit": limit,
            "sort_on": sort_on.value if sort_on is not None else None,
            "sort_order": sort_order.value if sort_order is not None else None,
            "offset": offset,
            "keywords": keywords,
        }
        return self._issue_request(uri, **kwargs)

    def get_listings_by_listing_ids(
        self, listing_ids: List[int], includes: List[Includes] = None
    ):
        uri = f"{ETSY_API_BASEURL}/listings/batch"
        kwargs = {
            "listing_ids": listing_ids,
            "includes": [x.value for x in includes] if includes is not None else None,
        }
        return self._issue_request(uri, **kwargs)

    def get_featured_listings_by_shop(self, shop_id, limit=None, offset=None):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/featured"
        kwargs = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def delete_listing_property(self, shop_id: int, listing_id: int, property_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/properties/{property_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def update_listing_property(
        self,
        shop_id: int,
        listing_id: int,
        property_id: int,
        listing_property: ListingProperty,
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/properties/{property_id}"
        raise NotImplementedError

    def get_listing_property(self, listing_id: int, property_id: int):
        # not in production yet
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/properties/{property_id}"
        raise NotImplementedError

    def get_listing_properties(self, shop_id: int, listing_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/properties"
        return self._issue_request(uri)

    def update_listing(
        self, shop_id: int, listing_id: int, listing: UpdateListingRequest
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}"
        raise NotImplementedError

    def get_listings_by_shop_receipt(
        self, shop_id: int, receipt_id: int, limit=None, offset=None
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/receipts/{receipt_id}/listings"
        kwargs = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def get_listings_by_shop_section_id(
        self,
        shop_id: int,
        shop_section_ids: List[int],
        limit: int = None,
        offset: int = None,
        sort_on: SortOn = None,
        sort_order: SortOrder = None,
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shop-sections/listings"
        kwargs = {
            "shop_section_ids": shop_section_ids,
            "limit": limit,
            "offset": offset,
            "sort_on": sort_on.value if sort_on is not None else None,
            "sort_order": sort_order.value if sort_order is not None else None,
        }
        return self._issue_request(uri, **kwargs)

    def delete_listing_file(self, shop_id: int, listing_id: int, listing_file_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/files/{listing_file_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def get_listing_file(self, shop_id: int, listing_id: int, listing_file_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/files/{listing_file_id}"
        return self._issue_request(uri)

    def get_all_listing_files(self, shop_id: int, listing_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/files"
        return self._issue_request(uri)

    def upload_listing_file(
        self, shop_id: int, listing_id: int, listing_file: ListingFile
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/files"
        raise NotImplementedError

    def delete_listing_image(
        self, shop_id: int, listing_id: int, listing_image_id: int
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/images/{listing_image_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def get_listing_image(self, listing_id: int, listing_image_id: int):
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/images/{listing_image_id}"
        return self._issue_request(uri)

    def get_listing_images(self, listing_id: int):
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/images"
        return self._issue_request(uri)

    def upload_listing_image(self):
        raise NotImplementedError

    def get_listing_inventory(self, listing_id):
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/inventory"
        return self._issue_request(uri)

    def update_listing_inventory(
        self, listing_id: int, listing_inventory: UpdateListingInventoryRequest
    ):
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/inventory"
        return self._issue_request(uri, Method.PUT, listing_inventory)

    def get_listing_offering(
        self, listing_id: int, product_id: int, product_offering_id: int
    ):
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/products/{product_id}/offerings/{product_offering_id}"
        return self._issue_request(uri)

    def get_listing_product(self, listing_id: int, product_id: int):
        uri = (
            f"{ETSY_API_BASEURL}/listings/{listing_id}/inventory/products/{product_id}"
        )
        return self._issue_request(uri)

    def create_listing_translation(self):
        raise NotImplementedError

    def get_listing_translation(self, shop_id: int, listing_id: int, language: str):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/translations/{language}"
        return self._issue_request(uri)

    def update_listing_translation(self):
        raise NotImplementedError

    def get_listing_variation_images(self, shop_id: int, listing_id: int):
        uri = (
            f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/variation-images"
        )
        return self._issue_request(uri)

    def update_variation_images(
        self,
        shop_id: int,
        listing_id: int,
        variation_images: UpdateVariationImagesRequest,
    ):
        uri = (
            f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/variation-images"
        )
        return self._issue_request(
            uri, method=Method.POST, request_payload=variation_images
        )

    def ping(self):
        uri = f"{ETSY_API_BASEURL}/openapi-ping"
        return self._issue_request(uri)

    def token_scopes(self):
        uri = f"{ETSY_API_BASEURL}/scopes"
        return self._issue_request(uri)

    def get_shop_payment_account_ledger_entry(self, shop_id: int, ledger_entry_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/payment-account/ledger-entries/{ledger_entry_id}"
        return self._issue_request(uri)

    def get_shop_payment_account_ledger_entries(
        self,
        shop_id: int,
        min_created: int,
        max_created: int,
        limit: int = None,
        offset: int = None,
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/payment-account/ledger-entries"
        kwargs = {
            "min_created": min_created,
            "max_created": max_created,
            "limit": limit,
            "offset": offset,
        }
        return self._issue_request(uri, **kwargs)

    def get_payment_account_ledger_entry_payments(
        self, shop_id: int, ledger_entry_ids: List[int]
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/payment-account/ledger-entries/payments"
        kwargs = {"ledger_entry_ids": ledger_entry_ids}
        return self._issue_request(uri, **kwargs)

    def get_shop_payment_by_receipt_id(self, shop_id: int, receipt_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/receipts/{receipt_id}/payments"
        return self._issue_request(uri)

    def get_payments(self, shop_id: int, payment_ids: List[int]):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/payments"
        kwargs = {"payment_ids": payment_ids}
        return self._issue_request(uri, **kwargs)

    def get_shop_receipt(self, shop_id: int, receipt_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/receipts/{receipt_id}"
        return self._issue_request(uri)

    def update_shop_receipt(self):
        raise NotImplementedError

    def get_shop_receipts(self, shop_id: int, limit: int = None, offset: int = None):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/receipts"
        kwargs = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def create_receipt_shipment(self):
        raise NotImplementedError

    def get_shop_receipt_transactions_by_listing(
        self, shop_id: int, listing_id: int, limit: int = None, offset: int = None
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/transactions"
        kwargs = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def get_shop_receipt_transactions_by_receipt(self, shop_id: int, receipt_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/receipts/{receipt_id}/transactions"
        return self._issue_request(uri)

    def get_shop_receipt_transaction(self, shop_id: int, transaction_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/transactions/{transaction_id}"
        return self._issue_request(uri)

    def get_shop_receipt_transactions_by_shop(
        self, shop_id: int, limit: int = None, offset: int = None
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/transactions"
        kwargs = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def get_reviews_by_listing(
        self, listing_id: int, limit: int = None, offset: int = None
    ):
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/reviews"
        kwargs = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def get_reviews_by_shop(self, shop_id: int, limit: int = None, offset: int = None):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/reviews"
        kwargs = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def get_shipping_carriers(self, origin_country_iso: str):
        uri = f"{ETSY_API_BASEURL}/shipping-carriers"
        kwargs = {"origin_country_iso": origin_country_iso}
        return self._issue_request(uri, **kwargs)

    def create_shop_shipping_profile(self):
        raise NotImplementedError

    def get_shop_shipping_profiles(self, shop_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shipping-profiles"
        return self._issue_request(uri)

    def delete_shop_shipping_profile(self, shop_id: int, shipping_profile_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shipping-profiles/{shipping_profile_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def get_shop_shipping_profile(self, shop_id: int, shipping_profile_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shipping-profiles/{shipping_profile_id}"
        return self._issue_request(uri)

    def update_shop_shipping_profile(self):
        raise NotImplementedError

    def create_shop_shipping_profile_destination(self):
        raise NotImplementedError

    def get_shop_shipping_profile_destinations_by_shipping_profile(
        self,
        shop_id: int,
        shipping_profile_id: int,
        limit: int = None,
        offset: int = None,
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/destinations"
        kwargs = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def delete_shop_shipping_profile_destination(
        self,
        shop_id: int,
        shipping_profile_id: int,
        shipping_profile_destination_id: int,
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/destinations/{shipping_profile_destination_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def update_shop_shipping_profile_destination(self):
        raise NotImplementedError

    def create_shop_shipping_profile_upgrade(self):
        raise NotImplementedError

    def get_shop_shipping_profile_upgrades(
        self, shop_id: int, shipping_profile_id: int
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/upgrades"
        return self._issue_request(uri)

    def delete_shop_shipping_profile_upgrade(
        self, shop_id: int, shipping_profile_id: int, upgrade_id: int
    ):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/upgrades/{upgrade_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def update_shop_shipping_profile_upgrade(self):
        raise NotImplementedError

    def get_shop(self, shop_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}"
        return self._issue_request(uri)

    def update_shop(self):
        raise NotImplementedError

    def get_shop_by_owner_user_id(self, user_id: int):
        uri = f"{ETSY_API_BASEURL}/users/{user_id}/shops"
        return self._issue_request(uri)

    def find_shops(self, shop_name: str, limit: int = None, offset: int = None):
        uri = f"{ETSY_API_BASEURL}/shops"
        kwargs = {"shop_name": shop_name, "limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def get_shop_production_partners(self, shop_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/production-partners"
        return self._issue_request(uri)

    def create_shop_section(self):
        raise NotImplementedError

    def get_shop_sections(self, shop_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/sections"
        return self._issue_request(uri)

    def delete_shop_section(self, shop_id: int, shop_section_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/sections/{shop_section_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def get_shop_section(self, shop_id: int, shop_section_id: int):
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/sections/{shop_section_id}"
        return self._issue_request(uri)

    def update_shop_section(self):
        raise NotImplementedError

    def get_user(self, user_id):
        uri = f"{ETSY_API_BASEURL}/users/{user_id}"
        return self._issue_request(uri)

    def get_authenticated_user(self):
        uri = f"{ETSY_API_BASEURL}/users/{self.user_id}"
        return self._issue_request(uri)

    def delete_user_address(self):
        raise NotImplementedError

    def get_user_address(self):
        raise NotImplementedError

    def get_user_addresses(self, limit: int = None, offset: int = None):
        uri = f"{ETSY_API_BASEURL}/user/addresses"
        kwargs = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def refresh(self):
        data = {
            "grant_type": "refresh_token",
            "client_id": self.keystring,
            "refresh_token": self.refresh_token,
        }
        del self.session.headers["Authorization"]
        r = self.session.post("https://api.etsy.com/v3/public/oauth/token", json=data)
        refreshed = r.json()
        self.token = refreshed["access_token"]
        self.refresh_token = refreshed["refresh_token"]
        tmp_expiry = datetime.now() + timedelta(seconds=refreshed["expires_in"])
        self.expiry = tmp_expiry.replace(tzinfo=timezone.utc).astimezone(tz=None)
        self.session.headers["Authorization"] = "Bearer " + self.token
        if self.refresh_save is not None:
            self.refresh_save(self.token, self.refresh_token, self.expiry)
        return self.token, self.refresh_token, self.expiry
