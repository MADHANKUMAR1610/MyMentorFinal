from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class StorageService:
    """
    Handles physical file storage.

    Currently supports local storage.
    S3 storage can be added later without changing the API layer.
    """

    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        self.storage_path = Path(settings.STORAGE_LOCAL_PATH)
        self.public_base_url = settings.PUBLIC_BASE_URL.rstrip("/")

    async def save_file(
        self,
        file: UploadFile,
        folder: str = "files",
    ) -> tuple[str, str, int]:
        """
        Save an uploaded file to storage.

        Returns:
            storage_path, public_url, file_size
        """

        if self.storage_type != "local":
            raise NotImplementedError(
                f"Storage type '{self.storage_type}' is not supported yet."
            )

        folder_path = self.storage_path / folder
        folder_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        original_filename = file.filename or "file"

        extension = Path(original_filename).suffix.lower()

        unique_filename = f"{uuid4()}{extension}"

        relative_path = Path(folder) / unique_filename
        absolute_path = self.storage_path / relative_path

        file_size = 0

        with absolute_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)

                if file_size > settings.MAX_UPLOAD_SIZE:
                    absolute_path.unlink(missing_ok=True)

                    raise ValueError(
                        "File size exceeds the maximum allowed limit."
                    )

                buffer.write(chunk)

        storage_path = relative_path.as_posix()

        public_url = (
            f"{self.public_base_url}/uploads/{storage_path}"
        )

        return (
            storage_path,
            public_url,
            file_size,
        )