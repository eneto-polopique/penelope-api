# Penelope Dataset API Specification v2

## Overview

This API provides access to the Penelope woven fabrics dataset, which organizes data into four main entities:

- **Wovens**: Base fabric specifications (draw patterns, references, compositions)
- **Variants**: Color/visual variations of each woven (each woven can have multiple variants)
- **Stock**: Inventory records for specific variants
- **Pantone Colors**: Color matching between Pantone standards and variants

### Key Concepts

- A **woven** represents a unique fabric design with technical specifications
- Each woven can have multiple **variants** (different color combinations of the same design)
- Each variant can have multiple **stock** entries (different inventory lots)
- **Pantone colors** link to the variants that most closely match their color

---

## Base URL
```
http://localhost:8000
```

---

## Endpoints

### 1. List Wovens

**Purpose:** Browse all woven fabric designs with a quick overview of their variants.

**Endpoint:** `GET /wovens`

**Use Case:** Main catalog view showing all fabric designs. Each woven shows how many color variants exist and displays the first variant's thumbnail for quick visual reference.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (minimum: 1) |
| `page_size` | integer | No | 50 | Items per page (max: 100) |
| `reference` | string | No | - | Filter by reference code (partial match, case-insensitive) |
| `draw` | string | No | - | Filter by draw pattern (partial match, case-insensitive) |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": 3372,
      "reference": "4612",
      "draw": "W339.1A",
      "finishing": null,
      "variant_count": 3,
      "variants": [
        {
          "variant_id": 1,
          "variant_ref": "000",
          "thumbnail": "thumb_eyJyZWZlcmVuY2UiOiAiNDYxMiIsICJkcmF3IjogIlczMzkuMUEiLCAidmFyaWFudF9yZWYiOiAiMDAwIn0.jpg"
        },
        {
          "variant_id": 2,
          "variant_ref": "001",
          "thumbnail": "thumb_xyz123.jpg"
        },
        {
          "variant_id": 3,
          "variant_ref": "002",
          "thumbnail": "thumb_abc456.jpg"
        }
      ]
    }
  ],
  "total": 15000,
  "page": 1,
  "page_size": 50,
  "total_pages": 300
}
```

**Response Fields Explained:**

- `id`: Unique woven identifier
- `reference`: Product reference code (e.g., "4612")
- `draw`: Draw pattern code (e.g., "W339.1A")
- `finishing`: Finishing process name (can be null)
- `variant_count`: Total number of color variants for this woven
- `variants`: Array of all variants with their IDs, refs, and thumbnails
  - `variant_id`: Database ID of the variant (use this to navigate to variant detail)
  - `variant_ref`: Variant reference code (e.g., "000", "001")
  - `thumbnail`: Thumbnail image filename/path

**Example Requests:**

```bash
# Get first page of all wovens
curl "http://localhost:8000/wovens"

# Get page 2 with 20 items per page
curl "http://localhost:8000/wovens?page=2&page_size=20"

# Search by reference code
curl "http://localhost:8000/wovens?reference=4612"

# Search by draw pattern
curl "http://localhost:8000/wovens?draw=W339"

# Combined search
curl "http://localhost:8000/wovens?reference=46&draw=W3"
```

**UI Flow:**
1. Display woven cards showing reference, draw, and first variant thumbnail
2. Show variant count badge (e.g., "3 variants")
3. When user clicks a woven card, navigate to the first variant's detail page using `variants[0].variant_id`

---

### 2. List Variants

**Purpose:** Browse all fabric variants with visual information.

**Endpoint:** `GET /variants`

**Use Case:** Search and filter variants by visual characteristics (colors, categories). This is your main search interface for finding fabrics by appearance.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (minimum: 1) |
| `page_size` | integer | No | 50 | Items per page (max: 100) |
| `color_name` | string[] | No | - | Filter by color name(s) - must have ALL specified colors (case-insensitive) |
| `category` | string | No | - | Filter by category (case-insensitive, partial match) |
| `reference` | string | No | - | Filter by woven reference (partial match) |
| `draw` | string | No | - | Filter by draw pattern (partial match) |
| `in_stock` | boolean | No | - | Filter by stock availability (true = has stock, false = no stock) |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": 1,
      "variant_ref": "000",
      "reference": "4612",
      "draw": "W339.1A",
      "thumbnail": "thumb_eyJyZWZlcmVuY2UiOiAiNDYxMiIsICJkcmF3IjogIlczMzkuMUEiLCAidmFyaWFudF9yZWYiOiAiMDAwIn0.jpg",
      "color_hex": ["#f7f8e9", "#f7faec", "#f9fbec", "#f8fbee", "#f8faeb"]
    }
  ],
  "total": 25000,
  "page": 1,
  "page_size": 50,
  "total_pages": 500
}
```

