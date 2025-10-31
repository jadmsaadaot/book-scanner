# Frontend Development Guide - Book Scanner

## Overview

The backend is complete! Now you need to build the frontend UI components to interact with the book scanning API.

## What's Already Set Up

✅ React + TypeScript + Vite
✅ Chakra UI for components
✅ Auto-generated API client (when you run `npm run generate-client`)
✅ User authentication system
✅ Routing infrastructure

## What You Need to Build

### 1. Book Scanner Page

**File**: `src/components/BookScanner/BookScanner.tsx`

**Features to implement**:
- [ ] File upload component (drag & drop or click to upload)
- [ ] Camera capture button (use device camera)
- [ ] Image preview before scanning
- [ ] Loading state during OCR processing
- [ ] Display detected books with:
  - Book cover thumbnails
  - Title and author
  - Confidence score (how accurate OCR was)
  - Match score (how well it fits your library)
  - "Add to Library" button
- [ ] Display recommendations separately
- [ ] Error handling (bad image, no books detected, etc.)

**Example API Call**:
```typescript
const handleScanImage = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch('/api/v1/books/scan', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    },
    body: formData
  })

  const result = await response.json()
  // result.detected_books - all books found
  // result.recommendations - books not in your library
}
```

### 2. Library Page

**File**: `src/components/Library/Library.tsx`

**Features to implement**:
- [ ] Grid view of book covers
- [ ] List view option
- [ ] Search/filter books by:
  - Title
  - Author
  - Genre/category
- [ ] Sort by:
  - Date added
  - Title (A-Z)
  - Author
- [ ] Book details modal/card
- [ ] "Remove from library" button
- [ ] Empty state (when no books in library)
- [ ] Pagination (if library has many books)

**Example API Call**:
```typescript
const fetchLibrary = async () => {
  const response = await fetch('/api/v1/books/library?skip=0&limit=50', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  })

  const data = await response.json()
  // data.data - array of books
  // data.count - total count
}
```

### 3. Book Card Component

**File**: `src/components/Book/BookCard.tsx`

**Reusable component to display a single book**:
- [ ] Book cover image (thumbnail)
- [ ] Title and author
- [ ] Rating stars
- [ ] Add/Remove from library button
- [ ] "View Details" button
- [ ] Confidence badge (for scanned books)
- [ ] Match score indicator (for recommendations)

### 4. Add Navigation Links

**File**: `src/components/Common/Sidebar.tsx` (or wherever your nav is)

Add links to:
- [ ] `/scan` - Book Scanner page
- [ ] `/library` - My Library page

## Suggested Component Structure

```
src/
├── components/
│   ├── BookScanner/
│   │   ├── BookScanner.tsx           # Main scanner page
│   │   ├── ImageUpload.tsx           # Upload/camera component
│   │   ├── ScanResults.tsx           # Display results
│   │   └── BookList.tsx              # List of detected books
│   ├── Library/
│   │   ├── Library.tsx               # Main library page
│   │   ├── LibraryGrid.tsx           # Grid view
│   │   ├── LibraryList.tsx           # List view
│   │   └── LibraryFilters.tsx        # Search/filter UI
│   ├── Book/
│   │   ├── BookCard.tsx              # Reusable book card
│   │   ├── BookDetails.tsx           # Book details modal
│   │   └── BookCover.tsx             # Book cover image
│   └── Common/
│       ├── LoadingSpinner.tsx
│       └── ErrorMessage.tsx
├── hooks/
│   ├── useBookScanner.ts             # Scanner logic
│   ├── useLibrary.ts                 # Library CRUD operations
│   └── useBooks.ts                   # Book-related API calls
└── types/
    └── book.ts                       # TypeScript types (auto-generated)
```

## Example Code Snippets

### Image Upload Component

```typescript
import { useRef, useState } from 'react'
import { Box, Button, Input, VStack } from '@chakra-ui/react'

export function ImageUpload({ onImageSelect }: { onImageSelect: (file: File) => void }) {
  const [preview, setPreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      onImageSelect(file)

      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  return (
    <VStack spacing={4}>
      <Input
        type="file"
        accept="image/*"
        ref={fileInputRef}
        onChange={handleFileChange}
        display="none"
      />
      <Button onClick={() => fileInputRef.current?.click()}>
        Choose Image
      </Button>

      {/* Camera capture for mobile */}
      <Input
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileChange}
        display="none"
        id="camera-input"
      />
      <Button as="label" htmlFor="camera-input">
        Take Photo
      </Button>

      {preview && (
        <Box>
          <img src={preview} alt="Preview" style={{ maxWidth: '100%', maxHeight: '300px' }} />
        </Box>
      )}
    </VStack>
  )
}
```

