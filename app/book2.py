from fastapi import FastAPI, HTTPException, Request, status, Form, Header
from pydantic import BaseModel, Field
from uuid import UUID
from fastapi.responses import JSONResponse
from typing import List


class NegativeNumberException(Exception):
    def __init__(self, books_to_return):
        self.books_to_return = books_to_return


app = FastAPI()


@app.exception_handler(NegativeNumberException)
async def negative_number_exception_handler(request: Request, exception: NegativeNumberException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Hey, why do you want {exception.books_to_return}."}
    )


class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: str = Field(title="Description of the book",
                             max_length=100, min_length=1, default=None)
    rating: int = Field(gt=0, le=5)

    class Config:
        json_schema_extra = {
            "example": {
               "id": "3c3fcc29-b85d-4ac2-9bbc-7b4d89274248",
               "title": "ExampleTitle",
               "author": "HHGHGHG",
               "description": "JGGHGHJGHG",
               "rating": 5,
            }
        }


class BookNoRating(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str
    description: str = Field(title="description of the Book",
                             max_length=100, min_length=1, default=None)


BOOKS = []


@app.post('/books/login')
async def book_login(username: str = Form(), password: str = Form()):
    return {'username': username, 'password': password}


@app.post('/books/login2/')
async def book_login(book_id: int, username: str = Header(None), password: str = Header(None)):
    if username == 'FastApiUser' and password == 'test1234!':
        return BOOKS[book_id]
    return 'Invalid User'


@app.get('/header')
async def read_header(random_header: str = Header(None)):
    return {'Random-Header': random_header}


@app.get("/")
async def read_all_books(books_to_return: int = None):
    if books_to_return and books_to_return < 0:
        raise NegativeNumberException(books_to_return=books_to_return)
    if len(BOOKS) < 1:
        create_books_no_api()
    if books_to_return and len(BOOKS) >= books_to_return > 0:
        i = 1
        new_books = []
        while i <= books_to_return:
            new_books.append(BOOKS[i - 1])
            i += 1
        return new_books
    return BOOKS


@app.get("/book/{book_id}")
async def read_book(book_id: UUID):
    for x in BOOKS:
        if x.id == book_id:
            return x
    raise raise_item_cannot_be_found_exception()


@app.get("/book/rating/{book_id}", response_model=BookNoRating)
async def read_book_no_rating(book_id: UUID):
    for x in BOOKS:
        if x.id == book_id:
            return x
    raise raise_item_cannot_be_found_exception()


@app.put("/{book_id}")
async def update_book(book_id: UUID, book: Book):
    counter = 0
    for x in BOOKS:
        counter += 1
        if x.id == book_id:
            BOOKS[counter - 1] = book
            return BOOKS[counter - 1]
    raise  raise_item_cannot_be_found_exception()


@app.delete("/{book_id}")
async def delete_book(book_id: UUID):
    counter = 0
    for x in BOOKS:
        counter += 1
        if x.id == book_id:
            del BOOKS[counter - 1]
            return f"ID:{book_id} deleted"
    raise raise_item_cannot_be_found_exception()


@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(book: Book):
    BOOKS.append(book)
    return book


def create_books_no_api():
    book_1 = Book(id="5c3fcc29-b85d-4ac2-9bbc-7b4d89274248",
                  title="Title1",
                  author="Author1",
                  description="Description1",
                  rating=4)
    book_2 = Book(id="1c01a2d0-afd1-4d5d-8fa9-fecfb4a57d36",
                  title="Title2",
                  author="Author2",
                  description="Description2",
                  rating=5)
    book_3 = Book(id="079e6124-d4e1-42b1-9e13-da5c49bb2080",
                  title="Title3",
                  author="Author3",
                  description="Description3",
                  rating=4)
    book_4 = Book(id="f10df664-7d5d-4f49-828e-071be36066e4",
                  title="Title4",
                  author="Author4",
                  description="Description4",
                  rating=5)
    BOOKS.append(book_1)
    BOOKS.append(book_2)
    BOOKS.append(book_3)
    BOOKS.append(book_4)


def raise_item_cannot_be_found_exception():
    return HTTPException(status_code=404,
                         detail="Book not found",
                         headers={"X-Header_Error": "Nothing to be seen at hte UUID."}
                         )
