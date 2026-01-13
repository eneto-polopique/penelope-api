# Penelope Dataset API

Professional-grade REST API for accessing woven fabric and Pantone color data.

## Project Structure

```
penelope_dataset/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and settings management
│   ├── database.py          # Database connection and session
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic schemas for validation
│   └── routers/
│       ├── __init__.py
│       ├── wovens.py        # Woven endpoints
│       └── pantone.py       # Pantone color endpoints
├── dataset/
│   ├── final_penelope_dataset.json
│   └── knn_pantone.json
├── scripts/
│   └── load_data.py         # Script to load data into database
├── .env                     # Environment variables (not in git)
├── .env.example             # Example environment file
└── pyproject.toml           # Project dependencies
```

## Features

- **RESTful API** with FastAPI
- **Automatic API documentation** (Swagger UI and ReDoc)
- **Environment-based configuration** using .env files
- **Database connection pooling** for optimal performance
- **Pagination support** for large datasets
- **Filtering capabilities** for woven queries
- **CORS enabled** for cross-origin requests
- **Health check endpoint** for monitoring
- **Professional error handling**

## API Endpoints

### Wovens

1. **GET /wovens** - List all wovens with pagination and filters
   - Query params:
     - `page` (default: 1) - Page number
     - `page_size` (default: 50, max: 100) - Items per page
     - `color_name` (optional) - Filter by color name
     - `category` (optional) - Filter by category
   - Returns: `id`, `color_name`, `category`

2. **GET /wovens/{id}** - Get detailed woven information
   - Returns: All woven fields + similar wovens with filenames

### Pantone Colors

3. **GET /pantone-colors** - List all Pantone colors
   - Returns: `name`, `hex`

4. **GET /pantone-colors/{name}** - Get detailed Pantone color information
   - Returns: All fields + nearest wovens with filenames

### Other

- **GET /** - API information and endpoint list
- **GET /health** - Health check with database status
- **GET /docs** - Interactive API documentation (Swagger UI)
- **GET /redoc** - Alternative API documentation (ReDoc)

## Setup

### 1. Install Dependencies

```bash
uv pip install -e .
```

Or manually:
```bash
uv pip install fastapi uvicorn[standard] sqlalchemy pg8000 pydantic pydantic-settings python-dotenv
```

### 2. Configure Environment

Copy the example environment file and update with your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials.

### 3. Load Data into Database

First, create the database schema (run the SQL from `aux/schema.sql`), then:

```bash
uv run scripts/load_data.py
```

### 4. Run the API

```bash
# Development mode (with auto-reload)
uv run api/main.py

# Or using uvicorn directly
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Usage Examples

### List wovens with filters
```bash
# Get first page
curl "http://localhost:8000/wovens?page=1&page_size=20"

# Filter by color
curl "http://localhost:8000/wovens?color_name=red"

# Filter by category
curl "http://localhost:8000/wovens?category=Jacquard"

# Combined filters with pagination
curl "http://localhost:8000/wovens?color_name=blue&category=Jacquard&page=1&page_size=10"
```

### Get specific woven
```bash
curl "http://localhost:8000/wovens/1"
```

### List all Pantone colors
```bash
curl "http://localhost:8000/pantone-colors"
```

### Get specific Pantone color
```bash
curl "http://localhost:8000/pantone-colors/PANTONE%20Yellow%20C"
```

### Health check
```bash
curl "http://localhost:8000/health"
```

## Configuration

All configuration is managed through environment variables in `.env`:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=penelope_db
DB_USER=penelope
DB_PASSWORD=your_password

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Pagination
DEFAULT_PAGE_SIZE=50
MAX_PAGE_SIZE=100
```

## Production Deployment

For production, consider:

1. Set `API_RELOAD=false`
2. Use a production ASGI server like Gunicorn with Uvicorn workers
3. Configure CORS `allow_origins` to specific domains
4. Set up proper logging
5. Use environment-specific .env files
6. Enable HTTPS

Example production command:
```bash
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
