# Penelope Dataset API Specification

## Base URL
```
http://localhost:8000
```

---

## Endpoints

### 1. List Wovens

Get a paginated list of woven fabrics with optional filtering.

**Endpoint:** `GET /wovens`

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (minimum: 1) |
| `page_size` | integer | No | 50 | Items per page (max: 100) |
| `color_name` | string | No | - | Filter by color name (case-insensitive) |
| `category` | string | No | - | Filter by category (case-insensitive) |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": 1,
      "color_name": ["gray", "yellow"],
      "category": "Jacquard"
    },
    {
      "id": 2,
      "color_name": ["blue", "white"],
      "category": "Plain"
    }
  ],
  "total": 50000,
  "page": 1,
  "page_size": 50,
  "total_pages": 1000
}
```

**Example Requests:**

```bash
# Get first page
curl "http://localhost:8000/wovens"

# Get page 2 with 20 items
curl "http://localhost:8000/wovens?page=2&page_size=20"

# Filter by color
curl "http://localhost:8000/wovens?color_name=red"

# Filter by category
curl "http://localhost:8000/wovens?category=Jacquard"

# Combined filters
curl "http://localhost:8000/wovens?color_name=blue&category=Plain&page=1&page_size=10"
```

---

### 2. Get Woven Detail

Get detailed information about a specific woven fabric, including similar wovens with filenames.

**Endpoint:** `GET /wovens/{id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Woven ID |

**Response:** `200 OK`

```json
{
  "id": 1,
  "filename": "Tei10000.jpg",
  "category": "Jacquard",
  "color_name": ["gray", "yellow"],
  "color_hex": [
    "#e3dfc6",
    "#e9e5cb",
    "#e5e2c8",
    "#d9d4b9"
  ],
  "similarity": [
    {
      "id": 851,
      "score_percent": 92.84339904785156,
      "filename": "Tei10851.jpg"
    },
    {
      "id": 46300,
      "score_percent": 83.25180053710938,
      "filename": "Tei56300.jpg"
    }
  ]
}
```

**Error Response:** `404 Not Found`

```json
{
  "detail": "Woven with ID 999999 not found"
}
```

**Example Requests:**

```bash
# Get woven with ID 1
curl "http://localhost:8000/wovens/1"

# Get woven with ID 12345
curl "http://localhost:8000/wovens/12345"
```

---

### 3. List Pantone Colors

Get a list of all Pantone colors with their hex values.

**Endpoint:** `GET /pantone-colors`

**Query Parameters:** None

**Response:** `200 OK`

```json
{
  "items": [
    {
      "name": "PANTONE Yellow C",
      "hex": "#FEDD00"
    },
    {
      "name": "PANTONE Yellow 012 C",
      "hex": "#FFD700"
    },
    {
      "name": "PANTONE Red C",
      "hex": "#ED2939"
    }
  ],
  "total": 2161
}
```

**Example Request:**

```bash
curl "http://localhost:8000/pantone-colors"
```

---

### 4. Get Pantone Color Detail

Get detailed information about a specific Pantone color, including nearest wovens with filenames.

**Endpoint:** `GET /pantone-colors/detail`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Exact Pantone color name (e.g., "PANTONE Yellow C") |

**Response:** `200 OK`

```json
{
  "name": "PANTONE Yellow C",
  "hex": "#FEDD00",
  "nearest": [
    {
      "id": 23561,
      "filename": "Tei33561.jpg"
    },
    {
      "id": 14397,
      "filename": "Tei24397.jpg"
    },
    {
      "id": 13921,
      "filename": "Tei23921.jpg"
    }
  ]
}
```

**Error Response:** `404 Not Found`

```json
{
  "detail": "Pantone color 'PANTONE Invalid C' not found"
}
```

**Example Requests:**

```bash
# Get Pantone Yellow C
curl "http://localhost:8000/pantone-colors/detail?name=PANTONE Yellow C"

# Get Pantone Red 032 C
curl "http://localhost:8000/pantone-colors/detail?name=PANTONE Red 032 C"

# URL encoded version (if needed)
curl "http://localhost:8000/pantone-colors/detail?name=PANTONE%20Yellow%20C"
```

---

### 5. Root Endpoint

Get API information and available endpoints.

**Endpoint:** `GET /`

**Response:** `200 OK`

```json
{
  "name": "Penelope Dataset API",
  "version": "1.0.0",
  "endpoints": {
    "wovens": {
      "list": "GET /wovens",
      "detail": "GET /wovens/{id}"
    },
    "pantone_colors": {
      "list": "GET /pantone-colors",
      "detail": "GET /pantone-colors/detail?name={name}"
    }
  },
  "docs": "/docs",
  "openapi": "/openapi.json"
}
```

**Example Request:**

```bash
curl "http://localhost:8000/"
```

---

### 6. Health Check

Check API and database health status.

**Endpoint:** `GET /health`

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Example Request:**

```bash
curl "http://localhost:8000/health"
```

---

## Interactive Documentation

### Swagger UI
Access interactive API documentation at:
```
http://localhost:8000/docs
```

### ReDoc
Access alternative API documentation at:
```
http://localhost:8000/redoc
```

### OpenAPI Specification
Download the OpenAPI JSON specification at:
```
http://localhost:8000/openapi.json
```

---

## Common Response Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `404` | Resource not found |
| `422` | Validation error (invalid parameters) |
| `500` | Internal server error |

---

## Data Models

### WovenListItem
```json
{
  "id": integer,
  "color_name": [string],
  "category": string | null
}
```

### WovenDetail
```json
{
  "id": integer,
  "filename": string,
  "category": string | null,
  "color_name": [string],
  "color_hex": [string],
  "similarity": [SimilarWovenItem]
}
```

### SimilarWovenItem
```json
{
  "id": integer,
  "score_percent": float,
  "filename": string
}
```

### PantoneColorListItem
```json
{
  "name": string,
  "hex": string
}
```

### PantoneColorDetail
```json
{
  "name": string,
  "hex": string,
  "nearest": [NearestWovenItem]
}
```

### NearestWovenItem
```json
{
  "id": integer,
  "filename": string
}
```

---

## Notes

- All endpoints return JSON
- Pagination is 1-indexed (first page is `page=1`)
- Maximum page size is 100 items
- Color name filtering is case-insensitive and matches any color in the array
- Category filtering is case-insensitive and matches exact category name
- Pantone color names must be exact matches (case-sensitive)
- All responses include proper CORS headers for cross-origin requests