### Book Card Component

```typescript
import { Box, Image, Text, Button, Badge, HStack, VStack } from '@chakra-ui/react'

interface BookCardProps {
  title: string
  author: string | null
  thumbnailUrl: string | null
  matchScore?: number
  inLibrary?: boolean
  onAddToLibrary?: () => void
  onRemoveFromLibrary?: () => void
}

export function BookCard({
  title,
  author,
  thumbnailUrl,
  matchScore,
  inLibrary,
  onAddToLibrary,
  onRemoveFromLibrary
}: BookCardProps) {
  return (
    <Box borderWidth="1px" borderRadius="lg" overflow="hidden" p={4}>
      <VStack align="start" spacing={3}>
        {thumbnailUrl && (
          <Image
            src={thumbnailUrl}
            alt={title}
            boxSize="150px"
            objectFit="cover"
          />
        )}

        <Text fontWeight="bold" fontSize="md">{title}</Text>
        {author && <Text fontSize="sm" color="gray.600">{author}</Text>}

        {matchScore !== undefined && (
          <HStack>
            <Badge colorScheme={matchScore > 0.7 ? "green" : "yellow"}>
              {Math.round(matchScore * 100)}% Match
            </Badge>
          </HStack>
        )}

        {inLibrary ? (
          <Button size="sm" colorScheme="red" onClick={onRemoveFromLibrary}>
            Remove from Library
          </Button>
        ) : (
          <Button size="sm" colorScheme="blue" onClick={onAddToLibrary}>
            Add to Library
          </Button>
        )}
      </VStack>
    </Box>
  )
}
```

### Custom Hook for Book Scanning

```typescript
import { useState } from 'react'

interface ScanResult {
  detected_books: DetectedBook[]
  recommendations: DetectedBook[]
}

export function useBookScanner() {
  const [isScanning, setIsScanning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<ScanResult | null>(null)

  const scanImage = async (file: File) => {
    setIsScanning(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/v1/books/scan', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: formData
      })

      if (!response.ok) {
        throw new Error('Scan failed')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsScanning(false)
    }
  }

  return { scanImage, isScanning, error, result }
}
```

## API Response Types

After running `npm run generate-client`, you'll get these types automatically. Here's what to expect:

```typescript
interface DetectedBook {
  title: string
  author: string | null
  isbn: string | null
  thumbnail_url: string | null
  google_books_id: string | null
  confidence: number  // 0.0 to 1.0
  match_score: number // 0.0 to 1.0
  in_library: boolean
}

interface ScanResult {
  detected_books: DetectedBook[]
  recommendations: DetectedBook[]
}

interface BookPublic {
  id: string
  title: string
  author: string | null
  isbn: string | null
  publisher: string | null
  published_date: string | null
  description: string | null
  page_count: number | null
  categories: string | null  // JSON string
  thumbnail_url: string | null
  google_books_id: string | null
  average_rating: number | null
  ratings_count: number | null
}

interface BooksPublic {
  data: BookPublic[]
  count: number
}
```

## Development Workflow

1. **Start backend** (in one terminal):
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Generate API client** (run once, then whenever API changes):
   ```bash
   cd frontend
   npm run generate-client
   ```

3. **Start frontend** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```

4. **Build components** following the structure above

5. **Test with real images** of book spines

## UI/UX Tips

### Good User Experience
- Show loading spinner during OCR (takes 2-5 seconds)
- Display confidence scores so users know how accurate the detection was
- Allow manual title correction if OCR misreads
- Show recommendations prominently
- Use book cover thumbnails (more visual than text lists)
- Add empty states ("No books in library yet - scan some books!")
- Mobile-friendly camera capture

### Styling Recommendations
- Use Chakra UI's responsive props
- Card-based layout for books
- Grid for library (2-3 columns on mobile, 4-6 on desktop)
- Color-coded badges:
  - Green: High confidence/match (>70%)
  - Yellow: Medium (40-70%)
  - Red: Low (<40%)

## Testing Your Frontend

### Test Cases
1. Upload image with 1 book → Should detect and show recommendation
2. Upload image with multiple books → Should detect all visible titles
3. Add book to library → Should show in library page
4. Scan same book again → Should show "in_library: true", not recommend
5. Remove book from library → Should disappear from library page
6. Upload bad image (not books) → Should handle gracefully
7. No internet → Should show error message

### Sample Test Images
Take photos of your own bookshelf, or find sample images online of:
- Book spines (vertical)
- Books stacked (horizontal)
- Close-up of single book cover
- Bookshelf with many books

## Ready to Build! 🚀

The backend is fully functional. Now build the UI to make it user-friendly!

Start with the ImageUpload component, then the BookScanner page, then the Library page.

Good luck! 📚
