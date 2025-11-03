import { useState } from "react"
import {
  Box,
  Container,
  Heading,
  Image,
  Text,
  VStack,
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { FiRefreshCw } from "react-icons/fi"

import { Button } from "@/components/ui/button"
import ImageUpload from "@/components/Scanner/ImageUpload"
import ScanResults from "@/components/Scanner/ScanResults"
import LoadingSpinner from "@/components/Common/LoadingSpinner"
import useScan from "@/hooks/useScan"

export const Route = createFileRoute("/_layout/scan")({
  component: ScanPage,
})

function ScanPage() {
  const { scan, isScanning, scanResult, scanError, reset } = useScan()
  const [selectedImage, setSelectedImage] = useState<string | null>(null)

  const handleImageSelect = (file: File) => {
    // Create preview URL
    const previewUrl = URL.createObjectURL(file)
    setSelectedImage(previewUrl)

    // Start scan
    scan(file)
  }

  const handleReset = () => {
    reset()
    setSelectedImage(null)
  }

  return (
    <Container maxW="4xl" py={8}>
      <VStack gap={6} align="stretch">
        {/* Header */}
        <Box textAlign="center">
          <Heading size="xl" mb={2}>
            Scan a Bookshelf 📸
          </Heading>
          <Text color="gray.fg">
            Take a photo of any bookshelf and discover which books match your
            taste
          </Text>
        </Box>

        {/* Upload State */}
        {!selectedImage && !scanResult && (
          <Box py={4}>
            <ImageUpload
              onImageSelect={handleImageSelect}
              disabled={isScanning}
            />
          </Box>
        )}

        {/* Processing State */}
        {isScanning && selectedImage && (
          <VStack gap={4}>
            <Box maxW="md" w="full">
              <Image
                src={selectedImage}
                alt="Uploaded bookshelf"
                borderRadius="lg"
                maxH="400px"
                objectFit="contain"
              />
            </Box>
            <LoadingSpinner message="Scanning bookshelf... This may take 5-10 seconds" />
            <Text fontSize="sm" color="gray.fg" textAlign="center" maxW="md">
              We're detecting book titles using OCR, searching our database, and
              matching them to your taste profile
            </Text>
          </VStack>
        )}

        {/* Results State */}
        {scanResult && !isScanning && (
          <VStack gap={6} align="stretch">
            {/* Scanned Image Preview */}
            <Box>
              <Text fontSize="sm" fontWeight="semibold" mb={2}>
                Scanned Image:
              </Text>
              <Image
                src={selectedImage || ""}
                alt="Scanned bookshelf"
                borderRadius="lg"
                maxH="300px"
                objectFit="contain"
              />
            </Box>

            {/* Results */}
            <ScanResults result={scanResult} />

            {/* Scan Another Button */}
            <Button
              size="lg"
              variant="outline"
              onClick={handleReset}
              alignSelf="center"
            >
              <FiRefreshCw />
              Scan Another Shelf
            </Button>
          </VStack>
        )}

        {/* Error State */}
        {scanError && !isScanning && (
          <Box
            bg="red.50"
            borderWidth="1px"
            borderColor="red.200"
            borderRadius="lg"
            p={6}
            textAlign="center"
          >
            <Text fontSize="lg" fontWeight="semibold" color="red.600" mb={2}>
              Scan Failed
            </Text>
            <Text fontSize="sm" color="red.600" mb={4}>
              {scanError.message || "Something went wrong while scanning"}
            </Text>
            <Button onClick={handleReset}>
              <FiRefreshCw />
              Try Again
            </Button>
          </Box>
        )}
      </VStack>
    </Container>
  )
}
