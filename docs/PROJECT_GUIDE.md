# AdVance Real Estate Portal - Complete Project Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [User Management](#user-management)
5. [User Interface (UI)](#user-interface-ui)
6. [Setup & Installation](#setup--installation)
7. [Admin Interface Guide](#admin-interface-guide)
8. [Development Workflow](#development-workflow)
9. [Project Structure](#project-structure)
10. [Common Tasks](#common-tasks)

---

## Project Overview

**AdVance Real Estate Portal** is a Django-based web application for managing and displaying property listings. The system allows real estate professionals (like Madison and her assistant) to manage property listings through an admin interface, while visitors can browse available properties on the public-facing website.

### Key Features
- **Database-based user authentication** - Secure email/password login system
- **Admin-managed user accounts** - Site administrators create and manage all user credentials
- **Property listing management** - Full CRUD operations for property listings
- **Lookup data management** - Statuses, property types, neighborhoods, price buckets
- **Public listing display** - Responsive grid layout showing available properties
- **Search logging** - Tracks user searches for analytics
- **Photo management** - Support for property images

---

## Architecture

### Technology Stack
- **Backend Framework:** Django 5.2.7
- **Database:** SQLite3 (development), can be migrated to PostgreSQL/MySQL for production
- **Frontend:** Django Templates with HTML/CSS
- **Authentication:** Django's built-in authentication with custom User model
- **Python Version:** 3.13.4+

### Application Structure
```
realestate_portal/          # Django project root
├── manage.py               # Django management script
├── db.sqlite3             # SQLite database (not in git)
├── listings/              # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin interface configuration
│   ├── forms.py           # Form definitions
│   ├── migrations/        # Database migrations
│   └── fixtures/          # Initial data fixtures
├── realestate_portal/     # Project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI configuration
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── accounts/          # Authentication templates
│   └── listings/          # Listing templates
└── static/                # Static files (CSS, JS, images)
    └── css/
        └── site.css       # Main stylesheet
```

---

## Database Schema

### Entity Relationship Overview

The database follows a normalized schema with the following main entities:

#### Core Tables

**User**
- Primary key: `User_ID`
- Fields: `Email` (unique), `Password_Hash`, `Firstname`, `Lastname`
- Purpose: Stores all user accounts (real estate agents, admins, etc.)

**Listing**
- Primary key: `Listing_ID`
- Foreign keys: `Created_by` → User, `Property_Type_ID`, `Neighborhood_ID`, `Pricebucket_ID`, `Status_ID`
- Fields: Address, Price, Description, Bedrooms, Bathrooms, Square Footage, Status, Visibility flags
- Purpose: Main property listing data

#### Lookup Tables

**Status** - Listing statuses (Active, Pending, Sold)
**PropertyType** - Property categories (House, Apartment, Condo, Townhouse, etc.)
**Neighborhood** - Geographic areas (Downtown, Midtown, Bellevue, Papillion, etc.)
**Pricebucket** - Price ranges ($0-$100k, $100k-$200k, etc.)

#### Supporting Tables

**Photo** - Property images linked to listings
**SearchLog** - Tracks user search queries for analytics
**OmahaResource** - Optional resources page content

### Complete Schema Details

#### User Table
```sql
User_ID (PK, INTEGER)
Email (TEXT, UNIQUE, NOT NULL)
Password_Hash (TEXT, NOT NULL)
Firstname (TEXT, NOT NULL)
Lastname (TEXT, NOT NULL)
is_active (BOOLEAN, default=True)
is_staff (BOOLEAN, default=False)
is_superuser (BOOLEAN, default=False)
date_joined (DATETIME, auto-set)
```

#### Listing Table
```sql
Listing_ID (PK, INTEGER)
Created_by (FK → User.User_ID, NOT NULL)
Property_Type_ID (FK → Property_Type.Property_Type_ID, NOT NULL)
Neighborhood_ID (FK → Neighborhood.Neighborhood_ID, NOT NULL)
Pricebucket_ID (FK → Pricebucket.Pricebucket_ID, nullable)
Address (TEXT, NOT NULL)
Price (NUMERIC, NOT NULL)
Description (TEXT, nullable)
Status_ID (FK → Status.Status_ID, nullable)
Is_Visible (INTEGER/BOOLEAN, default=1)
Is_Featured (INTEGER/BOOLEAN, default=0)
Bedrooms (INTEGER, nullable)
Bathrooms (REAL, nullable)
Square_Footage (INTEGER, nullable)
Status (TEXT, CHECK IN ('Available','Pending','Sold'), nullable)
listed_date (DATETIME, auto-set)
```

#### Lookup Tables
- **Status**: `Status_ID` (PK), `Name`
- **PropertyType**: `Property_Type_ID` (PK), `Name`
- **Neighborhood**: `Neighborhood_ID` (PK), `Name`
- **Pricebucket**: `Pricebucket_ID` (PK), `Range`

---

## User Management

### Overview
**All user accounts are managed exclusively through the Django Admin Interface.** There is no public user registration form. This ensures controlled access and proper credential management.

### User Management Flow

#### 1. Creating New Users (Admin Only)

**Step-by-Step:**
1. Log in to Django Admin: `http://127.0.0.1:8000/admin/`
2. Navigate to **Listings** → **Users**
3. Click **"Add User"** button
4. Fill in the form:
   - **Email:** User's email address (this is their username)
   - **First name:** User's first name
   - **Last name:** User's last name
   - **Password:** Set initial password (can be changed later)
   - **Password confirmation:** Re-enter password
5. Set permissions:
   - **Active:** Check to enable the account
   - **Staff status:** Check if user needs admin access
   - **Superuser status:** Check for full admin privileges
6. Click **"Save"**

#### 2. Sharing Credentials

After creating a user account:
- **Email address** = Username for login
- **Password** = The password you set in admin
- Share these credentials securely with the user (Madison, assistant, etc.)

#### 3. User Login

Users log in at: `http://127.0.0.1:8000/login/`
- Enter email address
- Enter password
- Click "Login"
- Redirected to homepage after successful login

#### 4. Managing Existing Users

**Edit User:**
- Go to **Listings** → **Users**
- Click on the user's email
- Modify fields as needed
- Click **"Save"**

**Change Password:**
- Edit user → Scroll to password field
- Enter new password and confirmation
- Save

**Deactivate User:**
- Edit user → Uncheck **"Active"** checkbox
- Save

**Delete User:**
- Go to user list → Select user → Choose **"Delete selected users"** → Confirm

### User Roles

- **Regular Users:** Can log in and view listings (if needed for future features)
- **Staff Users:** Can access Django admin interface
- **Superusers:** Full admin access, can manage all data

---

## User Interface (UI)

### Public Pages

#### Homepage (`/` or `/home/`)
- **URL:** `http://127.0.0.1:8000/`
- **Purpose:** Displays all visible property listings
- **Layout:** Responsive grid of listing cards
- **Features:**
  - Shows listing address (as title)
  - Price display
  - Property description (truncated to 180 characters)
  - Listed date
  - Only shows listings where `is_visible = True`

#### Login Page (`/login/`)
- **URL:** `http://127.0.0.1:8000/login/`
- **Purpose:** User authentication
- **Layout:** Two-column layout with login form on left, promotional content on right
- **Fields:**
  - Email address (required)
  - Password (required)
- **Features:**
  - Email validation
  - Error messages for invalid credentials
  - Link to contact administrator for account requests
  - Redirects to homepage after successful login

### Navigation

**Header Navigation:**
- **When Not Logged In:**
  - "AdVance Real Estate" branding (left)
  - "Login" link (right)

- **When Logged In:**
  - "AdVance Real Estate" branding (left)
  - "Welcome, [User's Full Name]!" message
  - "Logout" button (POST form for security)

### Design Elements

- **Branding:** "AdVance Real Estate" in header
- **Typography:** Italiana font family for branding
- **Colors:** Defined in `static/css/site.css`
- **Responsive:** Grid layout adapts to screen size
- **Cards:** Each listing displayed in a card with consistent styling

---

## Setup & Installation

### Prerequisites
- Python 3.13+ installed
- Git installed
- Virtual environment support (venv)

### Step-by-Step Setup

#### 1. Clone Repository
```bash
git clone https://github.com/tbrzezowsky/ISQA8210-Team3.git
cd ISQA8210-Team3
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Apply Database Migrations
```bash
python manage.py migrate
```
This creates all database tables based on the models.

#### 5. Create Superuser Account
```bash
python manage.py createsuperuser
```
Follow prompts:
- Email: (your admin email)
- First name: (your first name)
- Last name: (your last name)
- Password: (create a secure password)
- Password confirmation: (re-enter)

**Note:** Use email as the username when prompted.

#### 6. Load Initial Data (Fixtures)
```bash
# Load all lookup data
python manage.py loaddata listings/fixtures/statuses.json
python manage.py loaddata listings/fixtures/property_types.json
python manage.py loaddata listings/fixtures/neighborhoods.json
python manage.py loaddata listings/fixtures/pricebuckets.json

# Load sample listings
python manage.py loaddata listings/fixtures/listings.json
```

Or load all at once:
```bash
python manage.py loaddata listings/fixtures/*.json
```

#### 7. Run Development Server
```bash
python manage.py runserver
```

#### 8. Access the Application
- **Public Site:** http://127.0.0.1:8000/
- **Admin Interface:** http://127.0.0.1:8000/admin/
- **Login:** http://127.0.0.1:8000/login/

---

## Admin Interface Guide

### Accessing Admin
1. Navigate to: `http://127.0.0.1:8000/admin/`
2. Log in with superuser credentials

### Available Sections

#### Users (`/admin/listings/user/`)
- **View:** List of all users with email, name, staff status
- **Add:** Create new user accounts
- **Edit:** Modify user information, change passwords
- **Filters:** By staff status, superuser status, active status, date joined
- **Search:** By email, first name, last name

#### Listings (`/admin/listings/listing/`)
- **View:** All property listings with key details
- **Add:** Create new property listing
- **Edit:** Modify listing details
- **Filters:** By property type, neighborhood, status, visibility, featured status
- **Search:** By address, description

**Required Fields When Creating Listing:**
- Address
- Price
- Created by (select a user)
- Property Type (select from dropdown)
- Neighborhood (select from dropdown)

**Optional Fields:**
- Description
- Bedrooms, Bathrooms, Square Footage
- Price Bucket
- Status and Status ID
- Featured flag
- Visibility flag

#### Lookup Data Management

**Statuses** (`/admin/listings/status/`)
- Manage listing statuses (Active, Pending, Sold)
- Add custom statuses if needed

**Property Types** (`/admin/listings/propertytype/`)
- Manage property categories (House, Apartment, Condo, etc.)
- Add new property types

**Neighborhoods** (`/admin/listings/neighborhood/`)
- Manage geographic areas
- Add new neighborhoods

**Price Buckets** (`/admin/listings/pricebucket/`)
- Manage price ranges
- Add new price ranges

#### Other Models

**Photos** (`/admin/listings/photo/`)
- Manage property images
- Link photos to listings
- Set display order

**Search Logs** (`/admin/listings/searchlog/`)
- View search history
- Analytics data (read-only recommended)

**Omaha Resources** (`/admin/listings/omaharesource/`)
- Manage resources page content
- Optional feature

### Common Admin Tasks

#### Creating a New Property Listing
1. Go to **Listings** → **Listings** → **Add Listing**
2. Fill in required fields:
   - Address: Full property address
   - Price: Property price (numeric)
   - Created by: Select user who created listing
   - Property Type: Select from dropdown
   - Neighborhood: Select from dropdown
3. Fill optional fields:
   - Description: Property details
   - Bedrooms, Bathrooms, Square Footage
   - Status: Available/Pending/Sold
   - Featured: Check if should be highlighted
   - Visible: Check to show on public site
4. Click **"Save"**

#### Making a Listing Visible/Invisible
- Edit listing → Check/Uncheck **"Is visible"** → Save

#### Featuring a Listing
- Edit listing → Check **"Is featured"** → Save

#### Bulk Operations
- Select multiple items using checkboxes
- Choose action from dropdown (delete, etc.)
- Click **"Go"**

---

## Development Workflow

### Branch Strategy
- **main:** Production-ready code
- **feature branches:** New features (e.g., `database-login`)

### Making Changes

#### 1. Create Feature Branch
```bash
git checkout main
git pull origin main
git checkout -b feature-name
```

#### 2. Make Changes
- Edit files as needed
- Test locally
- Run migrations if model changes: `python manage.py makemigrations`

#### 3. Commit Changes
```bash
git add .
git commit -m "Descriptive commit message"
```

#### 4. Push to Remote
```bash
git push origin feature-name
```

#### 5. Create Pull Request
- Go to GitHub repository
- Click "New Pull Request"
- Select your branch
- Add description
- Request review

### Database Changes

**When modifying models:**
1. Edit `listings/models.py`
2. Create migration: `python manage.py makemigrations`
3. Review migration file in `listings/migrations/`
4. Apply migration: `python manage.py migrate`
5. Test changes
6. Commit migration files with code changes

**Important:** Always commit migration files with model changes.

### Testing Checklist

Before committing:
- [ ] Run `python manage.py check` (no errors)
- [ ] Test admin interface functionality
- [ ] Test user login/logout
- [ ] Verify listings display correctly
- [ ] Check for any console errors
- [ ] Test on different screen sizes (responsive)

---

## Project Structure

### Key Files Explained

**`manage.py`**
- Django management script
- Used for running commands: `python manage.py [command]`

**`realestate_portal/settings.py`**
- Django project settings
- Database configuration
- Installed apps
- Authentication settings
- Static files configuration

**`listings/models.py`**
- All database models
- Defines data structure
- Relationships between models

**`listings/views.py`**
- View functions
- Handles HTTP requests
- Returns responses

**`listings/urls.py`**
- URL routing for listings app
- Maps URLs to views

**`listings/admin.py`**
- Admin interface configuration
- Customizes how models appear in admin

**`listings/forms.py`**
- Form definitions
- Currently contains CustomLoginForm

**`templates/base.html`**
- Base template
- Contains header, navigation, footer structure
- Other templates extend this

**`templates/listings/home.html`**
- Homepage template
- Displays listing grid

**`templates/accounts/login.html`**
- Login page template

**`static/css/site.css`**
- Main stylesheet
- All CSS styling

**`listings/fixtures/`**
- JSON files with initial data
- Loaded using `loaddata` command

**`listings/migrations/`**
- Database migration files
- Tracks database schema changes
- Auto-generated, but should be committed

### Database File

**`db.sqlite3`**
- SQLite database file
- Contains all application data
- **NOT committed to git** (in .gitignore)
- Created automatically when migrations run
- Each developer has their own local copy

---

## Common Tasks

### Adding a New Property Listing

**Via Admin Interface:**
1. Log in to admin
2. Go to Listings → Listings → Add Listing
3. Fill in form fields
4. Save

**Via Fixture (for bulk data):**
1. Create/edit `listings/fixtures/listings.json`
2. Follow existing JSON structure
3. Run: `python manage.py loaddata listings/fixtures/listings.json`

### Creating a New User Account

1. Admin → Listings → Users → Add User
2. Enter email, name, password
3. Set permissions
4. Save
5. Share credentials securely

### Changing a User's Password

1. Admin → Listings → Users
2. Click on user's email
3. Scroll to password section
4. Enter new password (twice)
5. Save

### Adding a New Neighborhood

1. Admin → Listings → Neighborhoods → Add Neighborhood
2. Enter name
3. Save

### Making a Listing Invisible

1. Admin → Listings → Listings
2. Click on listing
3. Uncheck "Is visible"
4. Save

### Viewing Search Logs

1. Admin → Listings → Search Logs
2. View search history
3. Filter by date, property type, neighborhood, price bucket

### Resetting Database (Development Only)

**Warning:** This deletes all data!

```bash
# Delete database
rm db.sqlite3  # Linux/Mac
del db.sqlite3  # Windows

# Recreate database
python manage.py migrate

# Reload fixtures
python manage.py loaddata listings/fixtures/*.json
```

### Updating Lookup Data

**Add new status:**
1. Admin → Listings → Statuses → Add Status
2. Enter name
3. Save

**Or via fixture:**
1. Edit `listings/fixtures/statuses.json`
2. Add new entry
3. Run: `python manage.py loaddata listings/fixtures/statuses.json`

---

## URL Routes

### Public Routes
- `/` - Homepage (public listings)
- `/home/` - Homepage alias
- `/login/` - Login page
- `/logout/` - Logout (POST only)

### Admin Routes
- `/admin/` - Django admin interface
- `/admin/listings/user/` - User management
- `/admin/listings/listing/` - Listing management
- `/admin/listings/status/` - Status management
- `/admin/listings/propertytype/` - Property type management
- `/admin/listings/neighborhood/` - Neighborhood management
- `/admin/listings/pricebucket/` - Price bucket management
- `/admin/listings/photo/` - Photo management
- `/admin/listings/searchlog/` - Search log viewing
- `/admin/listings/omaharesource/` - Resources management

---

## Security Considerations

### Current Security Features
- ✅ CSRF protection enabled
- ✅ Password hashing (PBKDF2)
- ✅ Session-based authentication
- ✅ Secure logout (POST request)
- ✅ Admin-only user creation

### Production Recommendations
- Move `SECRET_KEY` to environment variables
- Use PostgreSQL or MySQL instead of SQLite
- Enable HTTPS
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS` properly
- Use strong passwords for admin accounts
- Regular security updates

---

## Troubleshooting

### "No such table" Error
**Solution:** Run migrations
```bash
python manage.py migrate
```

### Can't Log In
- Verify email and password are correct
- Check if user account is active (Admin → Users → Edit user)
- Clear browser cookies/cache
- Try creating new user account

### Listings Not Showing
- Check if listing has `is_visible = True`
- Verify listing exists in database (Admin → Listings)
- Check browser console for errors
- Verify template is rendering correctly

### Admin Interface Not Loading
- Verify superuser account exists
- Check if logged in
- Clear browser cache
- Check Django server logs

### Migration Errors
- Check migration files for conflicts
- Review model changes
- May need to reset database (development only)
- Consult team before deleting production data

---

## Team Contacts & Resources

### Repository
- **GitHub:** https://github.com/tbrzezowsky/ISQA8210-Team3
- **Branch:** `database-login` (current feature branch)

### Documentation Files
- `README.md` - Basic project overview
- `DATABASE_LOGIN_IMPLEMENTATION.md` - Technical implementation details
- `TECHNICAL_IMPLEMENTATION_DETAILS.md` - Konner's branch documentation
- `PROJECT_GUIDE.md` - Complete project guide (this file)

### Getting Help
1. Check this documentation first
2. Review Django documentation: https://docs.djangoproject.com/
3. Check existing code for examples
4. Ask team members
5. Review git commit history for context

---

## Future Enhancements

Potential features to consider:
- Property detail pages
- Search and filtering functionality
- Image upload for listings
- User favorites/bookmarks
- Email notifications
- Advanced search with filters
- Map integration
- Contact/inquiry forms
- Property comparison feature
- Mobile app API

---

## Quick Reference

### Essential Commands
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Run server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load fixtures
python manage.py loaddata listings/fixtures/*.json

# Check for errors
python manage.py check

# Django shell
python manage.py shell
```

### Important URLs
- Homepage: http://127.0.0.1:8000/
- Login: http://127.0.0.1:8000/login/
- Admin: http://127.0.0.1:8000/admin/

---

**Last Updated:** November 2025  
**Version:** 1.0  
**Maintained By:** ISQA8210 Team 3

