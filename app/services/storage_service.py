from pathlib import Path
from uuid import uuid4

import cloudinary
import cloudinary.uploader

from fastapi import UploadFile

from app.core.config import settings


class StorageService:
    """
    Handles file storage.

    Supported storage types:
        - local
        - cloudinary

    Local storage is useful for development.

    Cloudinary should be used in production because
    Render's local filesystem is ephemeral and files can
    disappear after redeployment.
    """

    def __init__(self):

        self.storage_type = settings.STORAGE_TYPE.lower().strip()

        # =========================================================
        # CLOUDINARY
        # =========================================================

        if self.storage_type == "cloudinary":

            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True,
            )

        # =========================================================
        # LOCAL STORAGE
        # =========================================================

        elif self.storage_type == "local":

            self.storage_path = Path(
                settings.STORAGE_LOCAL_PATH
            )

            self.public_base_url = (
                settings.PUBLIC_BASE_URL.rstrip("/")
            )

        # =========================================================
        # INVALID STORAGE TYPE
        # =========================================================

        else:

            raise ValueError(
                f"Unsupported storage type: "
                f"{self.storage_type}"
            )

    # =============================================================
    # SAVE FILE
    # =============================================================

    async def save_file(
        self,
        file: UploadFile,
        folder: str = "files",
    ) -> tuple[str, str, int]:
        """
        Save an uploaded file.

        Returns:
            (
                storage_path,
                public_url,
                file_size
            )

        For Cloudinary:
            storage_path = Cloudinary public_id
            public_url = Cloudinary secure URL

        For local:
            storage_path = relative filesystem path
            public_url = local API URL
        """

        # =========================================================
        # VALIDATE FILENAME
        # =========================================================

        original_filename = (
            file.filename or "file"
        )

        extension = (
            Path(original_filename)
            .suffix
            .lower()
        )

        # =========================================================
        # CLOUDINARY STORAGE
        # =========================================================

        if self.storage_type == "cloudinary":

            contents = await file.read()

            file_size = len(contents)

            # -----------------------------------------------------
            # FILE SIZE VALIDATION
            # -----------------------------------------------------

            if file_size > settings.MAX_UPLOAD_SIZE:

                raise ValueError(
                    "File size exceeds the maximum "
                    "allowed limit."
                )

            # -----------------------------------------------------
            # GENERATE UNIQUE PUBLIC ID
            # -----------------------------------------------------

            # Example:
            #
            # mymentor/files/550e8400-e29b-41d4-a716-446655440000
            #
            public_id = (
                f"mymentor/"
                f"{folder}/"
                f"{uuid4()}"
            )

            # -----------------------------------------------------
            # UPLOAD TO CLOUDINARY
            # -----------------------------------------------------

            result = cloudinary.uploader.upload(
                contents,
                public_id=public_id,
                resource_type="auto",
                overwrite=False,
            )

            # -----------------------------------------------------
            # CLOUDINARY VALUES
            # -----------------------------------------------------

            storage_path = result["public_id"]

            public_url = result["secure_url"]

            # -----------------------------------------------------
            # RETURN
            # -----------------------------------------------------

            return (
                storage_path,
                public_url,
                file_size,
            )

        # =========================================================
        # LOCAL STORAGE
        # =========================================================

        if self.storage_type == "local":

            folder_path = (
                self.storage_path / folder
            )

            folder_path.mkdir(
                parents=True,
                exist_ok=True,
            )

            # -----------------------------------------------------
            # UNIQUE FILE NAME
            # -----------------------------------------------------

            unique_filename = (
                f"{uuid4()}"
                f"{extension}"
            )

            relative_path = (
                Path(folder)
                / unique_filename
            )

            absolute_path = (
                self.storage_path
                / relative_path
            )

            # -----------------------------------------------------
            # WRITE FILE
            # -----------------------------------------------------

            file_size = 0

            with absolute_path.open("wb") as buffer:

                while chunk := await file.read(
                    1024 * 1024
                ):

                    file_size += len(chunk)

                    # ---------------------------------------------
                    # FILE SIZE VALIDATION
                    # ---------------------------------------------

                    if (
                        file_size
                        > settings.MAX_UPLOAD_SIZE
                    ):

                        absolute_path.unlink(
                            missing_ok=True
                        )

                        raise ValueError(
                            "File size exceeds the "
                            "maximum allowed limit."
                        )

                    buffer.write(chunk)

            # -----------------------------------------------------
            # STORAGE PATH
            # -----------------------------------------------------

            storage_path = (
                relative_path.as_posix()
            )

            # -----------------------------------------------------
            # PUBLIC URL
            # -----------------------------------------------------

            public_url = (
                f"{self.public_base_url}"
                f"/uploads/"
                f"{storage_path}"
            )

            # -----------------------------------------------------
            # RETURN
            # -----------------------------------------------------

            return (
                storage_path,
                public_url,
                file_size,
            )

        # =========================================================
        # SAFETY CHECK
        # =========================================================

        raise ValueError(
            f"Unsupported storage type: "
            f"{self.storage_type}"
        )