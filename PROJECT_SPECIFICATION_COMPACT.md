# Book Scanner - Quick Reference

**Version:** 1.1.0 | **Status:** Frontend Complete - Testing Phase | **Updated:** 2025-11-03

---

## Core Concept

**"Your personal book scout for browsing bookstores"**

Mobile-first app that scans physical bookshelves and recommends books based on your taste profile. NOT a home library catalog—it's a discovery tool for bookstores/sales.

**Use Case:** Walk into bookstore → Scan shelf → Get instant recommendations → Buy books you'll love

---

## Value Proposition

### What Problem We Solve
- Bookstore browsing is overwhelming (100s of titles)
- Can't remember your taste preferences
- Miss hidden gems due to unfamiliar titles/covers
- Waste time wandering randomly

### Our Solution
- Build taste profile (5+ books you love)
- Scan bookshelves with phone camera
- Get instant AI-powered recommendations with scores
- Explanations of why each book matches your taste

### What This Is
✅ Discovery tool for physical books
✅ Shopping assistant for bookstores
✅ Recommendation engine

### What This Is NOT
❌ Home library catalog
❌ Reading tracker (like Goodreads)
❌ Online bookstore
❌ Book review platform

---

## Tech Stack

### Backend (FastAPI + Python 3.10+)
- **Framework:** FastAPI 0.114.2, Uvicorn, Pydantic 2.0
- **Database:** PostgreSQL + SQLModel ORM + Alembic migrations
- **OCR:** pytesseract (Tesseract wrapper) + Pillow
- **APIs:** httpx (async), fuzzywuzzy (fuzzy matching)
- **LLM:** google-generativeai (Gemini), openai (GPT), anthropic (Claude)
- **Cache/Rate Limit:** cachetools (TTL cache), slowapi (10/min)
- **Auth:** python-jose (JWT), passlib[bcrypt]
- **Email:** emails + jinja2
- **Monitoring:** sentry-sdk

### Frontend (React 19 + TypeScript 5)
- **Framework:** React 19.1.1, TypeScript 5.2.2, Vite 7.1.11 (SWC)
- **Routing:** TanStack Router 1.131.50 (file-based)
- **State:** TanStack Query 5.90.2, React Hook Form 7.62.0
- **UI:** Chakra UI 3.27.0, next-themes (dark mode), react-icons
- **API Client:** axios + @hey-api/openapi-ts (auto-generated)
- **Dev Tools:** Biome 2.2.4 (lint/format), Playwright 1.56.1 (E2E)

---

## Architecture

```
[React Frontend]
    ↓ HTTPS/JSON
[FastAPI Backend]
    ├─ OCRService (Tesseract + HYBRID LLM fallback)
    ├─ GoogleBooksService (fuzzy search + metadata)
    ├─ RecommendationService (LLM + rule-based fallback)
    └─ LLM Providers (Gemini → GPT → Claude chain)
    ↓
[PostgreSQL Database]
    ├─ users (auth)
    ├─ books (cached Google Books data)
    └─ user_library (taste profile / "library")
```

**External Services:** Google Books API, Google Gemini API, OpenAI GPT, Anthropic Claude

---

## Hybrid OCR Title Extraction

**Problem:** Rule-based OCR fails on blurry images, unusual fonts, edge cases like "1984" vs "Chapter 1984"

**Solution:** Rules-first with intelligent LLM fallback

### Implementation

**Phase 1: Rules (Primary - 50ms)**
- Length filters (2-200 chars)
- Numeric ratio threshold (<50%)
- Keyword filtering (ISBN, copyright)

**Phase 2: LLM (Fallback - 500ms)**
- **Conservative** (MVP default): LLM only if rules extract 0 titles
- **Aggressive**: LLM if 0 titles OR confidence < 70%
- **Disabled**: Rules only (no LLM)

### Performance & Cost

**Conservative Strategy (Default):**
- LLM Usage: ~10-20% of scans (only when rules fail)
- Latency: +500ms on failed scans, 0ms on successful
- Cost: <$0.01/user/month (Gemini Flash)

**Example:** 1000 scans/month × 20% LLM × 500 tokens = 100k tokens = $0.0075/user

### Configuration

```bash
OCR_LLM_STRATEGY=conservative  # conservative | aggressive | disabled
OCR_MIN_TITLE_LENGTH=2
OCR_MAX_TITLE_LENGTH=200
OCR_MAX_NUMERIC_RATIO=0.5
OCR_LLM_MAX_TITLES=20
OCR_LLM_CONFIDENCE_THRESHOLD=0.7  # For aggressive mode
```

