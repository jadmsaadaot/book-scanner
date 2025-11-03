import { Box, Spinner, Text, VStack } from "@chakra-ui/react"

interface LoadingSpinnerProps {
  message?: string
  size?: "sm" | "md" | "lg" | "xl"
}

/**
 * LoadingSpinner component with optional message
 * Used for processing states (scanning, uploading, etc.)
 */
const LoadingSpinner = ({
  message = "Loading...",
  size = "lg",
}: LoadingSpinnerProps) => {
  return (
    <VStack gap={4} py={8}>
      <Spinner size={size} color="blue.500" />
      {message && (
        <Text fontSize="md" color="gray.fg">
          {message}
        </Text>
      )}
    </VStack>
  )
}

export default LoadingSpinner
