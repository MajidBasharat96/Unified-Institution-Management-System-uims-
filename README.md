# Unified-Institution-Management-System-uims-
A centralized platform that streamlines academic operations — managing students, faculty, courses, attendance, grades, and administrative workflows — all in one place. Designed to enhance efficiency, transparency, and collaboration across departments, UIMS empowers institutions to make data-driven decisions with ease.



To run it on any machine:

# 1. Extract the zip, enter the folder
cd uims/

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the one-click setup (migrations + admin user + sample data)
python setup.py

# 5. Start the server
python manage.py runserver 0.0.0.0:8000

Then open http://localhost:8000 and log in with admin / admin123.
