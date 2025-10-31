# Book Scanner App

A full-stack application that uses OCR (Optical Character Recognition) to scan images of book spines/covers, identify books via Google Books API, and provide personalized recommendations based on your reading library.

## Features

### Core Functionality
- **Image Upload & OCR**: Upload photos of books on shelves or tables
- **Text Extraction**: Uses Tesseract OCR to extract book titles from images
- **Book Identification**: Fuzzy matching with Google Books API to handle OCR errors
- **Library Management**: Save books to your personal library
- **Smart Recommendations**: Get book suggestions based on:
  - Author overlap with your library
  - Genre/category matching
  - Book ratings and popularity
  - Your reading preferences

## Architecture

### Backend (FastAPI + Python)
Located in `/backend`

#### Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLModel ORM
- **OCR**: Tesseract OCR (free, open-source)
- **Image Processing**: Pillow (PIL)
- **Fuzzy Matching**: FuzzyWuzzy + python-Levenshtein
- **External API**: Google Books API (free tier)
- **Authentication**: JWT tokens

#### Key Components

1. **Services** (`/backend/app/services/`)
   - `ocr_service.py`: Image preprocessing and text extraction
   - `google_books_service.py`: Google Books API integration with fuzzy search
   - `recommendation_service.py`: Recommendation algorithm

2. **Models** (`/backend/app/models.py`)
   - `Book`: Book metadata storage
   - `UserLibrary`: Junction table linking users to their books
   - `DetectedBook`: Response model for scanned books
   - `ScanResult`: Complete scan response with recommendations

3. **API Routes** (`/backend/app/api/routes/books.py`)
   - `POST /api/v1/books/scan`: Upload and scan book images
   - `POST /api/v1/books/library/add/{google_books_id}`: Add book to library
   - `DELETE /api/v1/books/library/remove/{book_id}`: Remove book from library
   - `GET /api/v1/books/library`: Get user's library

### Frontend (React + TypeScript)
Located in `/frontend`

#### Tech Stack
- **Framework**: React with Vite
- **Language**: TypeScript
- **UI Library**: Chakra UI
- **State Management**: React hooks
- **HTTP Client**: Auto-generated from OpenAPI spec

## How It Works

### 1. Image Upload & OCR Processing
```
User uploads image → OCR preprocesses image → Tesseract extracts text → Parse potential titles
```

**Image Preprocessing Steps:**
- Convert to grayscale
- Enhance contrast (2x)
- Apply sharpening filter
- Resize if too small (minimum 1000px)

### 2. Book Identification
```
OCR titles → Fuzzy search Google Books API → Return best matches (70%+ similarity)
```

**Fuzzy Matching Algorithm:**
- Uses token sort ratio for flexible matching
- Combines title similarity (70%) + author similarity (30%)
- Handles OCR errors and typos

### 3. Recommendation Engine
```
Detected books → Compare with user library → Calculate match scores → Rank recommendations
```

**Scoring Algorithm:**
- **Author Match (40%)**: Books by authors you've read
- **Category Match (30%)**: Books in genres you like
- **Rating (20%)**: Higher-rated books score better
- **Popularity (10%)**: Based on number of ratings

### 4. Library Management
- Books stored in PostgreSQL
- Many-to-many relationship (books can be in multiple libraries)
- Track when books were added
- Optional notes per book

## Database Schema

```sql
-- Core book data
Book
  - id (UUID, primary key)
  - title, author, isbn
  - publisher, published_date
  - description, page_count
  - categories (JSON string)
  - thumbnail_url
  - google_books_id (indexed)
  - average_rating, ratings_count

-- User's personal library (junction table)
UserLibrary
  - id (UUID, primary key)
  - user_id (FK to User)
  - book_id (FK to Book)
  - added_date
  - notes (optional)
```

## Setup & Installation