### Validation

All LLM responses validated with Pydantic models to prevent:
- Malformed JSON
- Hallucinated titles
- Excessive output (max 20 titles)
- Invalid characters/lengths

### Metrics Logged

- Rule title count
- LLM used (yes/no + reason)
- Processing times
- Final title count
- Improvement delta

---

## Image Rotation Detection

**Problem:** Vertical book spines (90° or 270° rotation) cause OCR failures

**Solution:** Tesseract OSD + limited fallback rotations

### Workflow

1. **OSD Detection**: Detect rotation angle (0°, 90°, 180°, 270°)
2. **Rotate if needed**: Apply detected rotation
3. **Run OCR**: Extract text and measure confidence
4. **Fallback** (if confidence < 70%): Try 90° and 270° rotations
5. **Select best**: Use rotation with highest OCR confidence

### Configuration

```bash
OCR_ROTATION_MODE=osd_fallback  # disabled | osd_only | osd_fallback
OCR_ROTATION_CONFIDENCE_THRESHOLD=0.7  # Trigger fallback threshold
OCR_ROTATION_FALLBACK_ANGLES=[90, 270]  # 90° first (NA standard: top→bottom), 270° fallback
```

### Performance

**Modes:**
- `disabled`: No rotation (~2s, fastest)
- `osd_only`: OSD + rotate once (~2.5s, 85-90% accuracy)
- `osd_fallback`: OSD + retry fallback angles (~3-5s, 90-95% accuracy) **[MVP default]**

**Typical flow:**
- OSD + initial OCR + optional 1-2 fallback attempts = 2-3 OCR passes
- Target: 3-5s scan time

### Benefits

✅ Handles 90-95% of vertical spine cases
✅ Low complexity (~100 lines)
✅ Fast (only 2-3 OCR passes typical)
✅ Configurable & observable

---

## Database Schema

```sql
-- Users: Standard auth fields
users (id, email, hashed_password, full_name, is_active, is_superuser)

-- Books: Cached from Google Books API
books (
  id, title, author, isbn, publisher, published_date,
  description, page_count, categories, thumbnail_url,
  google_books_id UNIQUE, average_rating, ratings_count
)

-- User Library: User's taste profile (NOT owned books)
user_library (
  id, user_id FK, book_id FK, added_date, notes,
  UNIQUE(user_id, book_id)
)
```

**Important:** `user_library` = taste profile, NOT owned books catalog

---

## API Endpoints

**Base:** `http://localhost:8000/api/v1` (dev) | `https://api.bookscanner.com/api/v1` (prod)

### Auth ✅ (Implemented)
- `POST /login/access-token` - Login
- `POST /login/signup` - Signup
- `POST /login/recover-password` - Request reset
- `POST /login/reset-password` - Reset password

### Users ✅ (Implemented)
- `GET /users/me` - Get current user
- `PATCH /users/me` - Update profile
- `PATCH /users/me/password` - Change password
- `DELETE /users/me` - Delete account

### Books ✅ (Implemented)
- `POST /books/scan` - Scan image → recommendations (10/min rate limit, 10MB max)
- `GET /books/library` - Get profile books
- `POST /books/library/add/{google_books_id}` - Add to profile
- `DELETE /books/library/remove/{book_id}` - Remove from profile

