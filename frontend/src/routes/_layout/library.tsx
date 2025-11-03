import { useState } from "react"
import {
  Box,
  Container,
  Grid,
  Heading,
  HStack,
  Text,
  VStack,
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { FiBookOpen, FiPlus } from "react-icons/fi"

import { Button } from "@/components/ui/button"
import {
  DialogBackdrop,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogHeader,
  DialogRoot,
  DialogTitle,
} from "@/components/ui/dialog"
import BookCard from "@/components/Library/BookCard"
import BookSearch from "@/components/Library/BookSearch"
import LoadingSpinner from "@/components/Common/LoadingSpinner"
import EmptyState from "@/components/Common/EmptyState"
import useLibrary from "@/hooks/useLibrary"

export const Route = createFileRoute("/_layout/library")({
  component: LibraryPage,
})

function LibraryPage() {
  const { library, isLoading, addBook, isAddingBook, removeBook, isRemovingBook } =
    useLibrary()
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)

  const books = library?.data || []
  const bookCount = library?.count || 0

  // Create a set of existing google_books_ids for quick lookup
  const existingBookIds = new Set(
    books
      .map((book) => book.google_books_id)
      .filter((id): id is string => id !== null && id !== undefined)
  )

  const handleAddBook = async (googleBooksId: string) => {
    try {
      await addBook(googleBooksId)
      // Don't close modal automatically - let user add multiple books
    } catch (error) {
      // Error is handled by the hook
    }
  }

  return (
    <Container maxW="6xl" py={8}>
      <VStack gap={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <Box>
            <Heading size="xl" mb={2}>
              My Library
            </Heading>
            <Text color="gray.fg">
              {bookCount === 0
                ? "Add books you love to get personalized recommendations"
                : `${bookCount} ${bookCount === 1 ? "book" : "books"} in your profile`}
            </Text>
          </Box>
          <Button
            colorScheme="blue"
            onClick={() => setIsAddModalOpen(true)}
            size="lg"
          >
            <FiPlus />
            Add Books
          </Button>
        </HStack>

        {/* Books Grid */}
        {isLoading ? (
          <LoadingSpinner message="Loading your library..." />
        ) : bookCount === 0 ? (
          <EmptyState
            icon={<FiBookOpen />}
            title="No books in your library yet"
            description="Start by adding some books you love. We'll use these to recommend books when you scan bookshelves."
            action={
              <Button
                colorScheme="blue"
                onClick={() => setIsAddModalOpen(true)}
              >
                <FiPlus />
                Add Your First Book
              </Button>
            }
          />
        ) : (
          <Grid
            templateColumns={{ base: "1fr", md: "1fr 1fr", lg: "1fr 1fr 1fr" }}
            gap={4}
          >
            {books.map((book) => (
              <BookCard
                key={book.id}
                book={book}
                onRemove={removeBook}
                isRemoving={isRemovingBook}
              />
            ))}
          </Grid>
        )}
      </VStack>

      {/* Add Book Modal */}
      <DialogRoot
        open={isAddModalOpen}
        onOpenChange={(e) => setIsAddModalOpen(e.open)}
        size="xl"
      >
        <DialogBackdrop />
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Books to Your Library</DialogTitle>
            <DialogCloseTrigger />
          </DialogHeader>
          <DialogBody>
            <BookSearch
              onAddBook={handleAddBook}
              isAdding={isAddingBook}
              existingBookIds={existingBookIds}
            />
          </DialogBody>
        </DialogContent>
      </DialogRoot>
    </Container>
  )
}
