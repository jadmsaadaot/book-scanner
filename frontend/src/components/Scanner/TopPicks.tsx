import { Box, HStack, Text, VStack } from "@chakra-ui/react"
import { FiStar } from "react-icons/fi"

import type { DetectedBook } from "@/client"
import BookCover from "@/components/Books/BookCover"
import MatchBadge from "@/components/Books/MatchBadge"

interface TopPicksProps {
  books: DetectedBook[]
}

/**
 * TopPicks component to display highly-recommended books
 * Shows match scores and explanations prominently
 */
const TopPicks = ({ books }: TopPicksProps) => {
  // Take top 5 recommendations
  const topBooks = books.slice(0, 5)

  return (
    <VStack gap={4} align="stretch">
      {topBooks.map((book, index) => (
        <Box
          key={`${book.google_books_id || book.title}-${index}`}
          borderWidth="2px"
          borderColor="blue.500"
          borderRadius="lg"
          p={4}
          bg="blue.50"
          position="relative"
        >
          {/* Rank Badge */}
          <Box
            position="absolute"
            top={-3}
            left={4}
            bg="blue.500"
            color="white"
            px={3}
            py={1}
            borderRadius="full"
            fontSize="xs"
            fontWeight="bold"
          >
            <FiStar style={{ display: "inline", marginRight: 4 }} />
            #{index + 1} Pick
          </Box>

          <HStack gap={4} align="start" mt={2}>
            <BookCover
              thumbnailUrl={book.thumbnail_url}
              title={book.title}
              size="md"
            />
            <VStack flex={1} align="start" gap={2}>
              <Text fontWeight="bold" fontSize="lg">
                {book.title}
              </Text>
              {book.author && (
                <Text fontSize="md" color="gray.600">
                  by {book.author}
                </Text>
              )}
              <MatchBadge score={book.match_score} size="md" />
              {book.recommendation_explanation && (
                <Box
                  bg="white"
                  p={3}
                  borderRadius="md"
                  borderLeftWidth={3}
                  borderLeftColor="blue.500"
                  w="full"
                >
                  <Text fontSize="sm" fontStyle="italic">
                    "{book.recommendation_explanation}"
                  </Text>
                </Box>
              )}
              {book.in_library && (
                <Text fontSize="xs" color="orange.600" fontWeight="semibold">
                  ✓ Already in your library
                </Text>
              )}
            </VStack>
          </HStack>
        </Box>
      ))}
    </VStack>
  )
}

export default TopPicks
