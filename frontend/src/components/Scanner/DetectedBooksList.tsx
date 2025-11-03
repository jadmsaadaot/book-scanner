import { useState } from "react"
import { Box, Grid, HStack, Text, VStack } from "@chakra-ui/react"
import { FiChevronDown, FiChevronUp } from "react-icons/fi"

import type { DetectedBook } from "@/client"
import { Button } from "@/components/ui/button"
import BookCover from "@/components/Books/BookCover"
import MatchBadge from "@/components/Books/MatchBadge"

interface DetectedBooksListProps {
  books: DetectedBook[]
}

/**
 * DetectedBooksList component to display all books found in scan
 * Collapsible list with match scores
 */
const DetectedBooksList = ({ books }: DetectedBooksListProps) => {
  const [isExpanded, setIsExpanded] = useState(false)

  // Show first 6 books by default
  const visibleBooks = isExpanded ? books : books.slice(0, 6)
  const hasMore = books.length > 6

  return (
    <VStack gap={4} align="stretch">
      <Grid
        templateColumns={{ base: "1fr", md: "1fr 1fr" }}
        gap={3}
      >
        {visibleBooks.map((book, index) => (
          <Box
            key={`${book.google_books_id || book.title}-${index}`}
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
                <HStack gap={2} mt={1}>
                  <MatchBadge score={book.match_score} size="sm" />
                  {book.in_library && (
                    <Text fontSize="xs" color="orange.600" fontWeight="semibold">
                      In library
                    </Text>
                  )}
                </HStack>
                {book.confidence < 0.7 && (
                  <Text fontSize="xs" color="orange.500">
                    Low confidence detection
                  </Text>
                )}
              </VStack>
            </HStack>
          </Box>
        ))}
      </Grid>

      {/* Show More/Less Button */}
      {hasMore && (
        <Button
          variant="ghost"
          onClick={() => setIsExpanded(!isExpanded)}
          alignSelf="center"
        >
          {isExpanded ? (
            <>
              <FiChevronUp /> Show Less
            </>
          ) : (
            <>
              <FiChevronDown /> Show {books.length - 6} More Books
            </>
          )}
        </Button>
      )}
    </VStack>
  )
}

export default DetectedBooksList
