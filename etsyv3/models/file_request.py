from typing import Any, Dict, List, Optional

from etsyv3.models import Request


class FileRequest(Request):
    def __init__(
        self,
        nullable: Optional[List[str]] = None,
        mandatory: Optional[List[str]] = None,
    ) -> None:
        self.file: Dict[str, Any] = self.file if self.file is not None else None
        self.data: Dict[str, Any] = self.data if self.data is not None else None
        super().__init__(nullable=nullable, mandatory=mandatory)

    @staticmethod
    def generate_bytes_from_file(file: str) -> bytes:
        with open(file, "rb") as f:
            f_bytes = f.read()
        return f_bytes


class UploadListingImageRequest(FileRequest):
    nullable: List[str] = ["file"]
    mandatory: List[str] = []

    def __init__(
        self,
        image_bytes: bytes,
        listing_image_id: Optional[int] = None,
        rank: Optional[int] = None,
        overwrite: Optional[bool] = None,
        is_watermarked: Optional[bool] = None,
        alt_text: Optional[str] = None,
    ) -> None:
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
    nullable: List[str] = ["file"]
    mandatory: List[str] = []

    def __init__(
        self,
        file_bytes: bytes,
        listing_file_id: Optional[int] = None,
        name: Optional[str] = None,
        rank: Optional[int] = None,
    ) -> None:
        self.file = {"file": (name, file_bytes, "multipart/form-data")}
        self.data = {"listing_file_id": listing_file_id, "rank": rank, "name": name}

        super().__init__(
            nullable=UploadListingFileRequest.nullable,
            mandatory=UploadListingFileRequest.mandatory,
        )


class UploadListingVideoRequest(FileRequest):
    nullable: List[str] = ["video"]
    mandatory: List[str] = []

    def __init__(
        self,
        video_bytes: bytes,
        listing_video_id: Optional[int] = None,
        name: Optional[str] = None,
    ) -> None:
        self.file = {"video": video_bytes}
        self.data = {
            "listing_video_id": listing_video_id,
            "name": name,
        }

        super().__init__(
            nullable=UploadListingVideoRequest.nullable,
            mandatory=UploadListingVideoRequest.mandatory,
        )
