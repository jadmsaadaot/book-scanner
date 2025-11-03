// BooksService - Manual implementation for Book Scanner API endpoints
import type { CancelablePromise } from './core/CancelablePromise';
import { OpenAPI } from './core/OpenAPI';
import { request as __request } from './core/request';
import type {
  BooksGetLibraryData,
  BooksGetLibraryResponse,
  BooksAddToLibraryData,
  BooksAddToLibraryResponse,
  BooksRemoveFromLibraryData,
  BooksRemoveFromLibraryResponse,
  BooksScanData,
  BooksScanResponse,
} from './types.gen';

export class BooksService {
  /**
   * Get Library
   * Get all books in user's library (profile books)
   * @param data The data for the request.
   * @param data.skip
   * @param data.limit
   * @returns BooksPublic Successful Response
   * @throws ApiError
   */
  public static getLibrary(
    data: BooksGetLibraryData = {}
  ): CancelablePromise<BooksGetLibraryResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/books/library',
      query: {
        skip: data.skip,
        limit: data.limit,
      },
      errors: {
        422: 'Validation Error',
      },
    });
  }

  /**
   * Add To Library
   * Add a book to user's library by Google Books ID
   * @param data The data for the request.
   * @param data.googleBooksId
   * @returns BookPublic Successful Response
   * @throws ApiError
   */
  public static addToLibrary(
    data: BooksAddToLibraryData
  ): CancelablePromise<BooksAddToLibraryResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/books/library/add/{google_books_id}',
      path: {
        google_books_id: data.googleBooksId,
      },
      errors: {
        400: 'Bad Request',
        404: 'Not Found',
        422: 'Validation Error',
      },
    });
  }

  /**
   * Remove From Library
   * Remove a book from user's library
   * @param data The data for the request.
   * @param data.bookId
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static removeFromLibrary(
    data: BooksRemoveFromLibraryData
  ): CancelablePromise<BooksRemoveFromLibraryResponse> {
    return __request(OpenAPI, {
      method: 'DELETE',
      url: '/api/v1/books/library/remove/{book_id}',
      path: {
        book_id: data.bookId,
      },
      errors: {
        404: 'Not Found',
        422: 'Validation Error',
      },
    });
  }

  /**
   * Scan Bookshelf
   * Upload an image and scan for books
   * @param data The data for the request.
   * @param data.file
   * @returns ScanResult Successful Response
   * @throws ApiError
   */
  public static scanBookshelf(
    data: BooksScanData
  ): CancelablePromise<BooksScanResponse> {
    const formData = new FormData();
    formData.append('file', data.file);

    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/books/scan',
      body: formData,
      mediaType: 'multipart/form-data',
      errors: {
        400: 'Bad Request',
        422: 'Validation Error',
      },
    });
  }
}
