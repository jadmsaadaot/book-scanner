import { Box, Text, VStack } from "@chakra-ui/react"
import type { ReactNode } from "react"

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: ReactNode
}

/**
 * EmptyState component for displaying empty data states
 * Used when library is empty, no scan results, etc.
 */
const EmptyState = ({ icon, title, description, action }: EmptyStateProps) => {
  return (
    <Box py={12} textAlign="center">
      <VStack gap={4}>
        {icon && <Box fontSize="4xl">{icon}</Box>}
        <Text fontSize="lg" fontWeight="semibold">
          {title}
        </Text>
        {description && (
          <Text fontSize="sm" color="gray.fg" maxW="md">
            {description}
          </Text>
        )}
        {action && <Box mt={4}>{action}</Box>}
      </VStack>
    </Box>
  )
}

export default EmptyState
