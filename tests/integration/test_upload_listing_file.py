import unittest

from etsyv3.models.file_request import (
    UploadListingFileRequest,
)
from tests.integration.integration_helpers import (
    get_api_client,
    create_test_listing,
    delete_test_listing,
    open_cred_file,
)


class TestUploadListingFile(unittest.TestCase):
    def setUp(self) -> None:
        self.api = get_api_client()
        self.shop_id = open_cred_file()["shop_id"]
        self.listing_id = create_test_listing(self.api, self.shop_id)

    def testUploadListingImage(self) -> None:
        listing_file_upload = UploadListingFileRequest(
            file_bytes=UploadListingFileRequest.generate_bytes_from_file(
                "tests/integration/gengar.png"
            ),
            name="samplefile.png",
        )
        self.api.upload_listing_file(self.shop_id, self.listing_id, listing_file_upload)

    def tearDown(self) -> None:
        delete_test_listing(self.api, self.shop_id, self.listing_id)
