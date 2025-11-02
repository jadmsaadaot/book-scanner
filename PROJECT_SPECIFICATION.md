# Book Scanner - Project Specification & Roadmap

**Version:** 1.0.0
**Last Updated:** 2025-11-02
**Status:** MVP Development Phase

---

## 📖 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Core Value Proposition](#core-value-proposition)
3. [User Problem & Solution](#user-problem--solution)
4. [MVP (Iteration 1)](#mvp-iteration-1)
5. [Future Iterations](#future-iterations)
6. [Architecture Overview](#architecture-overview)
7. [Technology Stack](#technology-stack)
8. [Database Schema](#database-schema)
9. [API Endpoints](#api-endpoints)
10. [Frontend Structure](#frontend-structure)
11. [User Flows](#user-flows)
12. [Implementation Plan](#implementation-plan)
13. [Success Criteria](#success-criteria)

---

## Executive Summary

**Book Scanner** is a mobile-first web application that acts as a personal book scout for people browsing bookstores, book sales, and libraries. Users build a taste profile of books they love, then scan bookshelves with their phone camera to get instant, personalized recommendations of which books to grab.

**Target Launch:** 2-4 weeks from 2025-11-02
**Primary Platform:** Mobile web (iOS/Android browsers)
**Secondary Platform:** Desktop web

---

## Core Value Proposition

### 🎯 The Elevator Pitch

**"Your personal book scout for browsing bookstores"**

> "Browsing bookstores is overwhelming. You scan hundreds of titles, but which ones match YOUR taste? Book Scanner solves this. Add a few books you love, then scan any shelf with your phone. We'll instantly tell you which books you should grab—like having a personal book scout in your pocket."

### Key Benefits

1. **Never miss a hidden gem** - Discover great books even if you don't recognize the title or author
2. **Save time** - Stop wandering aimlessly; get targeted recommendations in seconds
3. **Shop with confidence** - Know exactly why a book matches your reading preferences
4. **Works anywhere** - Bookstores, library sales, thrift shops, friends' shelves, Little Free Libraries

### What This Is NOT

- ❌ A digital library manager for books you own
- ❌ A reading tracker like Goodreads
- ❌ An online bookstore
- ❌ A book review platform

### What This IS

- ✅ A **discovery tool** for finding books in physical locations
- ✅ A **recommendation engine** based on your taste profile
- ✅ A **shopping assistant** for real-time book hunting

---

## User Problem & Solution

### The Problem

**Scenario:** You walk into a bookstore or library sale with hundreds/thousands of books.

**Pain Points:**
- Overwhelmed by choice (analysis paralysis)
- Can't remember what genres/authors you like
- Don't recognize most titles on the shelf
- Miss great books because you judged them by cover
- Waste time browsing randomly
- FOMO (fear of missing out) on hidden gems

### The Solution

**Before Book Scanner:**
```
Enter bookstore → Wander aimlessly → Pick books by cover →
Buy a few → Half of them disappoint → Missed better books
```

**With Book Scanner:**
```
Enter bookstore → Open app → Scan shelf → See "85% match: The Hobbit" →
Grab it → Repeat → Leave with books you'll love
```

### Use Cases

1. **Barnes & Noble browsing** - Scan fiction section, find next great read
2. **Library book sales** - Scan tables of used books, find treasures under $2
3. **Indie bookstores** - Support local shops with confident purchases
4. **Friend's house** - "Should I borrow anything from their collection?"
5. **Thrift stores** - Find unexpected gems among random piles
6. **Little Free Libraries** - Quick scan of neighborhood book boxes

---

## MVP (Iteration 1)

**Timeline:** 2-4 weeks
**Goal:** Launch-ready minimum viable product with core value proposition

### Features In Scope

#### 1. ✅ User Authentication (Already Implemented)
- Email/password signup & login
- JWT-based sessions
- Password reset flow
- Protected routes

#### 2. 🆕 Taste Profile Builder (NEW)
**Purpose:** Establish user's reading preferences to power recommendations

**Features:**
- Onboarding flow: "Add 5-10 books you love"
- Google Books search integration
- Simple list view of profile books
- Add/remove books from profile
- No ratings, no tags, no notes - just a simple list

**Terminology:**
- **Profile Books** = Books that define your taste (NOT books you own)
- Think of it as "Books I Love" not "Books I Own"

**UI Pages:**
- `/onboarding` - Guided setup for new users
- `/profile/books` - Manage your profile books
- Search modal for adding books

#### 3. 🆕 Book Scanner (PRIMARY FEATURE)
**Purpose:** Scan bookshelves and get instant personalized recommendations

**Features:**
- Camera capture or file upload
- OCR processing with Tesseract
- Parallel Google Books API lookups
- LLM-powered recommendation scoring
- Display all detected books
- Highlight top recommendations (3-5 books)
- Show match scores (0-100%)
- Explain why each book matches

**NO tracking, NO history, NO wishlist** - Pure discovery tool

**UI Flow:**
```
/scan
  ↓
[Upload Image] or [Use Camera]
  ↓
Processing... (OCR + matching)
  ↓
Results:
  ✨ Top Picks for You (3-5 highlighted)
  📚 All Detected Books (collapsed list)
```

#### 4. 🆕 Simple Dashboard
- Welcome message
- "Scan Now" CTA button
- Optional: Quick stats (# of profile books)

#### 5. ✅ User Settings (Already Implemented)
- Profile settings
- Change password
- Theme toggle (dark mode)
- Delete account

### Features Out of Scope (Deferred to Iteration 2+)

❌ Scan history (saving past scans)
❌ Wishlist / Reading lists
❌ Purchase tracking ("Bought it" / "Skipped it")
❌ Book ratings in profile
❌ Notes on books
❌ Goodreads/Amazon import
❌ Social features (sharing, friends)
❌ Analytics dashboard
❌ Owned books tracking
❌ Barcode scanning

### MVP Success Criteria

**Functional Requirements:**
- ✅ User can add 5+ books to profile via search
- ✅ User can scan a shelf image (upload or camera)
- ✅ App detects books with >70% accuracy
- ✅ App recommends 3-5 top matches
- ✅ Recommendations include match scores + explanations
- ✅ User can manage profile books (add/remove)

**Non-Functional Requirements:**
- ✅ Scan completes in <10 seconds
- ✅ Works on mobile browsers (iOS Safari, Android Chrome)
- ✅ Handles poor lighting (basic image preprocessing)
- ✅ No crashes on corrupted/invalid images
- ✅ Responsive UI (mobile-first design)

---

## Future Iterations

### 📅 Iteration 2: Enhanced Discovery (4-8 weeks post-MVP)

**New Features:**

1. **Scan History**
   - Save scan results for later reference
   - "Recent Scans" page
   - Re-view recommendations from past bookstore trips

2. **Wishlist / Reading List**
   - Mark books as "Want to Read"
   - Save recommendations for later
   - Export to Goodreads (if API available)

3. **Purchase Tracking** (Optional)
   - Mark books as "Bought" / "Skipped" / "Maybe Later"
   - Improve recommendation accuracy based on choices
   - "Books I've Bought" page

4. **Enhanced Profile**
   - Rate books (1-5 stars) instead of simple list
   - Add tags/preferences (genres, themes, moods)
   - "Why this book?" notes for each profile book

5. **Better Onboarding**
   - Genre-based book suggestions
   - "Pick from popular books" if search is hard
   - Goodreads import (if API available)
   - Amazon reading history import

6. **Improved Scanning**
   - Batch mode (scan multiple shelves in one session)
   - Better low-light image handling
   - Manual title entry fallback (if OCR fails)
   - ISBN barcode scanning

### 📅 Iteration 3: Social & Advanced (3-6 months post-MVP)

**New Features:**

1. **Social Discovery**
   - Share scans with friends
   - "Friends also liked..." recommendations
   - Public reading profiles (opt-in)
   - Follow other readers

2. **Bookstore Integration**
   - Partner with indie bookstores
   - "Find this book nearby" using geolocation
   - Affiliate links to online bookstores
   - In-store promotions/discounts

3. **Advanced Recommendations**
   - "Similar to [specific book]" mode
   - Mood-based filtering ("Need something light and funny")
   - Time-period filtering (classics vs new releases)
   - "Recommend from my unread wishlist"

4. **Library Features**
   - Track owned books (separate from profile)
   - Lend/borrow tracking with friends
   - Read/unread status
   - Reading progress tracker

5. **Gamification**
   - Badges for scanning milestones
   - Reading challenges (themes, genres, goals)
   - Leaderboards (most books scanned, diverse readers)

6. **Analytics Dashboard**
   - Reading patterns visualization
   - Genre distribution pie charts
   - Favorite authors/themes word clouds
   - Reading diversity metrics

### 📅 Iteration 4: Enterprise & Mobile App (6-12 months)

1. **Native Mobile Apps**
   - iOS app (React Native or Swift)
   - Android app (React Native or Kotlin)
   - Offline mode for scanning

2. **Team/Organization Features**
   - Shared team libraries (book clubs, classrooms)
   - Organization accounts (libraries, schools)
   - Group recommendations

3. **API & Integrations**
   - Public API for third-party developers
   - Integration with library systems
   - Integration with book retailers
   - Webhook support

4. **Monetization**
   - Freemium model (5 scans/month free)
   - Premium subscription ($4.99/month)
   - Affiliate revenue from book sales
   - Bookstore partnerships

---

## Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USER DEVICE                          │
│                    (iOS/Android/Desktop)                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         React Frontend (Vite + TypeScript)          │  │
│  │  - TanStack Router (file-based routing)             │  │
│  │  - TanStack Query (data fetching & caching)         │  │
│  │  - Chakra UI (component library)                    │  │
│  │  - Auto-generated API client (OpenAPI)              │  │
│  └──────────────────┬──────────────────────────────────┘  │
│                     │ HTTPS/JSON                           │
└─────────────────────┼──────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Python)                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  API Layer (FastAPI Routes)                         │  │
│  │  - Authentication (JWT)                             │  │
│  │  - Rate Limiting (SlowAPI - 10/min per IP)         │  │
│  │  - File Upload Validation (10MB max)               │  │
│  └──────────────────┬──────────────────────────────────┘  │
│                     ▼                                       │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Service Layer                                      │  │
│  │  - OCRService (Tesseract preprocessing & heuristics)│  │
│  │  - GoogleBooksService (fuzzy search, metadata)     │  │
│  │  - RecommendationService (LLM + rule-based)        │  │
│  │  - LLM Providers (Gemini/GPT/Claude w/ fallback)   │  │
│  └──────────────────┬──────────────────────────────────┘  │
│                     ▼                                       │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Data Layer (SQLModel ORM)                          │  │
│  │  - User management                                  │  │
│  │  - Book metadata caching                            │  │
│  │  - Profile books (user taste)                       │  │
│  └──────────────────┬──────────────────────────────────┘  │
└────────────────────┼────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL Database (SQLModel)                 │
│  - users                                                    │
│  - books (cached from Google Books)                         │
│  - user_library (user's profile books)                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     External Services                       │
│  - Google Books API (book metadata)                         │
│  - Google Gemini API (LLM recommendations)                  │
│  - OpenAI GPT API (LLM fallback)                            │
│  - Anthropic Claude API (LLM fallback)                      │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow: Scanning a Bookshelf

```
1. User uploads image via /scan page
   ↓
2. Frontend validates file (type, size)
   ↓
3. POST /api/v1/books/scan (multipart/form-data)
   ↓
4. Backend validates file (10MB max, image/* only)
   ↓
5. OCRService.extract_text()
   - Preprocess: grayscale, contrast, sharpen, upscale
   - Run Tesseract OCR
   - Extract line-level confidence scores
   ↓
6. OCRService.extract_book_titles()
   - Apply heuristics (length, numeric ratio, keywords)
   - Filter low-confidence detections (<50%)
   ↓
7. GoogleBooksService.fuzzy_search_book() [PARALLEL]
   - Search each detected title
   - Fuzzy match with 70% threshold
   - Return book metadata (title, author, cover, etc.)
   ↓
8. RecommendationService.get_user_library_books()
   - Fetch user's profile books from database
   ↓
9. RecommendationService.filter_and_rank_recommendations()
   - For each detected book:
     a. Check if already in profile (skip if yes)
     b. Calculate match score using LLM or rules
     c. Generate explanation
   - Sort by match score (highest first)
   ↓
10. Return ScanResult { detected_books, recommendations }
    ↓
11. Frontend displays:
    - Top Picks (3-5 highest scored books)
    - All Detected Books (full list, collapsed)
```

---

## Technology Stack

### Backend (FastAPI + Python 3.10+)

**Core Framework:**
- FastAPI 0.114.2+ (async web framework)
- Uvicorn (ASGI server)
- Pydantic 2.0+ (data validation)

**Database:**
- PostgreSQL (production database)
- SQLModel 0.0.21+ (ORM built on SQLAlchemy + Pydantic)
- Alembic 1.12.1+ (database migrations)

**OCR & Image Processing:**
- pytesseract 0.3.10+ (Tesseract OCR wrapper)
- Pillow 10.0+ (image preprocessing)

**External APIs:**
- httpx 0.25.1+ (async HTTP client)
- fuzzywuzzy 0.18+ (fuzzy string matching)
- python-levenshtein 0.25+ (edit distance calculation)

**LLM Providers:**
- google-generativeai 0.8+ (Google Gemini)
- openai 1.0+ (OpenAI GPT)
- anthropic 0.40+ (Anthropic Claude)

**Caching & Performance:**
- cachetools 5.3+ (TTL cache for LLM responses)
- slowapi 0.1.9+ (rate limiting)

**Security & Auth:**
- python-jose[cryptography] (JWT tokens)
- passlib[bcrypt] 1.7.4+ (password hashing)
- bcrypt 4.3.0

**Email:**
- emails 0.6 (password recovery emails)
- jinja2 3.1.4+ (email templates)

**Monitoring:**
- sentry-sdk[fastapi] 2.18.0 (error tracking)

### Frontend (React 19 + TypeScript 5)

**Core Framework:**
- React 19.1.1 (UI library)
- TypeScript 5.2.2 (type safety)
- Vite 7.1.11 (build tool with SWC)

**Routing:**
- @tanstack/router 1.131.50 (file-based routing)
- @tanstack/router-plugin (Vite integration)

**State Management:**
- @tanstack/query 5.90.2 (React Query for data fetching)
- React Hook Form 7.62.0 (form state)

**UI Framework:**
- Chakra UI 3.27.0 (component library)
- @chakra-ui/react (core components)
- next-themes 0.4.6 (dark mode)
- react-icons 5.5.0 (icon library)

**API Client:**
- axios 1.12.2 (HTTP client)
- @hey-api/openapi-ts 0.73.0 (auto-generated from OpenAPI spec)

**Developer Tools:**
- Biome 2.2.4 (linting & formatting)
- Playwright 1.56.1 (E2E testing)
- dotenv 17.2.2 (environment variables)

### Development & Build Tools

**Package Management:**
- npm (frontend)
- pip (backend)

**Code Quality:**
- Ruff (Python linting/formatting)
- Mypy (Python type checking)
- Biome (TypeScript linting/formatting)

**Testing:**
- Pytest (Python unit/integration tests)
- Playwright (E2E tests)

**Version Control:**
- Git
- GitHub (repository hosting)

---

## Database Schema

### Current Schema (Production-Ready)

```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_users_email ON users(email);

-- Books Table (Cached from Google Books API)
CREATE TABLE books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    author VARCHAR(500),
    isbn VARCHAR(13),
    publisher VARCHAR(255),
    published_date VARCHAR(50),
    description TEXT,
    page_count INTEGER,
    categories VARCHAR(500),  -- JSON string: ["Fiction", "Fantasy"]
    thumbnail_url VARCHAR(1000),
    google_books_id VARCHAR(100) UNIQUE,  -- External ID
    average_rating FLOAT,
    ratings_count INTEGER
);

CREATE INDEX idx_books_isbn ON books(isbn);
CREATE INDEX idx_books_google_books_id ON books(google_books_id);
CREATE UNIQUE INDEX idx_books_google_books_id_unique ON books(google_books_id);

-- User Library / Profile Books (Junction Table)
CREATE TABLE user_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    added_date TIMESTAMP NOT NULL DEFAULT NOW(),  -- Fixed in recent migration
    notes TEXT,
    UNIQUE(user_id, book_id)  -- Prevent duplicate entries
);

CREATE INDEX idx_user_library_user_id ON user_library(user_id);
CREATE INDEX idx_user_library_book_id ON user_library(book_id);
CREATE INDEX idx_user_library_composite ON user_library(user_id, book_id);  -- Performance
```

### Key Schema Notes

**Recent Fixes Applied:**
1. **Fixed `added_date` field** - Was storing UUIDs instead of timestamps (migration created)
2. **Added unique constraint** on `google_books_id` to prevent duplicate books
3. **Added composite index** on `(user_id, book_id)` for faster lookups

**Terminology Clarification:**
- `user_library` table = **User's Profile Books** (NOT owned books)
- Purpose: Define user's taste for recommendations
- Backend uses "library" but MVP frontend calls it "profile"

---

## API Endpoints

### Base URL
```
Production: https://api.bookscanner.com/api/v1
Development: http://localhost:8000/api/v1
```

### Authentication Endpoints ✅ (Implemented)

```http
POST   /login/access-token
  Body: { email, password }
  Returns: { access_token, token_type }

POST   /login/signup
  Body: { email, password, full_name? }
  Returns: { access_token, token_type }

POST   /login/recover-password
  Body: { email }
  Returns: { message }

POST   /login/reset-password
  Body: { token, new_password }
  Returns: { message }
```

### User Management ✅ (Implemented)

```http
GET    /users/me
  Returns: UserPublic

PATCH  /users/me
  Body: { email?, full_name? }
  Returns: UserPublic

PATCH  /users/me/password
  Body: { current_password, new_password }
  Returns: { message }

DELETE /users/me
  Returns: { message }
```

### Book Scanning ✅ (Implemented)

```http
POST   /books/scan
  Headers: Authorization: Bearer <token>
  Body: multipart/form-data (file: image)
  Rate Limit: 10 requests/minute per IP
  Max File Size: 10MB
  Returns: ScanResult {
    detected_books: DetectedBook[],
    recommendations: DetectedBook[]
  }
```

**ScanResult Schema:**
```typescript
interface DetectedBook {
  title: string
  author: string | null
  isbn: string | null
  thumbnail_url: string | null
  google_books_id: string | null
  confidence: number          // OCR confidence (0-1)
  match_score: number         // Recommendation score (0-1)
  in_library: boolean         // Already in user's profile?
  recommendation_explanation: string | null  // Why recommended
}
```

### Profile Books Management ✅ (Implemented - as "Library")

**Note:** Backend uses `/books/library/*` but MVP frontend treats this as "profile"

```http
GET    /books/library
  Query: ?skip=0&limit=100
  Returns: BooksPublic {
    data: BookPublic[],
    count: number
  }

POST   /books/library/add/{google_books_id}
  Returns: BookPublic (newly added book)

DELETE /books/library/remove/{book_id}
  Returns: { message }
```

### Admin Endpoints ✅ (Implemented - Superuser Only)

```http
GET    /users
  Query: ?skip=0&limit=100
  Returns: UsersPublic

POST   /users
  Body: { email, password, full_name?, is_superuser? }
  Returns: UserPublic

PATCH  /users/{user_id}
  Body: { email?, full_name?, is_active?, is_superuser? }
  Returns: UserPublic

DELETE /users/{user_id}
  Returns: { message }
```

### Future Endpoints (Iteration 2+)

```http
# Search Google Books (for adding to profile)
POST   /books/search
  Body: { query: string, max_results?: number }
  Returns: BookPublic[]

# Scan History
GET    /scans
  Returns: ScanHistory[]

GET    /scans/{scan_id}
  Returns: ScanResult

# Wishlist (Iteration 2)
GET    /wishlist
POST   /wishlist/add/{book_id}
DELETE /wishlist/remove/{book_id}
```

---

## Frontend Structure

### Directory Structure

```
frontend/
├── src/
│   ├── client/                    # Auto-generated API client (OpenAPI)
│   │   ├── services/              # API service functions
│   │   ├── types.gen.ts           # TypeScript types
│   │   └── index.ts
│   │
│   ├── components/
│   │   ├── Onboarding/            # 🆕 MVP
│   │   │   ├── OnboardingPage.tsx # Main onboarding flow
│   │   │   ├── BookSearch.tsx     # Search Google Books
│   │   │   └── BookSearchResult.tsx
│   │   │
│   │   ├── Profile/               # 🆕 MVP (Profile Books)
│   │   │   ├── ProfileBooksPage.tsx
│   │   │   ├── ProfileBookCard.tsx
│   │   │   └── AddBookButton.tsx
│   │   │
│   │   ├── Scanner/               # 🆕 MVP (Core Feature)
│   │   │   ├── ScanPage.tsx       # Main scanner page
│   │   │   ├── ImageUpload.tsx    # Drag-drop + camera
│   │   │   ├── ScanResults.tsx    # Results display
│   │   │   ├── TopPicks.tsx       # Highlighted recommendations
│   │   │   └── AllDetectedBooks.tsx
│   │   │
│   │   ├── Dashboard/             # 🆕 MVP
│   │   │   └── DashboardPage.tsx  # Simple welcome + CTA
│   │   │
│   │   ├── Common/                # 🆕 MVP (Reusable)
│   │   │   ├── BookCover.tsx      # Cover image w/ fallback
│   │   │   ├── MatchBadge.tsx     # "85% match" indicator
│   │   │   └── LoadingSpinner.tsx
│   │   │
│   │   ├── Admin/                 # ✅ Existing
│   │   │   ├── AddUser.tsx
│   │   │   ├── EditUser.tsx
│   │   │   └── DeleteUser.tsx
│   │   │
│   │   ├── UserSettings/          # ✅ Existing
│   │   │   ├── UserInformation.tsx
│   │   │   ├── ChangePassword.tsx
│   │   │   ├── Appearance.tsx
│   │   │   └── DeleteAccount.tsx
│   │   │
│   │   ├── Common/                # ✅ Existing
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── SidebarItems.tsx
│   │   │   └── UserMenu.tsx
│   │   │
│   │   └── ui/                    # ✅ Existing (Chakra wrappers)
│   │       ├── button.tsx
│   │       ├── input.tsx
│   │       ├── dialog.tsx
│   │       └── ... (16 components)
│   │
│   ├── hooks/
│   │   ├── useAuth.ts             # ✅ Existing
│   │   ├── useBooks.ts            # 🆕 MVP (Book operations)
│   │   ├── useProfile.ts          # 🆕 MVP (Profile books)
│   │   └── useScan.ts             # 🆕 MVP (Scan mutation)
│   │
│   ├── routes/                    # TanStack Router (file-based)
│   │   ├── __root.tsx             # ✅ Root layout
│   │   ├── _layout.tsx            # ✅ Protected layout
│   │   │   ├── index.tsx          # 🆕 Dashboard (replace items)
│   │   │   ├── scan.tsx           # 🆕 Scanner page
│   │   │   ├── profile/
│   │   │   │   └── books.tsx      # 🆕 Profile books page
│   │   │   ├── settings.tsx       # ✅ Existing
│   │   │   └── admin.tsx          # ✅ Existing
│   │   ├── login.tsx              # ✅ Existing
│   │   ├── signup.tsx             # ✅ Existing
│   │   ├── onboarding.tsx         # 🆕 MVP
│   │   ├── recover-password.tsx   # ✅ Existing
│   │   └── reset-password.tsx     # ✅ Existing
│   │
│   ├── theme/                     # Chakra UI theme
│   │   └── index.ts
│   │
│   ├── main.tsx                   # App entry point
│   ├── theme.tsx                  # Theme configuration
│   └── utils.ts                   # Utility functions
│
├── public/
│   └── assets/images/
│
├── package.json
├── vite.config.ts
├── tsconfig.json
├── .env                           # VITE_API_URL
└── README.md
```

### Key Frontend Patterns

**Routing (TanStack Router):**
- File-based routing (auto-generates route tree)
- Type-safe navigation
- Protected routes via `_layout.tsx` (checks auth)
- Auto-redirect to `/login` if unauthenticated

**Data Fetching (TanStack Query):**
- Global QueryClient with error handling
- Query keys: `["currentUser"]`, `["profileBooks"]`, `["scan", scanId]`
- Automatic caching & invalidation
- Optimistic updates (optional)

**Forms (React Hook Form):**
- Validation modes: `onBlur`, `criteriaMode: "all"`
- Integration with Chakra UI via Controller
- Error display with Field components

**API Client (Auto-Generated):**
```bash
# Regenerate after backend changes
npm run generate-client
```

Reads OpenAPI spec from `http://localhost:8000/api/v1/openapi.json`
Outputs to `src/client/` with full TypeScript types

---

## User Flows

### 🆕 First-Time User Onboarding

```
1. User visits app → Redirected to /login
2. Click "Sign up"
3. Enter email, password, name
4. Submit → Account created
5. Redirected to /onboarding
6. Onboarding Page:
   ┌──────────────────────────────────┐
   │ Welcome to Book Scanner!         │
   │ Tell us what you love to read    │
   │                                  │
   │ [Search for books...]            │
   │                                  │
   │ Your Profile Books (0):          │
   │ (empty state)                    │
   │                                  │
   │ Add at least 5 books to continue │
   │                                  │
   │ [Skip for now] [Continue →]     │
   └──────────────────────────────────┘
7. User searches: "The Hobbit"
8. Results appear → Click "Add"
9. Book added to profile list
10. Repeat until 5+ books added
11. Click "Continue" → Redirected to /
12. Dashboard shows:
    ┌──────────────────────────────────┐
    │ Ready to discover books!         │
    │ You have 7 books in your profile │
    │                                  │
    │ [📷 Scan a Bookshelf]            │
    └──────────────────────────────────┘
```

### 🆕 Scanning a Bookshelf

```
1. User at bookstore/library sale
2. Opens app → Tap "Scan" in sidebar or dashboard
3. /scan page:
   ┌──────────────────────────────────┐
   │ Scan a Bookshelf                 │
   │                                  │
   │ ┌────────────────────────────┐  │
   │ │  Drag & drop image         │  │
   │ │  or                        │  │
   │ │  [Choose File] [Camera 📷] │  │
   │ └────────────────────────────┘  │
   └──────────────────────────────────┘
4. User taps [Camera] → Browser requests camera permission
5. User takes photo of shelf
6. Image uploads → Processing...
   ┌──────────────────────────────────┐
   │ 🔍 Scanning bookshelf...         │
   │ [Progress bar]                   │
   │ Detecting book titles...         │
   └──────────────────────────────────┘
7. Results appear (5-8 seconds later):
   ┌──────────────────────────────────┐
   │ ✨ Top Picks for You             │
   │                                  │
   │ ┌──────────────────────────────┐│
   │ │ 📕 The Hobbit                ││
   │ │ by J.R.R. Tolkien            ││
   │ │ ⭐ 95% match                 ││
   │ │ "You loved The Lord of the   ││
   │ │ Rings. This fantasy classic  ││
   │ │ has similar epic adventure." ││
   │ └──────────────────────────────┘│
   │                                  │
   │ ┌──────────────────────────────┐│
   │ │ 📘 Dune                      ││
   │ │ by Frank Herbert             ││
   │ │ ⭐ 88% match                 ││
   │ │ "Sci-fi epic with world-     ││
   │ │ building like your favorites"││
   │ └──────────────────────────────┘│
   │                                  │
   │ [+ 1 more pick]                  │
   │                                  │
   │ 📚 All Detected Books (12)       │
   │ [Show All ▼]                     │
   └──────────────────────────────────┘
8. User finds "The Hobbit" on shelf
9. User buys it (or not) - no tracking in MVP
10. User can scan another shelf or close app
```

### Managing Profile Books

```
1. User navigates to Profile → My Books
2. /profile/books page:
   ┌──────────────────────────────────┐
   │ My Profile Books (7)             │
   │                                  │
   │ [+ Add Books]                    │
   │ ┌──────────────────────────────┐│
   │ │ 📗 The Hobbit                ││
   │ │ by J.R.R. Tolkien            ││
   │ │ [Remove]                     ││
   │ └──────────────────────────────┘│
   │ ┌──────────────────────────────┐│
   │ │ 📙 1984                      ││
   │ │ by George Orwell             ││
   │ │ [Remove]                     ││
   │ └──────────────────────────────┘│
   │ ... (5 more)                     │
   └──────────────────────────────────┘
3. Click [+ Add Books]
4. Search modal opens
5. Search for book → Add to profile
6. Click [Remove] on book → Confirmation dialog
7. Book removed from profile
```

---

## Implementation Plan

### Week 1: Backend Prep & Onboarding Frontend

**Backend Tasks (Minimal):**
- [ ] Verify `/books/library/*` endpoints work as "profile" endpoints
- [ ] Add `/books/search` endpoint (if needed for Google Books search)
- [ ] Test scan endpoint thoroughly
- [ ] Update documentation to clarify "library" = "profile"

**Frontend Tasks:**
- [ ] Create `/onboarding` route
- [ ] Build OnboardingPage component
- [ ] Build BookSearch component (Google Books search)
- [ ] Build BookSearchResult component
- [ ] Integrate with `/books/library/add` API
- [ ] Add validation: minimum 5 books
- [ ] Create skip/continue flow

**Hooks:**
- [ ] Create `useProfile` hook (fetch, add, remove profile books)
- [ ] Create `useBookSearch` hook (search Google Books)

**Deliverable:** New users can add books to profile via onboarding

---

### Week 2: Scanner UI & Dashboard

**Frontend Tasks:**
- [ ] Create `/scan` route
- [ ] Build ScanPage component
- [ ] Build ImageUpload component (drag-drop + camera)
- [ ] Integrate browser Camera API
- [ ] Add file validation (type, size)
- [ ] Build ScanResults component
- [ ] Build TopPicks component (highlighted recommendations)
- [ ] Build AllDetectedBooks component (collapsible list)
- [ ] Build MatchBadge component (score indicator)
- [ ] Build LoadingSpinner component (OCR processing)

**Hooks:**
- [ ] Create `useScan` mutation hook (upload → scan → results)

**Dashboard:**
- [ ] Replace existing items page with simple dashboard
- [ ] Show "Scan Now" CTA button
- [ ] Show profile book count
- [ ] Add welcome message

**Deliverable:** Users can scan shelves and see recommendations

---

### Week 3: Profile Management & Polish

**Frontend Tasks:**
- [ ] Create `/profile/books` route
- [ ] Build ProfileBooksPage component
- [ ] Build ProfileBookCard component
- [ ] Add "Add Books" button (opens search modal)
- [ ] Build BookCover component (with fallback image)
- [ ] Add empty state for new users

**Shared Components:**
- [ ] Refactor common code (BookCover, LoadingSpinner, etc.)
- [ ] Create consistent styling
- [ ] Add responsive design for mobile

**Deliverable:** Users can manage their profile books

---

### Week 4: Testing, Bug Fixes & Launch Prep

**Testing:**
- [ ] Test onboarding flow (happy path + edge cases)
- [ ] Test scanning flow (various image qualities)
- [ ] Test profile management (add/remove books)
- [ ] Test on mobile browsers (iOS Safari, Android Chrome)
- [ ] Test on desktop browsers (Chrome, Firefox, Safari)
- [ ] Test error handling (network failures, bad images, etc.)
- [ ] Test empty states (no profile books, no scan results)

**Bug Fixes:**
- [ ] Fix any critical bugs
- [ ] Improve loading states
- [ ] Improve error messages
- [ ] Add toasts for success/error feedback

**Polish:**
- [ ] Improve UI/UX based on testing
- [ ] Add animations/transitions
- [ ] Optimize performance (lazy loading, code splitting)
- [ ] Add meta tags (SEO, social sharing)

**Documentation:**
- [ ] Update README with setup instructions
- [ ] Document environment variables
- [ ] Create user guide (how to use the app)

**Deployment:**
- [ ] Set up production database
- [ ] Deploy backend to Railway/Render/DigitalOcean
- [ ] Deploy frontend to Vercel/Netlify
- [ ] Configure environment variables
- [ ] Test production deployment
- [ ] Set up monitoring (Sentry)

**Deliverable:** Production-ready MVP

---

## Success Criteria

### MVP Launch Requirements

**Functional Requirements:**
✅ All core features work end-to-end:
- [ ] User can sign up and log in
- [ ] User can complete onboarding (add 5+ books)
- [ ] User can scan a bookshelf image
- [ ] App detects books with >70% accuracy
- [ ] App recommends 3-5 top matches
- [ ] Recommendations show match scores + explanations
- [ ] User can view/edit profile books
- [ ] User can navigate all pages without errors

**Non-Functional Requirements:**
✅ Performance & UX:
- [ ] Scan completes in <10 seconds (avg)
- [ ] Page load time <2 seconds
- [ ] Mobile-responsive (works on phones)
- [ ] Camera API works on iOS/Android
- [ ] Dark mode works correctly
- [ ] No console errors in browser

**Quality Requirements:**
✅ Stability:
- [ ] No crashes on bad input (corrupted images, etc.)
- [ ] Graceful error handling (network failures, API errors)
- [ ] Clear error messages for users
- [ ] Fallback for LLM failures (rule-based scoring)

**Security Requirements:**
✅ Security basics:
- [ ] JWT authentication works
- [ ] Password reset flow works
- [ ] Rate limiting active (10 scans/min)
- [ ] File upload validation (type, size)
- [ ] No sensitive data in logs
- [ ] HTTPS in production

### Post-Launch Success Metrics (Monitor)

**User Engagement:**
- Daily active users (DAU)
- Scans per user per week
- Profile books per user (avg)
- Retention rate (7-day, 30-day)

**Technical Metrics:**
- OCR accuracy rate (%)
- Scan success rate (%)
- Average scan time (seconds)
- API error rate (%)
- LLM vs rule-based recommendation ratio

**User Satisfaction:**
- User feedback/reviews
- Feature requests
- Bug reports
- Net Promoter Score (NPS)

---

## Known Limitations & Future Improvements

### Current Limitations

**OCR Accuracy:**
- Depends heavily on image quality
- Struggles with:
  - Blurry or low-resolution images
  - Poor lighting (too dark/too bright)
  - Unusual fonts (decorative, handwritten)
  - Damaged or worn book spines
  - Books at odd angles
- Recommended: >1000px width, good lighting, straight angle

**Google Books API:**
- Not all books available (especially older/obscure titles)
- Rate limits (1000 requests/day free tier)
- Metadata quality varies
- No real-time inventory (doesn't know if book is in stock)

**LLM Recommendations:**
- Requires API keys (costs money per request)
- Response time: 2-5 seconds
- Quality depends on profile size (better with 10+ books)
- May fail (fallback to rule-based scoring)
- Not 100% accurate (subjective taste matching)

**Browser Support:**
- Requires modern browsers (Chrome 90+, Safari 14+, Firefox 88+)
- Camera API requires HTTPS (doesn't work on `http://`)
- No Internet Explorer support
- Some older mobile browsers may not support all features

**Bookstore Photography:**
- May not be allowed in all stores
- Could be awkward/conspicuous
- Privacy concerns (other customers in photo)

### Planned Improvements (Future Iterations)

**OCR Enhancements:**
- Advanced preprocessing (adaptive thresholding, deskewing)
- Multi-pass OCR with different settings
- Machine learning-based title extraction
- Support for spine orientation detection
- Batch processing (multiple images → one scan)

**Recommendation Quality:**
- Collaborative filtering (recommend what similar users liked)
- Genre preference learning over time
- Mood-based recommendations
- Time-period filtering (new vs classic)
- "More like this" feature

**User Experience:**
- Offline mode (save scans for later processing)
- Faster scanning (edge OCR, client-side preprocessing)
- Better camera UI (guidelines, auto-capture)
- Scan history with bookmarks
- Share scans with friends

**Integrations:**
- Goodreads import (reading history)
- Amazon integration (purchase history)
- Library system integration (check local availability)
- Bookstore partnerships (in-store promotions)

---

## Environment Configuration

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/book_scanner

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS (comma-separated)
BACKEND_CORS_ORIGINS=["http://localhost:5173","https://bookscanner.com"]

# LLM Providers (at least one required)
LLM_ENABLED=true
GOOGLE_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-claude-api-key-here

# Email (for password recovery)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
EMAILS_FROM_EMAIL=noreply@bookscanner.com
EMAILS_FROM_NAME=Book Scanner

# Sentry (optional, for error tracking)
SENTRY_DSN=your-sentry-dsn-here
ENVIRONMENT=production  # or local, staging

# Application
PROJECT_NAME=Book Scanner
API_V1_STR=/api/v1
```

### Frontend (.env)

```bash
# API URL (backend)
VITE_API_URL=http://localhost:8000/api/v1  # Development
# VITE_API_URL=https://api.bookscanner.com/api/v1  # Production
```

---

## Development Workflow

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload

# Server runs on http://localhost:8000
# OpenAPI docs: http://localhost:8000/docs
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with backend URL

# Generate API client (after backend is running)
npm run generate-client

# Start dev server
npm run dev

# App runs on http://localhost:5173
```

### Generate API Client (After Backend Changes)

```bash
cd frontend
npm run generate-client
```

This command:
1. Fetches OpenAPI spec from `http://localhost:8000/api/v1/openapi.json`
2. Generates TypeScript types and services
3. Outputs to `src/client/`

**When to run:**
- After adding new backend endpoints
- After changing request/response schemas
- After modifying Pydantic models

---

## Testing Strategy (Future)

### Backend Tests (Pytest)

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/api/test_books.py
```

**Test Coverage:**
- Unit tests for services (OCR, recommendations, Google Books)
- Integration tests for API endpoints
- Database tests (CRUD operations)
- Authentication tests

### Frontend Tests (Playwright)

```bash
# Run E2E tests
npm run test:e2e

# Run in headed mode (visible browser)
npm run test:e2e:headed

# Run specific test
npm run test:e2e -- scan.spec.ts
```

**Test Coverage:**
- E2E tests for critical flows (signup, onboarding, scan)
- Component tests (React Testing Library)
- Hook tests (custom hooks)

---

## Deployment Guide (Production)

### Recommended Stack

**Frontend:**
- Vercel (auto-deploy from GitHub)
- Netlify (alternative)
- Cloudflare Pages (alternative)

**Backend:**
- Railway (easy PostgreSQL + FastAPI hosting)
- Render (alternative)
- DigitalOcean App Platform (alternative)

**Database:**
- Railway Postgres (included with backend)
- Supabase (managed PostgreSQL)
- Neon (serverless PostgreSQL)

**Monitoring:**
- Sentry (error tracking - already integrated)
- Vercel Analytics (frontend metrics)
- Railway Metrics (backend metrics)

### Deployment Checklist

**Backend:**
- [ ] Set up production database
- [ ] Run migrations (`alembic upgrade head`)
- [ ] Set environment variables (secrets)
- [ ] Configure CORS for production domain
- [ ] Set up Sentry monitoring
- [ ] Test all endpoints

**Frontend:**
- [ ] Update `VITE_API_URL` to production backend
- [ ] Generate production API client
- [ ] Build production bundle (`npm run build`)
- [ ] Deploy to Vercel/Netlify
- [ ] Configure custom domain
- [ ] Set up CDN for images

**Security:**
- [ ] Use HTTPS everywhere
- [ ] Rotate JWT secret key
- [ ] Use strong database passwords
- [ ] Enable rate limiting
- [ ] Set up firewall rules

---

## Marketing & Positioning

### Target Audience

**Primary:**
- Avid readers (10+ books/year)
- Age: 25-45
- Comfortable with technology
- Frequent bookstore/library visitors
- Value personalized recommendations

**Secondary:**
- Book club members
- Teachers/librarians
- Thrift store shoppers
- Collectors of used books

### Tagline Options

1. **"Your personal book scout"** (Simple, clear)
2. **"Find your next favorite book—instantly"** (Benefit-focused)
3. **"Smart book hunting"** (Concise)
4. **"Never miss a great book again"** (Problem-focused)
5. **"Discover books tailored to your taste"** (Feature-focused)

**Recommended:** "Your personal book scout"

### Key Messaging

**Problem:** Bookstores are overwhelming. How do you know what's worth buying?

**Solution:** Book Scanner learns your taste, then tells you exactly which books to grab.

**Differentiation:**
- **vs Goodreads:** Real-time recommendations while browsing (not just tracking)
- **vs Amazon:** Works in physical stores (not online only)
- **vs Store staff:** Always available, knows YOUR taste (not generic picks)

---

## FAQ (Frequently Asked Questions)

**Q: Does this work with ebooks?**
A: Not currently. MVP focuses on physical bookstores. Ebook support may come in Iteration 3.

**Q: Can I scan books I already own?**
A: Yes, but the app is designed for discovering NEW books to buy. For cataloging owned books, consider using Goodreads or LibraryThing.

**Q: How accurate is the OCR?**
A: With good lighting and clear images, 70-90% accuracy. Works best with straight-on shots of book spines.

**Q: How are recommendations generated?**
A: Using AI (Google Gemini) by default, with fallback to rule-based scoring (author, genre, ratings).

**Q: Does it work offline?**
A: Not in MVP. Requires internet for OCR, Google Books API, and LLM recommendations. Offline mode planned for Iteration 4.

**Q: How much does it cost?**
A: MVP is free. Monetization (freemium/subscription) planned for Iteration 4.

**Q: Can I share my scans with friends?**
A: Not in MVP. Social features planned for Iteration 3.

**Q: What if the app doesn't detect a book?**
A: In MVP, it won't appear in results. Iteration 2 will add manual title entry fallback.

**Q: Is my reading data private?**
A: Yes. Your profile books and scans are private by default. Public profiles are planned as opt-in for Iteration 3.

---

## Contact & Support

**Developer:** [Your Name]
**Email:** support@bookscanner.com
**GitHub:** https://github.com/yourusername/book-scanner
**Issues:** https://github.com/yourusername/book-scanner/issues

---

## Changelog

### Version 1.0.0 (2025-11-02) - Initial Specification
- Defined MVP scope and roadmap
- Clarified core value proposition (discovery vs library management)
- Created detailed architecture documentation
- Outlined implementation plan (4-week timeline)
- Documented existing backend (FastAPI) and frontend (React) structure
- Planned 3 future iterations with feature breakdown

---

## License

MIT License - See LICENSE file for details

---

**End of Document**

*This specification is a living document and will be updated as the project evolves.*
