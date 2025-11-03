import { Box, Image } from "@chakra-ui/react"

interface BookCoverProps {
  thumbnailUrl?: string | null
  title: string
  size?: "sm" | "md" | "lg"
}

/**
 * BookCover component with fallback for missing images
 * Shows book cover image or a placeholder with book title initial
 */
const BookCover = ({ thumbnailUrl, title, size = "md" }: BookCoverProps) => {
  const sizes = {
    sm: { width: "60px", height: "90px", fontSize: "2xl" },
    md: { width: "100px", height: "150px", fontSize: "3xl" },
    lg: { width: "140px", height: "210px", fontSize: "4xl" },
  }

  const { width, height, fontSize } = sizes[size]

  if (thumbnailUrl) {
    return (
      <Image
        src={thumbnailUrl}
        alt={`Cover of ${title}`}
        width={width}
        height={height}
        objectFit="cover"
        borderRadius="md"
        fallback={<BookCoverFallback title={title} size={size} />}
      />
    )
  }

  return <BookCoverFallback title={title} size={size} />
}

/**
 * Fallback placeholder when no cover image is available
 */
const BookCoverFallback = ({
  title,
  size,
}: {
  title: string
  size: "sm" | "md" | "lg"
}) => {
  const sizes = {
    sm: { width: "60px", height: "90px", fontSize: "2xl" },
    md: { width: "100px", height: "150px", fontSize: "3xl" },
    lg: { width: "140px", height: "210px", fontSize: "4xl" },
  }

  const { width, height, fontSize } = sizes[size]

  // Get first letter of title for placeholder
  const initial = title.charAt(0).toUpperCase()

  return (
    <Box
      width={width}
      height={height}
      borderRadius="md"
      bg="gray.subtle"
      display="flex"
      alignItems="center"
      justifyContent="center"
      fontSize={fontSize}
      fontWeight="bold"
      color="gray.fg"
    >
      {initial}
    </Box>
  )
}

export default BookCover
