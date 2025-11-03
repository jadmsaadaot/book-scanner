import {
  Box,
  Container,
  Grid,
  Heading,
  HStack,
  Progress,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useNavigate, createFileRoute } from "@tanstack/react-router"
import { FiCheck } from "react-icons/fi"

import { Button } from "@/components/ui/button"
import BookSearch from "@/components/Library/BookSearch"
import BookCard from "@/components/Library/BookCard"
import LoadingSpinner from "@/components/Common/LoadingSpinner"
import useLibrary from "@/hooks/useLibrary"

export const Route = createFileRoute("/onboarding")({
  component: OnboardingPage,
})

const MIN_BOOKS = 5
const RECOMMENDED_BOOKS = 10

function OnboardingPage() {
  const navigate = useNavigate()
  const { library, isLoading, addBook, isAddingBook, removeBook, isRemovingBook } =
    useLibrary()

  const books = library?.data || []
  const bookCount = library?.count || 0
  const canContinue = bookCount >= MIN_BOOKS

  // Create a set of existing google_books_ids
  const existingBookIds = new Set(
    books
      .map((book) => book.google_books_id)
      .filter((id): id is string => id !== null && id !== undefined)
  )

  const handleAddBook = async (googleBooksId: string) => {
    try {
      await addBook(googleBooksId)
    } catch (error) {
      // Error is handled by the hook
    }
  }

  const handleContinue = () => {
    navigate({ to: "/" })
  }

  const handleSkip = () => {
    navigate({ to: "/" })
  }

  // Progress percentage
  const progress = Math.min((bookCount / RECOMMENDED_BOOKS) * 100, 100)

  return (
    <Container maxW="5xl" py={8}>
      <VStack gap={8} align="stretch">
        {/* Header */}
        <Box textAlign="center">
          <Heading size="2xl" mb={4}>
            Welcome to Book Scanner! 📚
          </Heading>
          <Text fontSize="lg" color="gray.fg" mb={2}>
            Let's build your reading profile
          </Text>
          <Text fontSize="md" color="gray.fg" maxW="2xl" mx="auto">
            Add books you love so we can recommend similar ones when you scan
            bookshelves. The more books you add, the better your recommendations
            will be.
          </Text>
        </Box>

        {/* Progress */}
        <Box>
          <HStack justify="space-between" mb={2}>
            <Text fontSize="sm" fontWeight="semibold">
              {bookCount} of {RECOMMENDED_BOOKS} books added
            </Text>
            <Text fontSize="sm" color="gray.fg">
              {canContinue ? (
                <span style={{ color: "green" }}>
                  <FiCheck style={{ display: "inline", marginRight: 4 }} />
                  Ready to continue!
                </span>
              ) : (
                `${MIN_BOOKS - bookCount} more to continue`
              )}
            </Text>
          </HStack>
          <Progress
            value={progress}
            colorScheme={canContinue ? "green" : "blue"}
            size="sm"
          />
        </Box>

        {/* Search */}
        <Box>
          <Heading size="md" mb={4}>
            Search for books you love
          </Heading>
          {isLoading ? (
            <LoadingSpinner message="Loading..." />
          ) : (
            <BookSearch
              onAddBook={handleAddBook}
              isAdding={isAddingBook}
              existingBookIds={existingBookIds}
            />
          )}
        </Box>

        {/* Your Books */}
        {bookCount > 0 && (
          <Box>
            <Heading size="md" mb={4}>
              Your profile books ({bookCount})
            </Heading>
            <Grid
              templateColumns={{ base: "1fr", md: "1fr 1fr" }}
              gap={3}
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
          </Box>
        )}

        {/* Actions */}
        <HStack justify="space-between" pt={4}>
          <Button variant="ghost" onClick={handleSkip}>
            Skip for now
          </Button>
          <Button
            size="lg"
            colorScheme="blue"
            onClick={handleContinue}
            disabled={!canContinue}
          >
            Continue to Dashboard
          </Button>
        </HStack>
      </VStack>
    </Container>
  )
}
