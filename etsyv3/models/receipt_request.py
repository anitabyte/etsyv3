from typing import List, Optional, Union

from etsyv3.enums import ShippingProvider
from etsyv3.models.listing_request import Request


class CreateReceiptShipmentRequest(Request):
    nullable: List[str] = []
    mandatory: List[str] = []

    def __init__(
        self,
        tracking_code: Optional[str] = None,
        carrier_name: Optional[Union[ShippingProvider, str]] = None,
        send_bcc: Optional[bool] = None,
        note_to_buyer: Optional[str] = None,
    ):
        self.tracking_code = tracking_code
        self.carrier_name = carrier_name
        self.send_bcc = send_bcc
        self.note_to_buyer = note_to_buyer

        super().__init__(
            nullable=CreateReceiptShipmentRequest.nullable,
            mandatory=CreateReceiptShipmentRequest.mandatory,
        )


class UpdateShopReceiptRequest(Request):
    nullable: List[str] = [
        "was_shipped",
        "was_paid",
    ]
    mandatory: List[str] = []

    def __init__(
        self,
        was_shipped: Optional[bool] = None,
        was_paid: Optional[bool] = None,
    ):
        self.was_shipped = was_shipped
        self.was_paid = was_paid

        super().__init__(
            nullable=UpdateShopReceiptRequest.nullable,
            mandatory=UpdateShopReceiptRequest.mandatory,
        )
