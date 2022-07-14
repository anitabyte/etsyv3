from enum import Enum
from typing import Any, Dict, List

from etsyv3.enums import (
    ItemDimensionsUnit,
    ItemWeightUnit,
    ListingRequestState,
    ListingType,
    WhenMade,
    WhoMade,
)
from etsyv3.models.product import Product
from etsyv3.util import todict


class Request:
    def __init__(self, nullable: List[str] = None, mandatory: List[str] = None):
        self._nullable = nullable
        self._mandatory = mandatory
        if not self.check_mandatory():
            raise ValueError

    def check_mandatory(self) -> bool:
        if self.mandatory is not None:
            for key in self.mandatory:
                try:
                    if self.__dict__[key] is None:
                        return False
                except Exception:
                    return False
        return True

    def get_nulled(self) -> List[str]:
        return [
            key
            for key, value in self.__dict__.items()
            if key in self._nullable and (value == [] or value == "" or value == 0)
        ]

    def get_dict(self) -> Dict[str, Any]:
        nulled = self.get_nulled()
        return todict(self, nullable=self._nullable)


class CreateDraftListingRequest(Request):
    nullable = [
        "shipping_profile_id",
        "materials",
        "shop_section_id",
        "processing_min",
        "processing_max",
        "tags",
        "styles",
        "item_weight",
        "item_length",
        "item_width",
        "item_height",
        "item_weight_unit",
        "item_dimensions_unit",
        "production_partner_ids",
        "image_ids",
    ]
    mandatory = [
        "quantity",
        "title",
        "description",
        "price",
        "who_made",
        "when_made",
        "taxonomy_id",
    ]

    def __init__(
        self,
        quantity: int = None,
        title: str = None,
        description: str = None,
        price: float = None,
        who_made: WhoMade = None,
        when_made: WhenMade = None,
        taxonomy_id: int = None,
        shipping_profile_id: int = None,
        materials: List[str] = None,
        shop_section_id: int = None,
        processing_min: int = None,
        processing_max: int = None,
        tags: List[str] = None,
        styles: List[str] = None,
        item_weight: float = None,
        item_length: float = None,
        item_width: float = None,
        item_height: float = None,
        item_weight_unit: ItemWeightUnit = None,
        item_dimensions_unit: ItemDimensionsUnit = None,
        is_personalizable: bool = None,
        personalization_is_required: bool = None,
        personalization_char_count_max: int = None,
        personalization_instructions: str = None,
        production_partner_ids: int = None,
        image_ids: List[int] = None,
        is_supply: bool = None,
        is_customizable: bool = None,
        should_auto_renew: bool = None,
        is_taxable: bool = None,
        listing_type: ListingType = None,
    ):
        self.quantity = quantity
        self.title = title
        self.description = description
        self.price = price
        self.who_made = who_made
        self.when_made = when_made
        self.taxonomy_id = taxonomy_id
        self.shipping_profile_id = shipping_profile_id
        self.materials = materials
        self.shop_section_id = shop_section_id
        self.processing_min = processing_min
        self.processing_max = processing_max
        self.tags = tags
        self.styles = styles
        self.item_weight = item_weight
        self.item_length = item_length
        self.item_width = item_width
        self.item_height = item_height
        self.item_weight_unit = item_weight_unit
        self.item_dimensions_unit = item_dimensions_unit
        self.is_personalizable = is_personalizable
        self.personalization_is_required = personalization_is_required
        self.personalization_char_count_max = personalization_char_count_max
        self.personalization_instructions = personalization_instructions
        self.production_partner_ids = production_partner_ids
        self.image_ids = image_ids
        self.is_supply = is_supply
        self.is_customizable = is_customizable
        self.should_auto_renew = should_auto_renew
        self.is_taxable = is_taxable
        self.listing_type = listing_type
        super().__init__(
            nullable=CreateDraftListingRequest.nullable,
            mandatory=CreateDraftListingRequest.mandatory,
        )


