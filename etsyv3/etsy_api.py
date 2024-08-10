import enum
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests

from etsyv3.models import Request, UpdateListingRequest
from etsyv3.models.file_request import (
    FileRequest,
    UploadListingFileRequest,
    UploadListingImageRequest,
    UploadListingVideoRequest,
)
from etsyv3.models.listing_request import (
    CreateDraftListingRequest,
    UpdateListingInventoryRequest,
    UpdateListingPropertyRequest,
    UpdateVariationImagesRequest,
    UpdateListingImageIDRequest,
)
from etsyv3.models.receipt_request import (
    CreateReceiptShipmentRequest,
    UpdateShopReceiptRequest,
)
from etsyv3.models.shop_request import (
    CreateShopSectionRequest,
    UpdateShopRequest,
    UpdateShopSectionRequest,
)

# From spec at https://developers.etsy.com/documentation/essentials/urlsyntax
ETSY_API_BASEURL = "https://api.etsy.com/v3/application"

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
    GET = enum.auto()
    POST = enum.auto()
    PUT = enum.auto()
    DELETE = enum.auto()
    PATCH = enum.auto()


class EtsyAPI:
    def __init__(
        self,
        keystring: str,
        token: str,
        refresh_token: str,
        expiry: datetime,
        refresh_save: Optional[Callable[[str, str, datetime], None]] = None,
    ):
        self.session = requests.Session()
        self.token = token
        self.user_id = token.split(".")[0]
        self.refresh_token = refresh_token
        self.keystring = keystring
        self.session.headers = {
            "Accept": "application/json",
            "x-api-key": keystring,
            "Authorization": "Bearer " + self.token,
        }
        self.expiry = expiry
        self.refresh_save = refresh_save

    @staticmethod
    def _generate_get_uri(uri: str, **kwargs: Dict[str, Any]) -> str:
        if kwargs == {} or kwargs is None:
            return uri
        params = "&".join(
            [f"{key}={value}" for key, value in kwargs.items() if value is not None]
        )
        uri = f"{uri}?{params}" if params != "" else uri
        return uri

    def _issue_request(
        self,
        uri: str,
        method: Method = Method.GET,
        request_payload: Optional[Request] = None,
        **kwargs: Dict[str, Any],
    ) -> Any:
        if (
            method != Method.GET and method != Method.DELETE
        ) and request_payload is None:
            raise ValueError
        if datetime.utcnow() < self.expiry:
            if method == Method.GET:
                uri_full = EtsyAPI._generate_get_uri(uri, **kwargs)
                return_val = self.session.get(uri_full)
            elif method == Method.PUT and isinstance(request_payload, Request):
                return_val = self.session.put(uri, json=request_payload.get_dict())
            elif method == Method.POST and isinstance(request_payload, FileRequest):
                return_val = self.session.post(
                    uri, files=request_payload.file, data=request_payload.data
                )
            elif method == Method.POST and isinstance(request_payload, Request):
                return_val = self.session.post(uri, json=request_payload.get_dict())
            elif method == Method.PATCH and isinstance(request_payload, Request):
                return_val = self.session.patch(uri, json=request_payload.get_dict())
            elif method == Method.DELETE:
                return_val = self.session.delete(uri)
            else:
                raise Exception()
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
            elif return_val.status_code == 204:
                return {"status": "OK"}
            return return_val.json()

        else:
            self.refresh()
            rkw: Dict[str, Any] = kwargs
            return self._issue_request(uri, **rkw)

    def get_buyer_taxonomy_nodes(self) -> Any:
        uri = f"{ETSY_API_BASEURL}/buyer-taxonomy/nodes"
        return self._issue_request(uri)

    def get_properties_by_buyer_taxonomy_id(self, taxonomy_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/buyer-taxonomy/nodes/{taxonomy_id}/properties"
        return self._issue_request(uri)

    def get_seller_taxonomy_nodes(self) -> Any:
        uri = f"{ETSY_API_BASEURL}/seller-taxonomy/nodes"
        return self._issue_request(uri)

    def get_properties_by_taxonomy_id(self, taxonomy_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/seller-taxonomy/nodes/{taxonomy_id}/properties"
        return self._issue_request(uri)

    def create_draft_listing(
        self, shop_id: int, listing: CreateDraftListingRequest
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings"
        return self._issue_request(uri, method=Method.POST, request_payload=listing)

    def get_listings_by_shop(
        self,
        shop_id: int,
        state: Optional[ListingState] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_on: Optional[SortOn] = None,
        sort_order: Optional[SortOrder] = None,
        includes: Optional[List[Includes]] = None,
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings"
        kwargs: Dict[str, Any] = {
            "state": state.value if state is not None else None,
            "limit": limit,
            "offset": offset,
            "sort_on": sort_on.value if sort_on is not None else None,
            "sort_order": sort_order.value if sort_order is not None else None,
            "includes": ",".join([x.value for x in includes])
            if includes is not None
            else None,
        }
        return self._issue_request(uri, **kwargs)

    def delete_listing(self, listing_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def get_listing(
        self, listing_id: int, includes: Optional[List[Includes]] = None
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}"
        kwargs: Dict[str, Any] = {
            "includes": ",".join([x.value for x in includes])
            if includes is not None
            else None
        }
        return self._issue_request(uri, **kwargs)

    def find_all_listings_active(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        keywords: Optional[str] = None,
        sort_on: Optional[SortOn] = None,
        sort_order: Optional[SortOrder] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        shop_location: Optional[str] = None,
    ) -> Any:
        # not implementing taxonomy ids because I don't know what they are
        uri = f"{ETSY_API_BASEURL}/listings/active"
        kwargs: Dict[str, Any] = {
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
        shop_id: int,
        limit: Optional[int] = None,
        sort_on: Optional[SortOn] = None,
        sort_order: Optional[SortOrder] = None,
        offset: Optional[int] = None,
        keywords: Optional[str] = None,
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/active"
        kwargs: Dict[str, Any] = {
            "limit": limit,
            "sort_on": sort_on.value if sort_on is not None else None,
            "sort_order": sort_order.value if sort_order is not None else None,
            "offset": offset,
            "keywords": keywords,
        }
        return self._issue_request(uri, **kwargs)

    def get_listings_by_listing_ids(
        self, listing_ids: List[int], includes: Optional[List[Includes]] = None
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/listings/batch"
        kwargs: Dict[str, Any] = {
            "listing_ids": ",".join([str(x) for x in listing_ids])
            if listing_ids is not None
            else None,
            "includes": ",".join([x.value for x in includes])
            if includes is not None
            else None,
        }
        return self._issue_request(uri, **kwargs)

    def get_featured_listings_by_shop(
        self, shop_id: int, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/featured"
        kwargs: Dict[str, Any] = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def delete_listing_property(
        self, shop_id: int, listing_id: int, property_id: int
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/properties/{property_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def update_listing_property(
        self,
        shop_id: int,
        listing_id: int,
        property_id: int,
        listing_property: UpdateListingPropertyRequest,
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/properties/{property_id}"
        return self._issue_request(
            uri, method=Method.PUT, request_payload=listing_property
        )

    def get_listing_property(self, listing_id: int, property_id: int) -> Any:
        # not in production yet
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/properties/{property_id}"
        raise NotImplementedError

    def get_listing_properties(self, shop_id: int, listing_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/properties"
        return self._issue_request(uri)

    def update_listing(
        self, shop_id: int, listing_id: int, listing: UpdateListingRequest
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}"
        return self._issue_request(uri, method=Method.PATCH, request_payload=listing)

    def get_listings_by_shop_receipt(
        self,
        shop_id: int,
        receipt_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/receipts/{receipt_id}/listings"
        kwargs: Dict[str, Any] = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def get_listings_by_shop_section_id(
        self,
        shop_id: int,
        shop_section_ids: List[int],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_on: Optional[SortOn] = None,
        sort_order: Optional[SortOrder] = None,
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shop-sections/listings"
        kwargs: Dict[str, Any] = {
            "shop_section_ids": ",".join([str(x) for x in shop_section_ids])
            if shop_section_ids is not None
            else None,
            "limit": limit,
            "offset": offset,
            "sort_on": sort_on.value if sort_on is not None else None,
            "sort_order": sort_order.value if sort_order is not None else None,
        }
        return self._issue_request(uri, **kwargs)

    def delete_listing_file(
        self, shop_id: int, listing_id: int, listing_file_id: int
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/files/{listing_file_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def get_listing_file(
        self, shop_id: int, listing_id: int, listing_file_id: int
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/files/{listing_file_id}"
        return self._issue_request(uri)

    def get_all_listing_files(self, shop_id: int, listing_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/files"
        return self._issue_request(uri)

    def upload_listing_file(
        self, shop_id: int, listing_id: int, listing_file: UploadListingFileRequest
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/files"
        return self._issue_request(
            uri, method=Method.POST, request_payload=listing_file
        )

    def delete_listing_video(
        self, shop_id: int, listing_id: int, listing_video_id: int
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/videos/{listing_video_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def get_listing_video(self, listing_id: int, listing_video_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/videos/{listing_video_id}"
        return self._issue_request(uri)

    def get_listing_videos(self, listing_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/videos"
        return self._issue_request(uri)

    def upload_listing_video(
        self, shop_id: int, listing_id: int, listing_video: UploadListingVideoRequest
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/videos"
        return self._issue_request(
            uri, method=Method.POST, request_payload=listing_video
        )

    def delete_listing_image(
        self, shop_id: int, listing_id: int, listing_image_id: int
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/images/{listing_image_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def get_listing_image(self, listing_id: int, listing_image_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/images/{listing_image_id}"
        return self._issue_request(uri)

    def get_listing_images(self, listing_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/images"
        return self._issue_request(uri)

    def upload_listing_image(
        self, shop_id: int, listing_id: int, listing_image: UploadListingImageRequest
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/images"
        return self._issue_request(
            uri, method=Method.POST, request_payload=listing_image
        )
    
    def update_listing_image_id(
        self, shop_id: int, listing_id: int, listing_image_id: UpdateListingImageIDRequest
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/images"
        return self._issue_request(
            uri, method=Method.POST, request_payload=listing_image_id
        )

    def get_listing_inventory(self, listing_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/inventory"
        return self._issue_request(uri)

    def update_listing_inventory(
        self, listing_id: int, listing_inventory: UpdateListingInventoryRequest
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/inventory"
        return self._issue_request(uri, Method.PUT, listing_inventory)

    def get_listing_offering(
        self, listing_id: int, product_id: int, product_offering_id: int
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/products/{product_id}/offerings/{product_offering_id}"
        return self._issue_request(uri)

    def get_listing_product(self, listing_id: int, product_id: int) -> Any:
        uri = (
            f"{ETSY_API_BASEURL}/listings/{listing_id}/inventory/products/{product_id}"
        )
        return self._issue_request(uri)

    def create_listing_translation(self) -> Any:
        raise NotImplementedError

    def get_listing_translation(
        self, shop_id: int, listing_id: int, language: str
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/translations/{language}"
        return self._issue_request(uri)

    def update_listing_translation(self) -> Any:
        raise NotImplementedError

    def get_listing_variation_images(self, shop_id: int, listing_id: int) -> Any:
        uri = (
            f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/variation-images"
        )
        return self._issue_request(uri)

    def update_variation_images(
        self,
        shop_id: int,
        listing_id: int,
        variation_images: UpdateVariationImagesRequest,
    ) -> Any:
        uri = (
            f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/variation-images"
        )
        return self._issue_request(
            uri, method=Method.POST, request_payload=variation_images
        )

    def ping(self) -> Any:
        uri = f"{ETSY_API_BASEURL}/openapi-ping"
        return self._issue_request(uri)

    def token_scopes(self) -> Any:
        uri = f"{ETSY_API_BASEURL}/scopes"
        return self._issue_request(uri)

    def get_shop_payment_account_ledger_entry(
        self, shop_id: int, ledger_entry_id: int
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/payment-account/ledger-entries/{ledger_entry_id}"
        return self._issue_request(uri)

    def get_shop_payment_account_ledger_entries(
        self,
        shop_id: int,
        min_created: int,
        max_created: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/payment-account/ledger-entries"
        kwargs: Dict[str, Any] = {
            "min_created": min_created,
            "max_created": max_created,
            "limit": limit,
            "offset": offset,
        }
        return self._issue_request(uri, **kwargs)

    def get_payment_account_ledger_entry_payments(
        self, shop_id: int, ledger_entry_ids: List[int]
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/payment-account/ledger-entries/payments"
        kwargs: Dict[str, Any] = {
            "ledger_entry_ids": ",".join([str(x) for x in ledger_entry_ids])
            if ledger_entry_ids is not None
            else None
        }
        return self._issue_request(uri, **kwargs)

    def get_shop_payment_by_receipt_id(self, shop_id: int, receipt_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/receipts/{receipt_id}/payments"
        return self._issue_request(uri)

    def get_payments(self, shop_id: int, payment_ids: List[int]) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/payments"
        kwargs: Dict[str, Any] = {
            "payment_ids": ",".join([str(x) for x in payment_ids])
            if payment_ids is not None
            else None
        }
        return self._issue_request(uri, **kwargs)

    def get_shop_receipt(self, shop_id: int, receipt_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/receipts/{receipt_id}"
        return self._issue_request(uri)

    def update_shop_receipt(
        self,
        shop_id: int,
        receipt_id: int,
        update_shop_receipt_request: UpdateShopReceiptRequest,
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/receipts/{receipt_id}"
        return self._issue_request(
            uri, method=Method.PUT, request_payload=update_shop_receipt_request
        )

    def get_shop_receipts(
        self,
        shop_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        was_paid: bool = True,
        was_shipped: bool = False,
        was_canceled: Optional[bool] = None,
        min_created: Optional[int] = None,
        max_created: Optional[int] = None,
        min_last_modified: Optional[int] = None,
        max_last_modified: Optional[int] = None,
        sort_on: Optional[str] = None,
        sort_order: Optional[str] = None,
        was_delivered: Optional[bool] = None,
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/receipts"
        kwargs: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "was_paid": was_paid,
            "was_shipped": was_shipped,
            "was_canceled": was_canceled,
            "min_created": min_created,
            "max_created": max_created,
            "min_last_modified": min_last_modified,
            "max_last_modified": max_last_modified,
            "sort_on": sort_on,
            "sort_order": sort_order,
            "was_delivered": was_delivered,
        }
        return self._issue_request(uri, **kwargs)

    def create_receipt_shipment(
        self,
        shop_id: int,
        receipt_id: int,
        receipt_shipment_request: CreateReceiptShipmentRequest,
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/receipts/{receipt_id}/tracking"
        return self._issue_request(
            uri, method=Method.POST, request_payload=receipt_shipment_request
        )

    def get_shop_receipt_transactions_by_listing(
        self,
        shop_id: int,
        listing_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/listings/{listing_id}/transactions"
        kwargs: Dict[str, Any] = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def get_shop_receipt_transactions_by_receipt(
        self, shop_id: int, receipt_id: int
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/receipts/{receipt_id}/transactions"
        return self._issue_request(uri)

    def get_shop_receipt_transaction(self, shop_id: int, transaction_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/transactions/{transaction_id}"
        return self._issue_request(uri)

    def get_shop_receipt_transactions_by_shop(
        self, shop_id: int, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/transactions"
        kwargs: Dict[str, Any] = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def get_reviews_by_listing(
        self, listing_id: int, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/listings/{listing_id}/reviews"
        kwargs: Dict[str, Any] = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def get_reviews_by_shop(
        self, shop_id: int, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/reviews"
        kwargs: Dict[str, Any] = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def get_shipping_carriers(self, origin_country_iso: str) -> Any:
        uri = f"{ETSY_API_BASEURL}/shipping-carriers"
        kwargs: Dict[str, Any] = {"origin_country_iso": origin_country_iso}
        return self._issue_request(uri, **kwargs)

    def create_shop_shipping_profile(self) -> Any:
        raise NotImplementedError

    def get_shop_shipping_profiles(self, shop_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shipping-profiles"
        return self._issue_request(uri)

    def delete_shop_shipping_profile(
        self, shop_id: int, shipping_profile_id: int
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shipping-profiles/{shipping_profile_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def get_shop_shipping_profile(self, shop_id: int, shipping_profile_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shipping-profiles/{shipping_profile_id}"
        return self._issue_request(uri)

    def update_shop_shipping_profile(self) -> Any:
        raise NotImplementedError

    def create_shop_shipping_profile_destination(self) -> Any:
        raise NotImplementedError

    def get_shop_shipping_profile_destinations_by_shipping_profile(
        self,
        shop_id: int,
        shipping_profile_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/destinations"
        kwargs: Dict[str, Any] = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def delete_shop_shipping_profile_destination(
        self,
        shop_id: int,
        shipping_profile_id: int,
        shipping_profile_destination_id: int,
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/destinations/{shipping_profile_destination_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def update_shop_shipping_profile_destination(self) -> Any:
        raise NotImplementedError

    def create_shop_shipping_profile_upgrade(self) -> Any:
        raise NotImplementedError

    def get_shop_shipping_profile_upgrades(
        self, shop_id: int, shipping_profile_id: int
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/upgrades"
        return self._issue_request(uri)

    def delete_shop_shipping_profile_upgrade(
        self, shop_id: int, shipping_profile_id: int, upgrade_id: int
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/upgrades/{upgrade_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def update_shop_shipping_profile_upgrade(self) -> Any:
        raise NotImplementedError

    def get_shop(self, shop_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}"
        return self._issue_request(uri)

    def update_shop(self, shop_id: int, shop_request: UpdateShopRequest) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}"
        return self._issue_request(uri, method=Method.PUT, request_payload=shop_request)

    def get_shop_by_owner_user_id(self, user_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/users/{user_id}/shops"
        return self._issue_request(uri)

    def find_shops(
        self, shop_name: str, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops"
        kwargs: Dict[str, Any] = {
            "shop_name": shop_name,
            "limit": limit,
            "offset": offset,
        }
        return self._issue_request(uri, **kwargs)

    def get_shop_production_partners(self, shop_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/production-partners"
        return self._issue_request(uri)

    def create_shop_section(
        self, shop_id: int, shop_section_request: CreateShopSectionRequest
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/sections"
        return self._issue_request(
            uri, method=Method.POST, request_payload=shop_section_request
        )

    def get_shop_sections(self, shop_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/sections"
        return self._issue_request(uri)

    def delete_shop_section(self, shop_id: int, shop_section_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/sections/{shop_section_id}"
        return self._issue_request(uri, method=Method.DELETE)

    def get_shop_section(self, shop_id: int, shop_section_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/sections/{shop_section_id}"
        return self._issue_request(uri)

    def update_shop_section(
        self,
        shop_id: int,
        shop_section_id: int,
        shop_section_request: UpdateShopSectionRequest,
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/shops/{shop_id}/sections/{shop_section_id}"
        return self._issue_request(
            uri, method=Method.PUT, request_payload=shop_section_request
        )

    def get_user(self, user_id: int) -> Any:
        uri = f"{ETSY_API_BASEURL}/users/{user_id}"
        return self._issue_request(uri)

    def get_authenticated_user(self) -> Any:
        uri = f"{ETSY_API_BASEURL}/users/{self.user_id}"
        return self._issue_request(uri)

    def delete_user_address(self) -> Any:
        raise NotImplementedError

    def get_user_address(self) -> Any:
        raise NotImplementedError

    def get_user_addresses(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> Any:
        uri = f"{ETSY_API_BASEURL}/user/addresses"
        kwargs: Dict[str, Any] = {"limit": limit, "offset": offset}
        return self._issue_request(uri, **kwargs)

    def refresh(self) -> Tuple[str, str, datetime]:
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
        tmp_expiry = datetime.utcnow() + timedelta(seconds=refreshed["expires_in"])
        self.expiry = tmp_expiry
        self.session.headers["Authorization"] = "Bearer " + self.token
        if self.refresh_save is not None:
            self.refresh_save(self.token, self.refresh_token, self.expiry)
        return self.token, self.refresh_token, self.expiry
