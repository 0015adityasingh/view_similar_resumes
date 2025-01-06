from flask import Flask
from dotenv import load_dotenv
from app.db import get_db  
from app.routes import routes

load_dotenv()

def create_app():
    app = Flask(__name__)
    try:
        db = get_db()
        db.command("ping")  
        print("Connected to MongoDB successfully!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
    
    app.register_blueprint(routes)
    return app
