import unittest

from etsyv3.models.file_request import UploadListingImageRequest
from tests.integration.integration_helpers import (
    get_api_client,
    create_test_listing,
    delete_test_listing,
    open_cred_file,
)


class TestUploadListingImage(unittest.TestCase):
    def setUp(self) -> None:
        self.api = get_api_client()
        self.shop_id = open_cred_file()["shop_id"]
        self.listing_id = create_test_listing(self.api, self.shop_id)

    def testUploadListingImage(self) -> None:
        listing_image_upload = UploadListingImageRequest(
            image_bytes=UploadListingImageRequest.generate_bytes_from_file(
                "tests/integration/gengar.png"
            )
        )
        self.api.upload_listing_image(
            self.shop_id, self.listing_id, listing_image_upload
        )

    def tearDown(self) -> None:
        delete_test_listing(self.api, self.shop_id, self.listing_id)