### Prerequisites
1. **Tesseract OCR** must be installed on your system:
   ```bash
   # macOS
   brew install tesseract

   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr

   # Windows
   # Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

2. **PostgreSQL** (or use Docker Compose)

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies using uv (recommended) or pip:
   ```bash
   # Using uv (faster)
   uv pip install -e .

   # Or using pip
   pip install -e .
   ```

3. Set up environment variables in `/.env`:
   ```env
   PROJECT_NAME=Book Scanner
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=book_scanner
   FIRST_SUPERUSER=admin@example.com
   FIRST_SUPERUSER_PASSWORD=changethis
   SECRET_KEY=your_secret_key_here
   ```

4. Run database migrations:
   ```bash
   # From backend directory
   alembic upgrade head
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

   API will be available at `http://localhost:8000`
   API docs at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`

### Using Docker Compose (Easiest)

```bash
# From project root
docker-compose up -d
```

This starts:
- Backend API on `http://localhost:8000`
- Frontend on `http://localhost:5173`
- PostgreSQL database
- Adminer (database UI) on `http://localhost:8080`

## API Usage Examples

### 1. Scan Books from Image
```bash
curl -X POST "http://localhost:8000/api/v1/books/scan" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/bookshelf.jpg"
```

**Response:**
```json
{
  "detected_books": [
    {
      "title": "The Great Gatsby",
      "author": "F. Scott Fitzgerald",
      "isbn": "9780743273565",
      "thumbnail_url": "http://...",
      "google_books_id": "abc123",
      "confidence": 0.92,
      "match_score": 0.85,
      "in_library": false
    }
  ],
  "recommendations": [
    {
      "title": "The Great Gatsby",
      ...
      "match_score": 0.85
    }
  ]
}
```

### 2. Add Book to Library
```bash
curl -X POST "http://localhost:8000/api/v1/books/library/add/abc123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Get User Library
```bash
curl "http://localhost:8000/api/v1/books/library?skip=0&limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Free Deployment Options

### Backend: Render.com (Free Tier)
1. Create account at render.com
2. Create new Web Service
3. Connect GitHub repository
4. Configure:
   - Build Command: `cd backend && pip install -e .`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables

### Frontend: Vercel (Free)
1. Create account at vercel.com
2. Import GitHub repository
3. Configure:
   - Root Directory: `frontend`
   - Framework: Vite
   - Add environment variable: `VITE_API_URL=https://your-backend.onrender.com`

### Database: Supabase (Free Tier)
- Free PostgreSQL hosting
- 500MB database
- Unlimited API requests

## Cost Breakdown (Free Tier)

| Service | Free Tier | Cost |
|---------|-----------|------|
| Tesseract OCR | Unlimited (local) | $0 |
| Google Books API | 1,000 requests/day | $0 |
| Render (backend) | 750 hours/month | $0 |
| Vercel (frontend) | Unlimited | $0 |
| Supabase (database) | 500MB | $0 |

**Total Monthly Cost: $0** (for personal use)

## Limitations & Improvements

### Current Limitations
1. **OCR Accuracy**: Depends on image quality, lighting, and text clarity
2. **Rate Limits**: Google Books API limited to 1,000 requests/day
3. **Cold Starts**: Free tier services spin down after 15 minutes of inactivity
4. **No Batch Processing**: One image at a time

### Potential Improvements
1. **Better OCR**: Upgrade to Google Cloud Vision API for higher accuracy
2. **Multiple Images**: Support uploading multiple photos in one scan
3. **Manual Correction**: Allow users to correct OCR misreads
4. **Reading Lists**: Create custom reading lists and wish lists
5. **Social Features**: Share libraries with friends, see what others are reading
6. **Barcode Scanning**: Add ISBN barcode scanning for faster input
7. **Mobile App**: Native iOS/Android apps with better camera integration
8. **Book Details**: Add synopsis, reviews, links to purchase
9. **Reading Progress**: Track reading progress and notes
10. **Export**: Export library to CSV, Goodreads, etc.

## Troubleshooting

### "Tesseract not found" Error
- Make sure Tesseract is installed and in your PATH
- On macOS: `brew install tesseract`
- Test: `tesseract --version`

### Poor OCR Results
- Ensure good image quality (well-lit, in focus)
- Book spines should be clearly visible
- Try preprocessing the image (crop, enhance contrast)

### Google Books API Returns No Results
- Check internet connection
- Verify the OCR extracted text is readable
- Try manual search with detected title

### Database Connection Errors
- Ensure PostgreSQL is running
- Check `.env` file has correct database credentials
- Run migrations: `alembic upgrade head`

## Contributing

This is a personal project, but contributions are welcome!

## License

MIT License - See LICENSE file for details
