import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# Book Scanner Models

# Shared properties for Book
class BookBase(SQLModel):
    title: str = Field(max_length=500)
    author: str | None = Field(default=None, max_length=500)
    isbn: str | None = Field(default=None, max_length=13, index=True)
    publisher: str | None = Field(default=None, max_length=255)
    published_date: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None)
    page_count: int | None = None
    categories: str | None = Field(default=None, max_length=500)  # JSON string of categories
    thumbnail_url: str | None = Field(default=None, max_length=1000)
    google_books_id: str | None = Field(default=None, max_length=100, index=True)
    average_rating: float | None = None
    ratings_count: int | None = None


# Database model for Book
class Book(BookBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_libraries: list["UserLibrary"] = Relationship(back_populates="book")


# Properties to return via API
class BookPublic(BookBase):
    id: uuid.UUID


class BooksPublic(SQLModel):
    data: list[BookPublic]
    count: int


# User Library - Junction table between User and Book
class UserLibrary(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    book_id: uuid.UUID = Field(foreign_key="book.id", nullable=False, ondelete="CASCADE")
    added_date: str = Field(default_factory=lambda: str(uuid.uuid4()))  # Will be replaced with actual date
    notes: str | None = Field(default=None)

    # Relationships
    user: User | None = Relationship()
    book: Book | None = Relationship(back_populates="user_libraries")


# Response for detected books from scanning
class DetectedBook(SQLModel):
    title: str
    author: str | None = None
    isbn: str | None = None
    thumbnail_url: str | None = None
    google_books_id: str | None = None
    confidence: float  # OCR confidence score
    match_score: float  # How well it matches user's library
    in_library: bool = False
    recommendation_explanation: str | None = None  # Why this book was recommended


class ScanResult(SQLModel):
    detected_books: list[DetectedBook]
    recommendations: list[DetectedBook]  # Books not in library, sorted by relevance
