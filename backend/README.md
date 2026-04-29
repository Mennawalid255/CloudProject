Backend Setup (Flask)

Commands to run:

Navigate to the backend folder: cd backend

Create a Virtual Environment:

Windows: python -m venv venv

Mac/Linux: python3 -m venv venv

Activate it:

Windows: .\venv\Scripts\activate

Mac/Linux: source venv/bin/activate

Install dependencies: pip install -r requirements.txt

Run the App: python run.py (or flask run)

Note: Remind them that the first time they run the app, the instance/users.db will be created automatically because of your db.create_all() logic.