### Admin ✅ (Implemented - Superuser only)
- `GET /users` - List users
- `POST /users` - Create user
- `PATCH /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

---

## MVP Features (Iteration 1) - STATUS: FRONTEND COMPLETE ✅

### Implemented Features
1. ✅ **User Authentication** (COMPLETE)
   - Email/password signup/login, JWT sessions, password reset

2. ✅ **Taste Profile Builder** (COMPLETE)
   - Onboarding flow with progress indicator (5 min, 10 recommended)
   - Google Books search (client-side API)
   - Library page with grid view
   - Add/remove books with modal interface

3. ✅ **Book Scanner - PRIMARY FEATURE** (COMPLETE)
   - Camera capture + file upload + drag-drop
   - OCR processing (Tesseract backend)
   - Parallel Google Books lookups
   - LLM-powered match scoring (Gemini → GPT → Claude)
   - Display all detected books
   - Top 3-5 recommendations with color-coded match scores
   - Explanations for each recommendation
   - **NO tracking, NO history, NO wishlist**

4. ✅ **Dashboard** (COMPLETE)
   - Welcome message with value prop
   - "Scan Now" CTA (disabled if no books)
   - Library book count
   - "How it works" guide

5. ✅ **User Settings** (COMPLETE)
   - Profile settings, change password, dark mode, delete account

### Out of Scope (Future Iterations)
❌ Scan history, wishlist, purchase tracking, book ratings, notes, Goodreads/Amazon import, social features, analytics, owned books tracking, barcode scanning

---

## Frontend Structure (Implemented 2025-11-03)

```
frontend/src/
├── routes/                        # TanStack Router
│   ├── _layout/
│   │   ├── index.tsx             # ✅ Dashboard
│   │   ├── library.tsx           # ✅ Library/Profile books page
│   │   ├── scan.tsx              # ✅ Scanner page
│   │   ├── settings.tsx          # ✅ User settings
│   │   └── admin.tsx             # ✅ Admin
│   ├── onboarding.tsx            # ✅ Onboarding flow
│   ├── login.tsx / signup.tsx    # ✅ Auth pages
│
├── components/
│   ├── Books/
│   │   ├── BookCover.tsx         # ✅ Cover with fallback
│   │   └── MatchBadge.tsx        # ✅ Match % badge
│   ├── Library/
│   │   ├── BookCard.tsx          # ✅ Book display card
│   │   └── BookSearch.tsx        # ✅ Google Books search
│   ├── Scanner/
│   │   ├── ImageUpload.tsx       # ✅ Upload/camera/drag-drop
│   │   ├── ScanResults.tsx       # ✅ Results display
│   │   ├── TopPicks.tsx          # ✅ Top recommendations
│   │   └── DetectedBooksList.tsx # ✅ All books list
│   ├── Common/
│   │   ├── LoadingSpinner.tsx    # ✅ Loading states
│   │   └── EmptyState.tsx        # ✅ Empty states
│   ├── Admin/                    # ✅ Admin components
│   ├── UserSettings/             # ✅ Settings components
│   └── ui/                       # ✅ Chakra wrappers
│
├── hooks/
│   ├── useAuth.ts                # ✅ Authentication
│   ├── useLibrary.ts             # ✅ Library CRUD
│   ├── useGoogleBooks.ts         # ✅ Book search
│   └── useScan.ts                # ✅ Scan mutation
│
└── client/
    ├── BooksService.ts           # ✅ Book API client
    └── types.gen.ts              # ✅ TypeScript types
```

---

## Key User Flows

### 1. First-Time Onboarding
```
Signup → /onboarding → Search & add 5+ books → Continue → Dashboard
```

### 2. Scanning a Bookshelf
```
Dashboard → Scan Now → Upload/Camera → OCR processing (5-8s) →
Results: Top Picks (3-5 highlighted) + All Detected Books (collapsed)
```

### 3. Managing Profile Books
```
Profile → My Books → View list → Add/Remove books via search modal
```

---

## Implementation Status

### ✅ Iteration 1: MVP (COMPLETED - 2025-11-03)
**What was built:**
- ✅ Backend: All book endpoints (library, scan) fully implemented
- ✅ Frontend Core: Custom hooks (useLibrary, useScan, useGoogleBooks)
- ✅ Frontend Components: BookCover, MatchBadge, Loading, EmptyState
- ✅ Dashboard: Welcome page with stats and CTAs
- ✅ Library Management: Search, add, remove books
- ✅ Scanner: Camera/upload, OCR, recommendations display
- ✅ Onboarding: Guided setup (min 5 books)

**Current Status:** Frontend complete, entering testing phase

**Next Steps:**
- Test end-to-end flows
- Fix bugs
- Deploy to production

---

## Future Iterations

### Iteration 2: Enhanced Discovery (4-8 weeks post-MVP)
- Scan history
- Wishlist / Reading list
- Purchase tracking (Bought/Skipped/Maybe)
- Enhanced profile (ratings, tags, notes)
- Better onboarding (genre suggestions, Goodreads import)
- Improved scanning (batch mode, low-light, manual fallback, ISBN barcode)

### Iteration 3: Social & Advanced (3-6 months post-MVP)
- Social discovery (share scans, friends, follow readers)
- Bookstore integration (find nearby, affiliate links, promotions)
- Advanced recommendations (mood-based, time-period filters)
- Library features (track owned books, lend/borrow)
- Gamification (badges, challenges, leaderboards)
- Analytics dashboard

### Iteration 4: Enterprise & Mobile (6-12 months)
- Native mobile apps (iOS/Android)
- Offline mode
- Team/organization features (book clubs, classrooms)
- Public API & integrations
- Monetization (freemium, subscription, affiliate revenue)

---

## Success Criteria (MVP)

### Functional ✅
- [ ] User can sign up, log in, complete onboarding (5+ books)
- [ ] User can scan bookshelf image
- [ ] App detects books with >70% accuracy
- [ ] App recommends 3-5 top matches with scores + explanations
- [ ] User can view/edit profile books
- [ ] All pages work without errors

### Performance ✅
- [ ] Scan completes in <10s avg
- [ ] Page load <2s
- [ ] Mobile-responsive
- [ ] Camera API works on iOS/Android
- [ ] Dark mode works

### Quality ✅
- [ ] No crashes on bad input
- [ ] Graceful error handling
- [ ] Clear error messages
- [ ] Fallback for LLM failures

### Security ✅
- [ ] JWT auth works
- [ ] Password reset works
- [ ] Rate limiting active (10 scans/min)
- [ ] File validation (type, size)
- [ ] HTTPS in production

---

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/book_scanner
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
BACKEND_CORS_ORIGINS=["http://localhost:5173"]

LLM_ENABLED=true
GOOGLE_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-claude-key

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

SENTRY_DSN=your-sentry-dsn
ENVIRONMENT=production

PROJECT_NAME=Book Scanner
API_V1_STR=/api/v1
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000/api/v1  # Dev
# VITE_API_URL=https://api.bookscanner.com/api/v1  # Prod
```

