import unittest

from etsyv3.enums import ListingRequestState, WhenMade, WhoMade
from etsyv3.models import UpdateListingRequest
from etsyv3.models.listing_request import (
    CreateDraftListingRequest,
    UpdateListingInventoryRequest,
)
from etsyv3.models.product import Product
from etsyv3.util import todict


class TestListingRequest(unittest.TestCase):
    def test_nullable(self):
        listing = UpdateListingRequest(
            tags=[], title="A title!", who_made=WhoMade.I_DID
        )
        self.assertEqual(len(listing.get_nulled()), 1)
        self.assertEqual(3, len(listing.get_dict()))

    def test_required_missing(self):
        with self.assertRaises(ValueError):
            listing = CreateDraftListingRequest(
                quantity=1, title="Another title!", description="Description"
            )

    def test_required(self):
        listing = CreateDraftListingRequest(
            quantity=1,
            title="Another title!",
            description="Description",
            price=1.10,
            who_made=WhoMade.I_DID,
            when_made=WhenMade.MADE_TO_ORDER,
            taxonomy_id=1,
            tags=[],
        )
        self.assertEqual(8, len(listing.get_dict()))
        self.assertTrue("_nullable" not in listing.get_dict().keys())
        self.assertTrue("nullable" not in listing.get_dict().keys())
        self.assertEqual("i_did", listing.get_dict()["who_made"])

    def test_listing_inventory_request(self):
        properties = [
            {
                "property_id": 1,
                "value_ids": [1],
                "scale_id": 1,
                "property_name": "string",
                "values": ["string"],
            }
        ]
        offerings = [{"price": 0, "quantity": 0, "is_enabled": True}]
        product1 = Product("PRODUCT1", properties, offerings)
        product2 = Product("PRODUCT2", properties, offerings)
        product3 = Product("PRODUCT3", properties, offerings)
        product_list = [product1, product2, product3]
        listing_inventory_request = UpdateListingInventoryRequest(product_list, 0, 0, 0)
        self.assertEqual(3, len(listing_inventory_request.products))
        self.assertEqual(
            "PRODUCT1", listing_inventory_request.get_dict()["products"][0]["sku"]
        )

    def test_create_listing_inventory_request_from_response(self):
        response = {
            "products": [
                {
                    "product_id": 1,
                    "sku": "string",
                    "is_deleted": True,
                    "offerings": [
                        {
                            "offering_id": 1,
                            "quantity": 0,
                            "is_enabled": True,
                            "is_deleted": True,
                            "price": {
                                "amount": 0,
                                "divisor": 0,
                                "currency_code": "string",
                            },
                        }
                    ],
                    "property_values": [
                        {
                            "property_id": 1,
                            "property_name": "string",
                            "scale_id": 1,
                            "scale_name": "string",
                            "value_ids": [1],
                            "values": ["string"],
                        }
                    ],
                }
            ],
            "price_on_property": [0],
            "quantity_on_property": [0],
            "sku_on_property": [0],
            "listing": {
                "listing_id": 1,
                "user_id": 1,
                "shop_id": 1,
                "title": "string",
                "description": "string",
                "state": "active",
                "creation_timestamp": 946684800,
                "created_timestamp": 946684800,
                "ending_timestamp": 946684800,
                "original_creation_timestamp": 946684800,
                "last_modified_timestamp": 946684800,
                "updated_timestamp": 946684800,
                "state_timestamp": 946684800,
                "quantity": 0,
                "shop_section_id": 1,
                "featured_rank": 0,
                "url": "string",
                "num_favorers": 0,
                "non_taxable": True,
                "is_taxable": True,
                "is_customizable": True,
                "is_personalizable": True,
                "personalization_is_required": True,
                "personalization_char_count_max": 0,
                "personalization_instructions": "string",
                "listing_type": "physical",
                "tags": [],
                "materials": [],
                "shipping_profile_id": 1,
                "processing_min": 0,
                "processing_max": 0,
                "who_made": "i_did",
                "when_made": "made_to_order",
                "is_supply": True,
                "item_weight": 0,
                "item_weight_unit": "oz",
                "item_length": 0,
                "item_width": 0,
                "item_height": 0,
                "item_dimensions_unit": "in",
                "is_private": True,
                "style": [],
                "file_data": "string",
                "has_variations": True,
                "should_auto_renew": True,
                "language": "string",
                "price": {},
                "taxonomy_id": 0,
            },
        }
