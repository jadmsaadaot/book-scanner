import { useState } from "react"
import {
  Box,
  HStack,
  Input,
  Text,
  VStack,
  IconButton,
  Grid,
} from "@chakra-ui/react"
import { FiSearch, FiPlus, FiX } from "react-icons/fi"

import type { BookPublic } from "@/client"
import { Button } from "@/components/ui/button"
import BookCover from "@/components/Books/BookCover"
import LoadingSpinner from "@/components/Common/LoadingSpinner"
import useGoogleBooks from "@/hooks/useGoogleBooks"

interface BookSearchProps {
  onAddBook: (googleBooksId: string) => void
  isAdding: boolean
  existingBookIds?: Set<string>
}

/**
 * BookSearch component for searching and adding books to library
 * Uses Google Books API to search for books
 */
const BookSearch = ({
  onAddBook,
  isAdding,
  existingBookIds = new Set(),
}: BookSearchProps) => {
  const [query, setQuery] = useState("")
  const { searchBooks, isSearching, searchResults, clearResults } =
    useGoogleBooks()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      searchBooks(query.trim())
    }
  }

  const handleClear = () => {
    setQuery("")
    clearResults()
  }

  return (
    <VStack gap={4} align="stretch">
      {/* Search Input */}
      <form onSubmit={handleSearch}>
        <HStack gap={2}>
          <Input
            placeholder="Search for books by title or author..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            size="lg"
          />
          <Button type="submit" size="lg" disabled={!query.trim() || isSearching}>
            <FiSearch />
            Search
          </Button>
          {(query || searchResults.length > 0) && (
            <IconButton aria-label="Clear search" size="lg" onClick={handleClear}>
              <FiX />
            </IconButton>
          )}
        </HStack>
      </form>

      {/* Search Results */}
      {isSearching && <LoadingSpinner message="Searching for books..." />}

      {!isSearching && searchResults.length > 0 && (
        <VStack gap={3} align="stretch">
          <Text fontSize="sm" color="gray.fg">
            Found {searchResults.length} results
          </Text>
          <Grid templateColumns={{ base: "1fr", md: "1fr 1fr" }} gap={3}>
            {searchResults.map((book) => {
              const alreadyInLibrary = book.google_books_id
                ? existingBookIds.has(book.google_books_id)
                : false

              return (
                <Box
                  key={book.google_books_id}
                  borderWidth="1px"
                  borderRadius="md"
                  p={3}
                  bg="bg.panel"
                >
                  <HStack gap={3} align="start">
                    <BookCover
                      thumbnailUrl={book.thumbnail_url}
                      title={book.title}
                      size="sm"
                    />
                    <VStack flex={1} align="start" gap={1}>
                      <Text fontWeight="semibold" fontSize="sm" lineClamp={2}>
                        {book.title}
                      </Text>
                      {book.author && (
                        <Text fontSize="xs" color="gray.fg" lineClamp={1}>
                          {book.author}
                        </Text>
                      )}
                      {book.published_date && (
                        <Text fontSize="xs" color="gray.fg">
                          {book.published_date}
                        </Text>
                      )}
                      <Button
                        size="xs"
                        colorScheme={alreadyInLibrary ? "gray" : "blue"}
                        onClick={() =>
                          book.google_books_id &&
                          onAddBook(book.google_books_id)
                        }
                        disabled={alreadyInLibrary || isAdding}
                        mt={2}
                      >
                        {alreadyInLibrary ? (
                          "Already in Library"
                        ) : (
                          <>
                            <FiPlus /> Add
                          </>
                        )}
                      </Button>
                    </VStack>
                  </HStack>
                </Box>
              )
            })}
          </Grid>
        </VStack>
      )}

      {!isSearching && query && searchResults.length === 0 && (
        <Text textAlign="center" color="gray.fg" py={4}>
          No books found. Try a different search term.
        </Text>
      )}
    </VStack>
  )
}

export default BookSearch
