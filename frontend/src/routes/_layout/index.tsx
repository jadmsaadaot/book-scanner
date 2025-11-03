import { Box, Container, Heading, Text, VStack } from "@chakra-ui/react"
import { Link, createFileRoute } from "@tanstack/react-router"
import { FiCamera, FiBookOpen } from "react-icons/fi"

import { Button } from "@/components/ui/button"
import LoadingSpinner from "@/components/Common/LoadingSpinner"
import useAuth from "@/hooks/useAuth"
import useLibrary from "@/hooks/useLibrary"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {
  const { user: currentUser } = useAuth()
  const { library, isLoading } = useLibrary()

  const bookCount = library?.count || 0
  const hasBooks = bookCount > 0

  return (
    <Container maxW="4xl" py={8}>
      <VStack gap={8} align="stretch">
        {/* Welcome Section */}
        <Box textAlign="center" py={8}>
          <Heading size="2xl" mb={4}>
            Welcome to Book Scanner! 📚
          </Heading>
          <Text fontSize="lg" color="gray.fg" mb={2}>
            Hi, {currentUser?.full_name || currentUser?.email}!
          </Text>
          <Text fontSize="md" color="gray.fg" maxW="2xl" mx="auto">
            Your personal book scout for browsing bookstores. Scan any shelf
            with your phone camera and instantly discover which books match your
            taste.
          </Text>
        </Box>

        {/* Profile Status */}
        {isLoading ? (
          <LoadingSpinner message="Loading your library..." />
        ) : (
          <Box textAlign="center" py={4}>
            {hasBooks ? (
              <VStack gap={2}>
                <Text fontSize="xl" fontWeight="semibold">
                  {bookCount} {bookCount === 1 ? "book" : "books"} in your
                  profile
                </Text>
                <Text fontSize="sm" color="gray.fg">
                  We'll use these to find your next favorite read
                </Text>
              </VStack>
            ) : (
              <VStack gap={2}>
                <Text fontSize="xl" fontWeight="semibold" color="orange.500">
                  No books in your profile yet
                </Text>
                <Text fontSize="sm" color="gray.fg" maxW="md">
                  Add some books you love to get personalized recommendations
                  when scanning
                </Text>
              </VStack>
            )}
          </Box>
        )}

        {/* Action Buttons */}
        <VStack gap={4}>
          <Link to="/scan">
            <Button
              size="xl"
              colorScheme="blue"
              width="full"
              maxW="md"
              disabled={!hasBooks}
            >
              <FiCamera />
              Scan a Bookshelf
            </Button>
          </Link>
          {!hasBooks && (
            <Text fontSize="xs" color="gray.fg">
              Add books to your library first to enable scanning
            </Text>
          )}

          <Link to="/library">
            <Button size="lg" variant="outline" width="full" maxW="md">
              <FiBookOpen />
              {hasBooks ? "Manage My Library" : "Add Books to Library"}
            </Button>
          </Link>
        </VStack>

        {/* How It Works */}
        <Box bg="bg.subtle" p={6} borderRadius="lg" mt={8}>
          <Heading size="md" mb={4}>
            How it works:
          </Heading>
          <VStack align="stretch" gap={3}>
            <Text fontSize="sm">
              1️⃣ <strong>Build your profile</strong> - Add books you love to
              teach us your taste
            </Text>
            <Text fontSize="sm">
              2️⃣ <strong>Visit a bookstore</strong> - Browse any bookstore,
              library sale, or thrift shop
            </Text>
            <Text fontSize="sm">
              3️⃣ <strong>Scan shelves</strong> - Take a photo of any bookshelf
              with your phone
            </Text>
            <Text fontSize="sm">
              4️⃣ <strong>Discover gems</strong> - Get instant personalized
              recommendations with match scores
            </Text>
          </VStack>
        </Box>
      </VStack>
    </Container>
  )
}
