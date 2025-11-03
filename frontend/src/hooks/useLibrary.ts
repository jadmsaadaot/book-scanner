import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import {
  type ApiError,
  type BookPublic,
  type BooksPublic,
  BooksService,
} from "@/client"
import { handleError } from "@/utils"

/**
 * Custom hook for managing user's library (profile books)
 * Handles fetching, adding, and removing books from the library
 */
const useLibrary = () => {
  const queryClient = useQueryClient()

  // Fetch library books
  const {
    data: library,
    isLoading,
    error,
  } = useQuery<BooksPublic, Error>({
    queryKey: ["library"],
    queryFn: () => BooksService.getLibrary({ skip: 0, limit: 100 }),
  })

  // Add book to library mutation
  const addBookMutation = useMutation({
    mutationFn: (googleBooksId: string) =>
      BooksService.addToLibrary({ googleBooksId }),
    onSuccess: (newBook: BookPublic) => {
      // Optimistically update the cache
      queryClient.setQueryData<BooksPublic>(["library"], (old) => {
        if (!old) return { data: [newBook], count: 1 }
        return {
          data: [...old.data, newBook],
          count: old.count + 1,
        }
      })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: ["library"] })
    },
  })

  // Remove book from library mutation
  const removeBookMutation = useMutation({
    mutationFn: (bookId: string) =>
      BooksService.removeFromLibrary({ bookId }),
    onSuccess: (_, bookId) => {
      // Optimistically update the cache
      queryClient.setQueryData<BooksPublic>(["library"], (old) => {
        if (!old) return old
        return {
          data: old.data.filter((book) => book.id !== bookId),
          count: old.count - 1,
        }
      })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: ["library"] })
    },
  })

  return {
    library,
    isLoading,
    error,
    addBook: addBookMutation.mutate,
    addBookAsync: addBookMutation.mutateAsync,
    isAddingBook: addBookMutation.isPending,
    removeBook: removeBookMutation.mutate,
    removeBookAsync: removeBookMutation.mutateAsync,
    isRemovingBook: removeBookMutation.isPending,
  }
}

export default useLibrary
