from typing import List, Optional

from etsyv3.models.listing_request import Request


class CreateShopSectionRequest(Request):
    nullable: List[str] = []
    mandatory: List[str] = ["title"]

    def __init__(self, title: str):
        self.title = title

        super().__init__(
            nullable=CreateShopSectionRequest.nullable,
            mandatory=CreateShopSectionRequest.mandatory,
        )


class UpdateShopSectionRequest(Request):
    nullable: List[str] = []
    mandatory: List[str] = ["title"]

    def __init__(self, title: str):
        self.title = title

        super().__init__(
            nullable=UpdateShopSectionRequest.nullable,
            mandatory=UpdateShopSectionRequest.mandatory,
        )


class UpdateShopRequest(Request):
    nullable: List[str] = []
    mandatory: List[str] = []

    def __init__(
        self,
        title: Optional[str] = None,
        announcement: Optional[str] = None,
        sale_message: Optional[str] = None,
        digital_sale_message: Optional[str] = None,
        policy_additional: Optional[str] = None,
    ):
        self.title = title
        self.announcement = announcement
        self.sale_message = sale_message
        self.digital_sale_message = digital_sale_message
        self.policy_additional = policy_additional

        super().__init__(
            nullable=UpdateShopRequest.nullable,
            mandatory=UpdateShopRequest.mandatory,
        )