**Response Fields Explained:**

- `id`: Unique variant identifier (use this to navigate to detail page)
- `variant_ref`: Variant reference code within the woven (e.g., "000", "001", "002")
- `reference`: Parent woven's product reference
- `draw`: Parent woven's draw pattern
- `thumbnail`: Thumbnail image filename/path
- `color_hex`: Array of dominant hex colors in the variant

**Example Requests:**

```bash
# Get all variants
curl "http://localhost:8000/variants"

# Find variants with white color
curl "http://localhost:8000/variants?color_name=white"

# Find variants with BOTH white AND blue
curl "http://localhost:8000/variants?color_name=white&color_name=blue"

# Find variants in a specific category
curl "http://localhost:8000/variants?category=Lisos"

# Find only variants that have stock
curl "http://localhost:8000/variants?in_stock=true"

# Combined search: white variants with stock
curl "http://localhost:8000/variants?color_name=white&in_stock=true"

# Search by parent woven reference
curl "http://localhost:8000/variants?reference=4612"
```

**UI Flow:**
1. Display variant cards with thumbnail and color swatches
2. Show reference and draw for context
3. When user clicks a variant, navigate to `/variants/{id}` for full details

---

### 3. Get Variant Detail

**Purpose:** View complete information about a specific variant, including similar variants, yarns, and stock.

**Endpoint:** `GET /variants/{id}`

**Use Case:** Detail page showing everything about a variant - its colors, similar options, yarn composition, parent woven info, and available stock.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Variant ID (from list endpoints) |

**Response:** `200 OK`

```json
{
  "id": 1,
  "variant_ref": "000",
  "filename": null,
  "thumbnail": "thumb_eyJyZWZlcmVuY2UiOiAiNDYxMiIsICJkcmF3IjogIlczMzkuMUEiLCAidmFyaWFudF9yZWYiOiAiMDAwIn0.jpg",
  "category": "Lisos e Falsos Lisos",
  "color_name": ["white", "orange", "gray"],
  "color_hex": ["#f7f8e9", "#f7faec", "#f9fbec", "#f8fbee", "#f8faeb"],
  "similarity": [
    {
      "id": 153896,
      "score_percent": 89.62240600585938,
      "variant_ref": "001",
      "reference": "5123",
      "thumbnail": "thumb_xyz.jpg"
    }
  ],
  "woven": {
    "id": 3372,
    "reference": "4612",
    "draw": "W339.1A",
    "composition": "90.4%CV 9.6%CO",
    "date": "2013-06-18",
    "finishing": null
  },
  "yarns": [
    {
      "name": "00000",
      "ne": "50",
      "composition": "100%CV",
      "colors": "#FFFFFF"
    },
    {
      "name": "00000",
      "ne": "40/2",
      "composition": "100%CO",
      "colors": "#FAEBDC"
    }
  ],
  "stock": [
    {
      "id": 1,
      "description": "TS PR239150",
      "quantity": 36.9,
      "perfect_match": false
    }
  ]
}
```

**Response Fields Explained:**

**Variant Information:**
- `id`: Unique variant identifier
- `variant_ref`: Variant code (e.g., "000")
- `filename`: Original image filename (can be null)
- `thumbnail`: Thumbnail image path
- `category`: Visual category classification
- `color_name`: Array of color names in natural language
- `color_hex`: Array of hex color codes

**Similarity Matches:**
- `similarity`: Array of visually similar variants, ordered by similarity score
  - `id`: Similar variant's ID
  - `score_percent`: Similarity score (0-100, higher = more similar)
  - `variant_ref`: Similar variant's reference code
  - `reference`: Similar variant's woven reference
  - `thumbnail`: Similar variant's thumbnail

**Parent Woven Information:**
- `woven`: Technical specifications of the parent woven
  - `id`: Woven ID
  - `reference`: Product reference
  - `draw`: Draw pattern
  - `composition`: Fiber composition (e.g., "90.4%CV 9.6%CO")
  - `date`: Production date (ISO format)
  - `finishing`: Finishing process

