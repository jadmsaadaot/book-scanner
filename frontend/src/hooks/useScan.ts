import { useMutation } from "@tanstack/react-query"

import {
  type ApiError,
  type ScanResult,
  BooksService,
} from "@/client"
import { handleError } from "@/utils"

/**
 * Custom hook for scanning bookshelf images
 * Handles image upload and returns detected books and recommendations
 */
const useScan = () => {
  const scanMutation = useMutation({
    mutationFn: (file: File | Blob) =>
      BooksService.scanBookshelf({ file }),
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  return {
    scan: scanMutation.mutate,
    scanAsync: scanMutation.mutateAsync,
    isScanning: scanMutation.isPending,
    scanResult: scanMutation.data as ScanResult | undefined,
    scanError: scanMutation.error,
    reset: scanMutation.reset,
  }
}

export default useScan