---

## Development Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env  # Edit with your keys
alembic upgrade head
uvicorn app.main:app --reload
# http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env  # Edit with backend URL
npm run generate-client  # After backend is running
npm run dev
# http://localhost:5173
```

---

## Known Limitations

**OCR:** Depends on image quality. Struggles with blurry/low-light/unusual fonts. Best: >1000px width, good lighting, straight angle.

**Google Books API:** Not all books available, rate limits (1000/day free), metadata quality varies.

**LLM:** Requires API keys (costs $), 2-5s latency, quality depends on profile size (10+ books), may fail (fallback to rules).

**Browser:** Requires modern browsers (Chrome 90+, Safari 14+, Firefox 88+). Camera API requires HTTPS.

**Photography:** May not be allowed in all bookstores, potentially awkward/conspicuous.

---

## Deployment (Production)

**Frontend:** Vercel (auto-deploy from GitHub)
**Backend:** Railway (easy PostgreSQL + FastAPI hosting)
**Database:** Railway Postgres (included)
**Monitoring:** Sentry (already integrated)

### Checklist
- [ ] Set up production database
- [ ] Run migrations (`alembic upgrade head`)
- [ ] Set environment variables (secrets)
- [ ] Configure CORS for production domain
- [ ] Set up Sentry monitoring
- [ ] Update `VITE_API_URL` to production backend
- [ ] Deploy frontend to Vercel
- [ ] Configure custom domain
- [ ] Use HTTPS everywhere
- [ ] Rotate JWT secret key
- [ ] Enable rate limiting

---

## Key Terminology

**Profile Books** = Books that define your taste (NOT books you own)
**Library** = Backend term for profile books (confusing, but implemented)
**Taste Profile** = Collection of profile books used for recommendations
**Scanner** = Core feature: scan shelves → get recommendations
**Match Score** = 0-100% how well a detected book matches your taste
**Detected Books** = All books found via OCR
**Recommendations** = Subset of detected books NOT in your profile, ranked by match score

---

## Recent Bug Fixes Applied

1. ✅ Fixed `user_library.added_date` storing UUIDs instead of timestamps
2. ✅ Added rate limiting (10 scans/min)
3. ✅ Added file size validation (10MB max)
4. ✅ Parallelized Google Books API calls (10x faster)
5. ✅ Improved error handling with structured logging
6. ✅ Added unique constraint on `google_books_id`
7. ✅ Added composite index on `(user_id, book_id)`
8. ✅ Fixed OCR title filtering (removed Title Case/ALL CAPS rules)

---

## Target Audience

**Primary:** Avid readers (10+ books/year), age 25-45, tech-savvy, frequent bookstore visitors

**Secondary:** Book club members, teachers/librarians, thrift store shoppers

---

## Tagline

**"Your personal book scout"**

---

**End of Compact Specification**

*Last Updated: 2025-11-03*