**Yarn Details:**
- `yarns`: Array of yarns used in this variant (filtered by variant_ref)
  - `name`: Yarn identifier
  - `ne`: Yarn count (thickness)
  - `composition`: Fiber composition
  - `colors`: Hex color of the yarn

**Stock Information:**
- `stock`: Array of available stock entries
  - `id`: Stock record ID
  - `description`: Stock lot description
  - `quantity`: Available quantity (meters/yards)
  - `perfect_match`: Whether this is a perfect color match

**Error Response:** `404 Not Found`

```json
{
  "detail": "Variant with ID 999999 not found"
}
```

**Example Requests:**

```bash
# Get variant details
curl "http://localhost:8000/variants/1"

# Get variant 153896 (from similarity results)
curl "http://localhost:8000/variants/153896"
```

**UI Flow:**
1. Display large thumbnail/image at top
2. Show color swatches from `color_hex`
3. Display parent woven specs (reference, draw, composition)
4. Show yarn composition table
5. Display "Similar Variants" carousel from `similarity` array
6. Show stock availability table if `stock` array has items
7. Allow navigation to similar variants by clicking thumbnails

---

### 4. List Stock

**Purpose:** View and search all inventory records.

**Endpoint:** `GET /stock`

**Use Case:** Inventory management - find available stock by variant, quantity, or match quality.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (minimum: 1) |
| `page_size` | integer | No | 50 | Items per page (max: 100) |
| `variant_id` | integer | No | - | Filter by specific variant ID |
| `perfect_match` | boolean | No | - | Filter by perfect match status |
| `min_quantity` | float | No | - | Minimum stock quantity |
| `description` | string | No | - | Filter by description (partial match, case-insensitive) |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": 1,
      "variant_id": 175164,
      "description": "TS PR239150",
      "quantity": 36.9,
      "perfect_match": false,
      "variant": {
        "id": 175164,
        "variant_ref": "002",
        "reference": "TC BO497",
        "category": "Xadrez",
        "thumbnail": "thumb_abc.jpg"
      }
    }
  ],
  "total": 5000,
  "page": 1,
  "page_size": 50,
  "total_pages": 100
}
```

**Response Fields Explained:**

- `id`: Stock record ID
- `variant_id`: ID of the variant this stock belongs to
- `description`: Stock lot description/identifier
- `quantity`: Available quantity (units depend on your system)
- `perfect_match`: True if this is an exact color match
- `variant`: Summary of the variant this stock belongs to
  - `id`: Variant ID (clickable to navigate)
  - `variant_ref`: Variant reference code
  - `reference`: Parent woven reference
  - `category`: Visual category
  - `thumbnail`: Variant thumbnail

**Example Requests:**

```bash
# Get all stock
curl "http://localhost:8000/stock"

# Get stock for a specific variant
curl "http://localhost:8000/stock?variant_id=175164"

# Find only perfect matches
curl "http://localhost:8000/stock?perfect_match=true"

# Find stock with at least 50 units
curl "http://localhost:8000/stock?min_quantity=50"

# Search by description
curl "http://localhost:8000/stock?description=PR239"

