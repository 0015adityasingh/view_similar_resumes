# ○	Display a list of all resumes in a table or grid format.
# ○	Include attributes: name, email, skills, experience, education.

# ●	APIs:
# 	GET /resumes: Fetch all resumes.
# ●	Performance: API response time under 2 seconds
# Database schema and API setup 	Aditya	3 days



from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from app.db import get_db

routes = Blueprint('routes', __name__)
db = get_db()
resumes_collection = db['resumes'] 

@routes.route('/resumes', methods=['GET'])
def fetch_all_resumes():
    try:
        resumes = []
        for resume in resumes_collection.find():
            resume['_id'] = str(resume['_id'])  
            resumes.append(resume)
        print(resumes) 
        return jsonify(resumes), 200
    except Exception as e:
        print(f"Error fetching resumes: {e}")
        return jsonify({"error": "Unable to fetch resumes"}), 500




