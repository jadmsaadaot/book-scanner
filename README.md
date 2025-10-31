# Book Scanner App 📚

A full-stack application that uses OCR to scan book images, identify titles via Google Books API, and provide personalized reading recommendations.

## Quick Links

- **📖 [Complete Documentation](BOOK_SCANNER_README.md)** - Full project overview and architecture
- **🚀 [Quick Start Guide](QUICK_START.md)** - Setup instructions to get running fast
- **💻 [Frontend Development Guide](frontend/FRONTEND_TODO.md)** - Build the UI components

## What This App Does

1. **📸 Upload/Capture** - Take a photo of books on your shelf
2. **🔍 OCR Processing** - Extracts book titles using Tesseract
3. **📚 Book Lookup** - Finds books via Google Books API (with fuzzy matching for OCR errors)
4. **🎯 Smart Recommendations** - Suggests books based on your library preferences
5. **📖 Library Management** - Save and organize your book collection

## Technology Stack

### Backend (Complete ✅)
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database with SQLModel ORM
- **Tesseract OCR** - Free, open-source text recognition
- **Google Books API** - Book metadata (free tier)
- **FuzzyWuzzy** - Intelligent matching for OCR errors

### Frontend (Template Ready)
- **React + TypeScript** - Modern UI framework
- **Vite** - Fast build tool
- **Chakra UI** - Component library
- **TanStack Router** - Type-safe routing

## Quick Start

### 1. Install Tesseract OCR

```bash
# macOS
brew install tesseract

# Ubuntu
sudo apt-get install tesseract-ocr
```

### 2. Install Dependencies

```bash
# Backend
cd backend
pip install -e .

# Frontend
cd frontend
npm install
```

### 3. Set Up Database

```bash
# Start PostgreSQL (via Docker)
docker-compose up -d postgres

# Run migrations
cd backend
alembic upgrade head

# Create admin user
python -m app.initial_data
```

### 4. Start Development Servers

```bash
# Backend (terminal 1)
cd backend
uvicorn app.main:app --reload

# Frontend (terminal 2)
cd frontend
npm run dev
```

**Backend**: http://localhost:8000
**Frontend**: http://localhost:5173
**API Docs**: http://localhost:8000/docs

## Project Structure

```
book-scanner/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   └── books.py          # Book scanning endpoints
│   │   ├── services/
│   │   │   ├── ocr_service.py    # Tesseract OCR
│   │   │   ├── google_books_service.py
│   │   │   └── recommendation_service.py
│   │   └── models.py             # Book & UserLibrary models
│   └── pyproject.toml
├── frontend/
│   └── src/
│       ├── components/           # TODO: Build book scanner UI
│       └── routes/
└── docker-compose.yml
```

## API Endpoints

All endpoints require authentication (JWT token).

### Book Scanning
- `POST /api/v1/books/scan` - Upload image, get detected books + recommendations
- `POST /api/v1/books/library/add/{google_books_id}` - Add book to library
- `GET /api/v1/books/library` - Get your library
- `DELETE /api/v1/books/library/remove/{book_id}` - Remove from library

### Authentication
- `POST /api/v1/login/access-token` - Login
- `POST /api/v1/users/signup` - Register

## Features

### ✅ Implemented (Backend)
- Image upload and OCR processing
- Book title extraction with preprocessing
- Google Books API integration
- Fuzzy matching for OCR errors
- Recommendation engine based on:
  - Author matching (40%)
  - Genre/category overlap (30%)
  - Book ratings (20%)
  - Popularity (10%)
- User library management
- PostgreSQL database with proper relationships

### 🚧 To Build (Frontend)
- Book scanner page with camera/upload
- Library management interface
- Book card components
- Search and filtering

See [frontend/FRONTEND_TODO.md](frontend/FRONTEND_TODO.md) for detailed instructions.

## Deployment (Free Tier)

### Recommended Stack
- **Backend**: [Render.com](https://render.com) (free tier)
- **Frontend**: [Vercel](https://vercel.com) (free tier)
- **Database**: [Supabase](https://supabase.com) (free tier)

**Total Cost**: $0/month for personal use

See [BOOK_SCANNER_README.md](BOOK_SCANNER_README.md) for deployment instructions.

## How the Recommendation Engine Works

```python
# For each detected book, calculate match score:
score = (
    0.4 * author_match +      # Books by authors you've read
    0.3 * category_match +    # Books in genres you like
    0.2 * rating_score +      # Higher rated books
    0.1 * popularity_score    # Based on # of ratings
)
```

Books already in your library are filtered out. Recommendations are sorted by match score.

## Development

### Generate Frontend API Client
After backend changes, regenerate TypeScript types:

```bash
cd frontend
npm run generate-client
```

### Run Tests
```bash
cd backend
pytest
```

### Code Quality
```bash
cd backend
ruff check .
mypy .
```

## Environment Variables

Key variables in `.env`:

```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis
POSTGRES_DB=book_scanner

# Security
SECRET_KEY=your-secret-key-here
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis

# Frontend
FRONTEND_HOST=http://localhost:5173
```

## Troubleshooting

### "Tesseract not found"
- Install: `brew install tesseract` (macOS)
- Verify: `tesseract --version`

### Poor OCR accuracy
- Use well-lit, focused images
- Book spines should be clearly visible
- Try preprocessing: crop, enhance contrast

### Database errors
- Ensure PostgreSQL is running: `docker-compose ps`
- Run migrations: `alembic upgrade head`

## Documentation

- **[BOOK_SCANNER_README.md](BOOK_SCANNER_README.md)** - Complete architecture and documentation
- **[QUICK_START.md](QUICK_START.md)** - Step-by-step setup guide
- **[frontend/FRONTEND_TODO.md](frontend/FRONTEND_TODO.md)** - Frontend development guide
- **[deployment.md](deployment.md)** - Production deployment
- **[development.md](development.md)** - Local development setup

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with the [FastAPI Full Stack Template](https://github.com/fastapi/full-stack-fastapi-template)
