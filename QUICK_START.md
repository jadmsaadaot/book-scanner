# Quick Start Guide - Book Scanner App

## What You Need to Do Next

### Step 1: Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

**Verify installation:**
```bash
tesseract --version
```

### Step 2: Install Backend Dependencies

```bash
cd backend

# Using uv (recommended - faster)
pip install uv
uv pip install -e .

# OR using pip
pip install -e .
```

### Step 3: Set Up Database

The project uses Docker Compose for easy setup:

```bash
# From project root
docker-compose up -d postgres

# This starts PostgreSQL on localhost:5432
```

**OR** install PostgreSQL locally if you prefer.

### Step 4: Configure Environment Variables

The `.env` file should already exist in the project root. Update these values:

```env
# Required changes:
POSTGRES_PASSWORD=your_secure_password
FIRST_SUPERUSER_PASSWORD=your_admin_password
SECRET_KEY=run_this_command_to_generate_one

# To generate SECRET_KEY:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Run Database Migrations

```bash
cd backend
alembic upgrade head
```

This creates all the necessary tables including the new `book` and `userlibrary` tables.

### Step 6: Create Initial Data

```bash
cd backend
python -m app.initial_data
```

This creates the first superuser account.

### Step 7: Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### Step 8: Start Frontend (Optional - for now)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

### Step 9: Test the API

#### 1. Login to get token:
```bash
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=your_admin_password"
```

Save the `access_token` from the response.

#### 2. Test book scanning:
```bash
# Replace YOUR_ACCESS_TOKEN with the token from step 1
curl -X POST "http://localhost:8000/api/v1/books/scan" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/book/image.jpg"
```

#### 3. Check your library:
```bash
curl "http://localhost:8000/api/v1/books/library" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Testing Tips

### Good Test Images
- Well-lit book spines with clear text
- Books arranged vertically or horizontally
- Avoid shadows and reflections
- Take photo straight-on (not at an angle)

### Expected OCR Accuracy
- **Good lighting**: 80-90% accuracy
- **Poor lighting**: 50-70% accuracy
- **Blurry images**: 30-50% accuracy

The fuzzy matching algorithm helps compensate for OCR errors!

## What's Been Built

### Backend ✅
- [x] Database models for Books and UserLibrary
- [x] OCR service with image preprocessing
- [x] Google Books API integration with fuzzy matching
- [x] Recommendation engine based on user library
- [x] API endpoints:
  - POST `/api/v1/books/scan` - Scan book images
  - POST `/api/v1/books/library/add/{google_books_id}` - Add to library
  - GET `/api/v1/books/library` - Get your library
  - DELETE `/api/v1/books/library/remove/{book_id}` - Remove from library

### Frontend ⏳
- [ ] Book scanning UI component (you'll need to build this)
- [ ] Library management interface
- [ ] Recommendation display

The frontend template is ready - you'll need to create the book scanner specific pages.

## Next Steps for Frontend Development

### 1. Create Book Scanner Page

Create `frontend/src/pages/BookScanner.tsx`:
- File upload component
- Camera capture (using device camera)
- Display scanning progress
- Show detected books
- Display recommendations

### 2. Create Library Page

Create `frontend/src/pages/Library.tsx`:
- Display user's book collection
- Grid/list view toggle
- Search and filter books
- Remove books from library

### 3. Add Routes

Update `frontend/src/routes.tsx` to include:
- `/scan` - Book scanning page
- `/library` - User's library page

### 4. Generate TypeScript Client

The template has auto-generated API client. After starting the backend, run:

```bash
cd frontend
npm run generate-client
```

This creates TypeScript types and API functions based on your FastAPI endpoints.

## Common Issues

### "ModuleNotFoundError: No module named 'pytesseract'"
```bash
cd backend
uv pip install -e .  # or pip install -e .
```

### "Tesseract is not installed or it's not in your PATH"
- Install Tesseract OCR (see Step 1)
- Restart your terminal
- Verify: `tesseract --version`

### "Connection refused" when connecting to database
- Make sure PostgreSQL is running: `docker-compose ps`
- Check `.env` has correct `POSTGRES_SERVER` and `POSTGRES_PASSWORD`

### 502 Bad Gateway on Render.com
- Render free tier spins down after 15 min of inactivity
- First request after sleep takes 30-60 seconds to wake up

## Project Structure

```
book-scanner/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── books.py          # Book scanning endpoints
│   │   ├── models.py                  # Book & UserLibrary models
│   │   ├── services/
│   │   │   ├── ocr_service.py        # Tesseract OCR
│   │   │   ├── google_books_service.py  # Google Books API
│   │   │   └── recommendation_service.py # Recommendations
│   │   └── alembic/versions/         # Database migrations
│   ├── pyproject.toml                # Python dependencies
│   └── alembic.ini                   # Database migration config
├── frontend/
│   ├── src/
│   │   ├── pages/                    # TODO: Add BookScanner.tsx
│   │   └── routes.tsx                # TODO: Add book routes
│   └── package.json                  # Node dependencies
├── .env                              # Environment variables
├── docker-compose.yml                # Docker setup
├── BOOK_SCANNER_README.md           # Full documentation
└── QUICK_START.md                   # This file
```

## Need Help?

1. Check `BOOK_SCANNER_README.md` for detailed documentation
2. Visit API docs: `http://localhost:8000/docs`
3. Check backend logs for errors
4. Verify Tesseract is working: `tesseract --version`

## You're Ready! 🎉

The backend is complete and ready to use. You can:
1. Test it using curl commands (see Step 9 above)
2. Use the API docs at `http://localhost:8000/docs`
3. Build the frontend UI for a complete experience

Happy scanning! 📚
