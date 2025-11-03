import { Box, Heading, Text, VStack } from "@chakra-ui/react"

import type { ScanResult } from "@/client"
import TopPicks from "./TopPicks"
import DetectedBooksList from "./DetectedBooksList"

interface ScanResultsProps {
  result: ScanResult
}

/**
 * ScanResults component to display scan output
 * Shows top recommendations and all detected books
 */
const ScanResults = ({ result }: ScanResultsProps) => {
  const { recommendations, detected_books } = result

  return (
    <VStack gap={8} align="stretch" w="full">
      {/* Top Picks Section */}
      {recommendations.length > 0 && (
        <Box>
          <Heading size="lg" mb={4}>
            ✨ Top Picks for You
          </Heading>
          <Text fontSize="sm" color="gray.fg" mb={4}>
            Based on your library, these books match your taste
          </Text>
          <TopPicks books={recommendations} />
        </Box>
      )}

      {/* All Detected Books */}
      {detected_books.length > 0 && (
        <Box>
          <Heading size="md" mb={4}>
            📚 All Detected Books ({detected_books.length})
          </Heading>
          <DetectedBooksList books={detected_books} />
        </Box>
      )}

      {/* No Results */}
      {detected_books.length === 0 && (
        <Box textAlign="center" py={8}>
          <Text fontSize="lg" color="gray.fg">
            No books detected in this image. Try a clearer photo with better
            lighting.
          </Text>
        </Box>
      )}
    </VStack>
  )
}

export default ScanResults
