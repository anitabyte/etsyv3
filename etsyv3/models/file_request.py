from etsyv3.models import Request


class FileRequest(Request):
    def __init__(self, nullable=None, mandatory=None):
        super().__init__(nullable=nullable, mandatory=mandatory)

    @staticmethod
    def generate_bytes_from_file(file):
        with open(file, "rb") as f:
            f_bytes = f.read()
        return f_bytes


class UploadListingImageRequest(FileRequest):
    nullable = ["file"]
    mandatory = []

    def __init__(
        self,
        image_bytes: bytes,
        listing_image_id=None,
        rank=None,
        overwrite=None,
        is_watermarked=None,
        alt_text=None,
    ):
        self.file = {"image": image_bytes}
        self.data = {
            "listing_image_id": listing_image_id,
            "rank": rank,
            "overwrite": overwrite,
            "is_watermarked": is_watermarked,
            "alt_text": alt_text,
        }

        super().__init__(
            nullable=UploadListingImageRequest.nullable,
            mandatory=UploadListingImageRequest.mandatory,
        )


class UploadListingFileRequest(FileRequest):
    nullable = ["file"]
    mandatory = []

    def __init__(
        self,
        file_bytes: bytes,
        listing_file_id=None,
        name=None,
        rank=None
    ):
        self.file = {"file": (name, file_bytes, 'multipart/form-data')}
        self.data = {
            "listing_file_id": listing_file_id,
            "rank": rank,
            "name": name
        }

        super().__init__(
            nullable=UploadListingFileRequest.nullable,
            mandatory=UploadListingFileRequest.mandatory,
        )
