import { useRef, useState } from "react"
import { Box, Input, Text, VStack } from "@chakra-ui/react"
import { FiCamera, FiUpload } from "react-icons/fi"

import { Button } from "@/components/ui/button"

interface ImageUploadProps {
  onImageSelect: (file: File) => void
  disabled?: boolean
}

/**
 * ImageUpload component for selecting or capturing images
 * Supports file upload, drag-and-drop, and camera capture
 */
const ImageUpload = ({ onImageSelect, disabled }: ImageUploadProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.type.startsWith("image/")) {
      onImageSelect(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const file = e.dataTransfer.files?.[0]
    if (file && file.type.startsWith("image/")) {
      onImageSelect(file)
    }
  }

  return (
    <VStack gap={4} w="full">
      {/* Drag and Drop Area */}
      <Box
        w="full"
        p={12}
        borderWidth={2}
        borderStyle="dashed"
        borderRadius="lg"
        borderColor={isDragging ? "blue.500" : "gray.300"}
        bg={isDragging ? "blue.50" : "bg.subtle"}
        textAlign="center"
        cursor="pointer"
        transition="all 0.2s"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        opacity={disabled ? 0.5 : 1}
        pointerEvents={disabled ? "none" : "auto"}
      >
        <VStack gap={3}>
          <FiUpload size={48} color="gray" />
          <Text fontSize="lg" fontWeight="semibold">
            Drag and drop an image here
          </Text>
          <Text fontSize="sm" color="gray.fg">
            or click to browse your files
          </Text>
          <Text fontSize="xs" color="gray.fg">
            Supports: JPG, PNG, WEBP (max 10MB)
          </Text>
        </VStack>
      </Box>

      {/* Action Buttons */}
      <VStack gap={2} w="full">
        <Text fontSize="sm" color="gray.fg">
          or
        </Text>
        <Button
          size="lg"
          colorScheme="blue"
          onClick={() => cameraInputRef.current?.click()}
          disabled={disabled}
          w="full"
          maxW="md"
        >
          <FiCamera />
          Take Photo with Camera
        </Button>
      </VStack>

      {/* Hidden File Inputs */}
      <Input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        display="none"
      />
      <Input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileChange}
        display="none"
      />
    </VStack>
  )
}

export default ImageUpload
