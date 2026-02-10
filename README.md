# Property Listings App

A full-stack Django application for browsing property listings by location. Users can search locations, view properties as cards, and open detailed property pages with image galleries.

## Tech Stack

**Backend:**
- Django
- Django REST Framework
- SQLite

**Frontend:**
- Django Templates
- Vanilla JavaScript
- CSS

---

## Project Installation

### 1. Clone Repository
```bash
git clone <repo-url>
cd property_app
```

### 2. Create Virtual Environment (using uv)
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
uv add django djangorestframework pillow
```

### 4. Apply Migrations
```bash
uv run manage.py migrate
```

### 5. Run Development Server
```bash
uv run manage.py runserver
```

Open your browser to: **http://127.0.0.1:8000**

### Seed the Database
```bash
uv run manage.py seed_from_csv --clear
```
This command will populate the database and now you can see results by searching location name

---

## Project Structure

```
property_app/
│
├── core/
│   ├── settings.py
│   └── urls.py
│
├── listings/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py              # DRF API views
│   ├── views_pages.py        # Template views
│   ├── urls.py               # API routes
│   ├── urls_pages.py         # Page routes
│   │
│   ├── templates/
│   │   └── listings/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── property_detail.html
│   │       └── partials/
│   │           ├── navbar.html
│   │           └── footer.html
│   │
│   ├── static/
│   │   └── listings/
│   │       ├── css/
│   │       │   └── styles.css
│   │       └── js/
│   │           ├── home.js
│   │           └── detail.js
│   │
│   └── management/
│       └── commands/
│           └── seed_from_csv.py
│
├── seed_data/
│   ├── locations.csv
│   ├── properties.csv
│   └── images.csv
│
├── seed_media/               # Source images for seeding
├── media/                    # Generated uploaded images
├── db.sqlite3
└── manage.py
```

---

## Data Models

### Location
- `name` (unique)
- `slug` (auto-generated)

### Property
- `external_id` (auto-generated)
- `slug` (auto-generated from title + id)
- `location` (ForeignKey to Location)
- `property_name`
- `country`
- `address`
- `title`
- `description`
- `created_at`

### PropertyImage
- `property` (ForeignKey to Property)
- `image` (ImageField)
- `is_primary` (boolean)
- `alt_text`
- `created_at`

**Constraint:** Only one primary image per property

---

## API Endpoints

### Location Autocomplete
```http
GET /api/locations/autocomplete/?q=new
```

**Response:**
```json
{
  "results": [
    { "name": "New York", "slug": "new-york" }
  ]
}
```

### Property Search
```http
GET /api/properties/?location=New York&page=1
```

**Response:**
```json
{
  "count": 20,
  "next": "http://example.com/api/properties/?location=New+York&page=2",
  "previous": null,
  "results": [
    {
      "id": 12,
      "title": "Cozy Apartment",
      "slug": "cozy-apartment-12",
      "location_slug": "new-york",
      "address": "123 Main St",
      "country": "USA",
      "primary_image_url": "/media/properties/image.jpg"
    }
  ]
}
```

### Property Detail
```http
GET /api/properties/<id>/
```

**Returns:**
- Full property information
- All associated images

---

## Page Routes

### Home Page
```
/
```
**Features:**
- Location search input with autocomplete
- Property card grid
- Pagination controls

### Property Detail Page
```
/properties/<location-slug>/<property-slug>/
```

**Example:**
```
/properties/new-york/cozy-apartment-12/
```

---

### CSV File Formats

**locations.csv:**
```csv
name
New York
Barcelona
Dhaka
```

**properties.csv:**
```csv
external_id,location_name,property_name,country,address,title,description
PROP-0001,New York,Central Flat,USA,5th Ave,Cozy Apartment,Near park
```

**images.csv:**
```csv
property_external_id,file_path,is_primary,alt_text
PROP-0001,seed_media/img1.jpg,true,Living room
PROP-0001,seed_media/img2.jpg,false,Bedroom
```


## Static Files & Media Configuration

**Static files location:**
```
listings/static/listings/
```

**Media files location:**
```
media/
```

**Add to `settings.py`:**
```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

---

### Search Behavior
- Autocomplete triggers after typing 3 characters
- Case-insensitive location search
- Press Enter or click a suggestion to search
- Results paginated (8 per page)

---

### Some Screen Shots
**Home Page**
<img width="1199" height="633" alt="home" src="https://github.com/user-attachments/assets/9d70e622-f62e-4a4b-b465-6230206021f8" />

**Search Suggestion**
<img width="1199" height="633" alt="suggestion" src="https://github.com/user-attachments/assets/1a2cafac-d04a-4151-b9bb-c488afd6ebf9" />

**Property Lists**
<img width="1228" height="912" alt="property" src="https://github.com/user-attachments/assets/354e7a53-8c7f-4049-b480-c175a87f44da" />

**Property Detail**
<img width="1228" height="912" alt="detail" src="https://github.com/user-attachments/assets/e97ebbe0-54fd-4f9e-ad27-323c47682694" />