# Combined: perfect matches with 100+ quantity
curl "http://localhost:8000/stock?perfect_match=true&min_quantity=100"
```

**UI Flow:**
1. Display stock table with quantity, description, and variant info
2. Show variant thumbnail for visual reference
3. Highlight perfect matches
4. Allow click-through to variant detail page

---

### 5. Get Available Filters

**Purpose:** Get metadata about available filter values to populate search forms and dropdowns.

#### 5.1. Get Available Colors

**Endpoint:** `GET /filters/colors`

**Use Case:** Populate color filter dropdowns with valid color names.

**Query Parameters:** None

**Response:** `200 OK`

```json
[
  "beige",
  "black",
  "blue",
  "brown",
  "cream",
  "gold",
  "gray",
  "green",
  "grey",
  "maroon",
  "navy",
  "olive",
  "orange",
  "pink",
  "purple",
  "red",
  "silver",
  "teal",
  "turquoise",
  "white",
  "yellow"
]
```

**Example Request:**

```bash
curl "http://localhost:8000/filters/colors"
```

---

#### 5.2. Get Available Categories

**Endpoint:** `GET /filters/categories`

**Use Case:** Populate category filter dropdowns with valid categories.

**Query Parameters:** None

**Response:** `200 OK`

```json
[
  "Bordados",
  "Estampados",
  "Fantasia",
  "Jacquard",
  "Lisos e Falsos Lisos",
  "Maquinetas",
  "Riscados",
  "Xadrez"
]
```

**Example Request:**

```bash
curl "http://localhost:8000/filters/categories"
```

---

#### 5.3. Get Available References

**Endpoint:** `GET /filters/references`

**Use Case:** Get all unique reference codes from the database for autocomplete or filtering.

**Query Parameters:** None

**Response:** `200 OK`

```json
[
  "4612",
  "4856",
  "5123",
  "TC BO497",
  "..."
]
```

**Example Request:**

```bash
curl "http://localhost:8000/filters/references"
```

**Note:** This endpoint queries the database and returns all distinct reference codes currently in the system.

---

#### 5.4. Get Available Draw Patterns

**Endpoint:** `GET /filters/draws`

**Use Case:** Get all unique draw patterns from the database for autocomplete or filtering.

**Query Parameters:** None

**Response:** `200 OK`

```json
[
  "W339.1A",
  "W340.2B",
  "W341.3C",
  "..."
]
```

**Example Request:**

```bash
curl "http://localhost:8000/filters/draws"
```

**Note:** This endpoint queries the database and returns all distinct draw patterns currently in the system.

---

### 6. List Pantone Colors

**Purpose:** Browse all Pantone color standards in the database.

**Endpoint:** `GET /pantone-colors`

**Use Case:** Color reference catalog - see all available Pantone colors and how many fabric variants match each.

**Query Parameters:** None

**Response:** `200 OK`

```json
{
  "items": [
    {
      "name": "PANTONE Yellow C",
      "hex": "#FEDD00",
      "nearest_count": 25
    },
    {
      "name": "PANTONE Yellow 012 C",
      "hex": "#FFD700",
      "nearest_count": 18
    }
  ],
  "total": 2161
}
```

**Response Fields Explained:**

- `name`: Official Pantone color name
- `hex`: Hex color code
- `nearest_count`: Number of fabric variants that match this Pantone color

**Example Request:**

```bash
curl "http://localhost:8000/pantone-colors"
```

**UI Flow:**
1. Display Pantone color grid with color swatches
2. Show color name and hex code
3. Display match count badge
4. Click color to see matching variants

---

### 7. Get Pantone Color Detail

**Purpose:** Find fabric variants that match a specific Pantone color.

**Endpoint:** `GET /pantone-colors/detail`

**Use Case:** "Show me all fabrics that match Pantone Yellow C" - useful for color-matching projects.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Exact Pantone color name (case-sensitive, e.g., "PANTONE Yellow C") |

**Response:** `200 OK`

```json
{
  "name": "PANTONE Yellow C",
  "hex": "#FEDD00",
  "nearest": [
    {
      "id": 23561,
      "variant_ref": "002",
      "reference": "TC BO497",
      "category": "Xadrez",
      "thumbnail": "thumb_abc.jpg",
      "has_stock": true
    },
    {
      "id": 14397,
      "variant_ref": "001",
      "reference": "4856",
      "category": "Jacquard",
      "thumbnail": "thumb_def.jpg",
      "has_stock": false
    }
  ]
}
```

**Response Fields Explained:**

- `name`: Pantone color name
- `hex`: Hex color code
- `nearest`: Array of matching variants, ordered by color similarity (best matches first)
  - `id`: Variant ID (use for navigation)
  - `variant_ref`: Variant reference code
  - `reference`: Parent woven reference
  - `category`: Visual category
  - `thumbnail`: Variant thumbnail
  - `has_stock`: Whether this variant has any stock available

**Error Response:** `404 Not Found`

```json
{
  "detail": "Pantone color 'PANTONE Invalid C' not found"
}
```

**Example Requests:**

```bash
# Get matches for Pantone Yellow C
curl "http://localhost:8000/pantone-colors/detail?name=PANTONE Yellow C"

# URL encoded (if needed)
curl "http://localhost:8000/pantone-colors/detail?name=PANTONE%20Yellow%20C"

