from enum import Enum

class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    MD = "md"
    TXT = "txt"
    IMAGE = "image"
    OTHER = "other"