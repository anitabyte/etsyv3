from etsyv3.models.listing_request import Request


class CreateShopSectionRequest(Request):
    nullable = []
    mandatory = ["title"]

    def __init__(self, title: str):
        self.title = title

        super().__init__(
            nullable=CreateShopSectionRequest.nullable,
            mandatory=CreateShopSectionRequest.mandatory,
        )


class UpdateShopSectionRequest(Request):
    nullable = []
    mandatory = ["title"]

    def __init__(self, title: str):
        self.title = title

        super().__init__(
            nullable=UpdateShopSectionRequest.nullable,
            mandatory=UpdateShopSectionRequest.mandatory,
        )


class UpdateShopRequest(Request):
    nullable = []
    mandatory = []

    def __init__(
        self,
        title: str = None,
        announcement: str = None,
        sale_message: str = None,
        digital_sale_message: str = None,
        policy_additional: str = None,
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
