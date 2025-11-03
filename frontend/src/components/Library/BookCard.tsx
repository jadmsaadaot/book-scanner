import { Box, HStack, Text, VStack, IconButton } from "@chakra-ui/react"
import { FiTrash2 } from "react-icons/fi"

import type { BookPublic } from "@/client"
import BookCover from "@/components/Books/BookCover"

interface BookCardProps {
  book: BookPublic
  onRemove: (bookId: string) => void
  isRemoving?: boolean
}

/**
 * BookCard component for displaying a book in the library
 * Shows cover, title, author, and remove button
 */
const BookCard = ({ book, onRemove, isRemoving }: BookCardProps) => {
  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      p={4}
      bg="bg.panel"
      _hover={{ shadow: "md" }}
      transition="all 0.2s"
    >
      <HStack gap={4} align="start">
        <BookCover
          thumbnailUrl={book.thumbnail_url}
          title={book.title}
          size="sm"
        />
        <VStack flex={1} align="start" gap={1}>
          <Text fontWeight="semibold" fontSize="md" lineClamp={2}>
            {book.title}
          </Text>
          {book.author && (
            <Text fontSize="sm" color="gray.fg" lineClamp={1}>
              by {book.author}
            </Text>
          )}
          {book.published_date && (
            <Text fontSize="xs" color="gray.fg">
              {book.published_date}
            </Text>
          )}
          {book.categories && (
            <Text fontSize="xs" color="gray.fg" lineClamp={1}>
              {JSON.parse(book.categories).join(", ")}
            </Text>
          )}
        </VStack>
        <IconButton
          aria-label="Remove book"
          size="sm"
          variant="ghost"
          colorScheme="red"
          onClick={() => onRemove(book.id)}
          loading={isRemoving}
        >
          <FiTrash2 />
        </IconButton>
      </HStack>
    </Box>
  )
}

export default BookCard
