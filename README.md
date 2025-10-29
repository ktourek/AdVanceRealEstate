# ISQA8210-Team3
# RealEstate Portal

A Django-based real estate web application for managing and displaying property listings.  
This project was created as part of coursework to practice Django fundamentals and build a foundation for a real estate platform.

---

## 🚀 Features
- Django project **realestate_portal** with app **listings**
- Admin dashboard with superuser authentication
- `Listing` model for properties (title, price, description, address, etc.)
- Fixtures (`listings.json`) to preload sample property listings
- Homepage (`/`) that dynamically displays all published listings in a responsive grid layout

---

## 🛠️ Tech Stack
- **Backend:** Python 3.x, Django 5.x
- **Database:** SQLite (default, can be swapped for PostgreSQL/MySQL)
- **Frontend:** Django templates with simple HTML/CSS
- **Dev Tools:** Git, PyCharm, Virtual Environments

---

## 📂 Project Structure
```
realestate_portal/
    manage.py
    realestate_portal/        ← project settings
    listings/                 ← app for property listings
    templates/                ← global templates (base.html, listings/home.html)
    fixtures/                 ← sample listings (listings.json)
    requirements.txt
    README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone git@github.com:tbrzezowsky/ISQA8210-Team3.git
cd realestate_portal
```

### 2. Create and activate a virtual environment
```bash
python -m venv env
source env/bin/activate   # On macOS/Linux
env\Scripts\activate      # On Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply migrations
```bash
python manage.py migrate
```

### 5. Create a superuser
```bash
python manage.py createsuperuser
```

### 6. Load sample data
```bash
python manage.py loaddata listings.json
```

### 7. Run the development server
```bash
python manage.py runserver
```
Open your browser at 👉 http://127.0.0.1:8000/

---

## ✅ Next Steps
- Add listing **detail pages** for individual properties  
- Implement **pagination and filters** (price, location, etc.)  
- Support **property images** and media uploads  
- Add **inquiry/contact forms** for users  

---

## 🤝 Contributing
1. Create a feature branch  
2. Commit your changes  
3. Push to your branch  
4. Open a Pull Request  

---

## 👥 Team
- **Arunjith Gopinathan** – Initial setup, project foundation  
- (Add other team members as they contribute)

---