class UpdateListingRequest(Request):
    nullable = [
        "materials",
        "shipping_profile_id",
        "shop_section_id",
        "item_weight",
        "item_length",
        "item_width",
        "item_height",
        "item_weight_unit",
        "item_dimensions_unit",
        "tags",
        "featured_rank",
        "production_partner_ids",
        "type",
    ]

    mandatory = []

    def __init__(
        self,
        image_ids: List[str] = None,
        title: str = None,
        description: str = None,
        materials: List[str] = None,
        should_auto_renew: bool = None,
        shipping_profile_id: int = None,
        shop_section_id: int = None,
        item_weight: float = None,
        item_length: float = None,
        item_width: float = None,
        item_height: float = None,
        item_weight_unit: ItemWeightUnit = None,
        item_dimensions_unit: ItemDimensionsUnit = None,
        is_taxable: bool = None,
        taxonomy_id: int = None,
        tags: List[str] = None,
        who_made: WhoMade = None,
        when_made: WhenMade = None,
        featured_rank: int = None,
        is_personalizable: bool = None,
        personalization_is_required: bool = None,
        personalization_char_count_max: int = None,
        personalization_instructions: str = None,
        state: ListingRequestState = None,
        is_supply: bool = None,
        production_partner_ids: List[int] = None,
        listing_type: ListingType = None,
    ):
        self.image_ids = image_ids
        self.title = title
        self.description = description
        self.materials = materials
        self.should_auto_renew = should_auto_renew
        self.shipping_profile_id = shipping_profile_id
        self.shop_section_id = shop_section_id
        self.item_weight = item_weight
        self.item_length = item_length
        self.item_width = item_width
        self.item_height = item_height
        self.item_weight_unit = item_weight_unit
        self.item_dimensions_unit = item_dimensions_unit
        self.is_taxable = is_taxable
        self.taxonomy_id = taxonomy_id
        self.tags = tags
        self.who_made = who_made
        self.when_made = when_made
        self.featured_rank = featured_rank
        self.is_personalizable = is_personalizable
        self.personalization_is_required = personalization_is_required
        self.personalization_char_count_max = personalization_char_count_max
        self.personalization_instructions = personalization_instructions
        self.state = state
        self.is_supply = is_supply
        self.production_partner_ids = production_partner_ids
        self.listing_type = listing_type
        super().__init__(nullable=UpdateListingRequest.nullable)


class UpdateListingInventoryRequest(Request):
    nullable = []
    mandatory = ["products"]

    def __init__(
        self,
        products: List[Product],
        price_on_property=None,
        quantity_on_property=None,
        sku_on_property=None,
    ):
        self.products = products
        self.price_on_property = price_on_property
        self.quantity_on_property = quantity_on_property
        self.sku_on_property = sku_on_property
        super().__init__(
            nullable=UpdateListingInventoryRequest.nullable,
            mandatory=UpdateListingInventoryRequest.mandatory,
        )

    @staticmethod
    def generate_request_from_inventory_response(response):
        products = []
        for product in response["products"]:
            property_values = product["property_values"]
            for prop_val in property_values:
                prop_val.pop("scale_name", None)
                prop_val.pop("value_pairs", None)
            offerings = product["offerings"]
            for offering in offerings:
                offering.pop("is_deleted", None)
                offering.pop("offering_id", None)
                offering["price"] = (
                    offering["price"]["amount"] / offering["price"]["divisor"]
                )
            products.append(Product(product["sku"], property_values, offerings))
        price_on_property = response["price_on_property"]
        quantity_on_property = response["quantity_on_property"]
        sku_on_property = response["sku_on_property"]
        return UpdateListingInventoryRequest(
            products, price_on_property, quantity_on_property, sku_on_property
        )


class UpdateVariationImagesRequest(Request):
    nullable = []
    mandatory = []

    def __init__(self, variation_images: List[Dict[str, Any]]):
        self.variation_images = variation_images
        super().__init__(
            nullable=UpdateVariationImagesRequest.nullable,
            mandatory=UpdateVariationImagesRequest.mandatory,
        )

    @staticmethod
    def generate_request_from_variation_images_response(response):
        variation_images = response["results"]
        for variation_image in variation_images:
            variation_image.pop("value", None)
        return UpdateVariationImagesRequest(variation_images)