# Get matches for Pantone Red 032 C
curl "http://localhost:8000/pantone-colors/detail?name=PANTONE Red 032 C"
```

**UI Flow:**
1. Display Pantone color swatch at top
2. Show grid of matching variant thumbnails
3. Indicate stock availability with badge/icon
4. Click variant to navigate to detail page
5. Sort by best match (already ordered in response)

---

### 8. Root Endpoint

**Purpose:** API discovery and version information.

**Endpoint:** `GET /`

**Response:** `200 OK`

```json
{
  "name": "Penelope Dataset API",
  "version": "2.0.0",
  "endpoints": {
    "wovens": {
      "list": "GET /wovens"
    },
    "variants": {
      "list": "GET /variants",
      "detail": "GET /variants/{id}"
    },
    "stock": {
      "list": "GET /stock"
    },
    "pantone_colors": {
      "list": "GET /pantone-colors",
      "detail": "GET /pantone-colors/detail?name={name}"
    },
    "filters": {
      "colors": "GET /filters/colors",
      "categories": "GET /filters/categories",
      "references": "GET /filters/references",
      "draws": "GET /filters/draws"
    }
  },
  "docs": "/docs",
  "openapi": "/openapi.json"
}
```

---

### 9. Health Check

**Purpose:** Monitor API and database status.

**Endpoint:** `GET /health`

**Use Case:** Health monitoring, uptime checks, deployment verification.

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "database": "connected",
  "tables": {
    "woven_info": 15000,
    "variant_info": 25000,
    "stock_info": 5000,
    "pantone_colors": 2161
  }
}
```

**Response Fields Explained:**

- `status`: Overall API status ("healthy" or "unhealthy")
- `database`: Database connection status ("connected" or "disconnected")
- `tables`: Record counts for each main table

---

## Common Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `200` | OK | Request successful |
| `404` | Not Found | Resource doesn't exist (wrong ID or Pantone name) |
| `422` | Validation Error | Invalid parameters (wrong type, out of range, etc.) |
| `500` | Internal Server Error | Something went wrong on the server |

---

## Common Patterns

### Pagination

All list endpoints support pagination with consistent parameters:

- `page`: Current page (1-indexed, minimum: 1)
- `page_size`: Items per page (default: 50, maximum: 100)

Response includes:
- `items`: Array of results
- `total`: Total number of matching items
- `page`: Current page number
- `page_size`: Items per page
- `total_pages`: Total number of pages

### Filtering

Filters are case-insensitive and support partial matching unless otherwise specified:

- Text fields (reference, draw, description): Partial match
- Color names: Must have ALL specified colors (AND condition)
- Categories: Partial match
- Booleans (in_stock, perfect_match): Exact match
- Pantone names: Exact match (case-sensitive)

### Navigation Flow

**Recommended user flow:**

1. **Browse wovens** → `GET /wovens`
   - Click woven → Navigate to first variant
   
2. **View variant detail** → `GET /variants/{first_variant_id}`
   - See similar variants → Click thumbnail → Navigate to similar variant
   - See other variants of same woven → Navigate to sibling variant
   
3. **Search by color** → `GET /variants?color_name=white`
   - Click result → Navigate to variant detail
   
4. **Match Pantone** → `GET /pantone-colors/detail?name=PANTONE Yellow C`
   - Click matching variant → Navigate to variant detail

---

## Interactive Documentation

For hands-on API exploration:

- **Swagger UI:** `http://localhost:8000/docs` (interactive testing)
- **ReDoc:** `http://localhost:8000/redoc` (clean documentation)
- **OpenAPI JSON:** `http://localhost:8000/openapi.json` (machine-readable spec)

---

## Technical Notes

### Data Types

- **Integer IDs**: All entity IDs (woven_id, variant_id, stock_id)
- **Float**: Stock quantities (can have decimals)
- **String Arrays**: color_name, color_hex, variants
- **Date Strings**: ISO 8601 format (YYYY-MM-DD)
- **Hex Colors**: 7 characters including # (e.g., "#FEDD00")

### CORS

All endpoints include CORS headers for cross-origin requests.

### Response Format

All responses are JSON with UTF-8 encoding.

### Yarn Filtering

In variant detail endpoint, yarns are automatically filtered to show only yarns belonging to that variant's `variant_ref`. This is done in the backend using the `yarns` JSONB field in `woven_info` table.

### Stock Availability

`has_stock` flag indicates whether ANY stock records exist for a variant, regardless of quantity. Use `min_quantity` filter on `/stock` endpoint for quantity-based filtering.