from pydantic import BaseModel


class StudentImportRow(BaseModel):
    name: str
    email: str
    phone: str
    department: str
    year: str


class StudentImportResponse(BaseModel):
    imported_count: int
    students: list[dict]