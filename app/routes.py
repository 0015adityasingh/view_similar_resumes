
from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from app.db import get_db
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os


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

@routes.route('/resumes/<id>/similar', methods=['GET'])
def fetch_similar_resumes(id):
    """Fetch resumes similar to the specified resume."""
    try:
        # Find the selected resume
        selected_resume = resumes_collection.find_one({"_id": ObjectId(id)})
        if not selected_resume:
            return jsonify({"error": "Resume not found"}), 404

        # Extract attributes with default values for missing or null fields
        selected_skills = set(selected_resume.get('skills', []))
        selected_experience = selected_resume.get('experience') or 0  # Default to 0 if null
        selected_education = set(selected_resume.get('education', []))

        # Validate the presence of necessary fields
        if not selected_skills and not selected_education:
            return jsonify({"error": "Incomplete data in selected resume"}), 400

        # Debugging Logs
        print(f"Selected Resume: Skills: {selected_skills}, Experience: {selected_experience}, Education: {selected_education}")

        similar_resumes = []
        for resume in resumes_collection.find():
            # Skip the selected resume
            if resume['_id'] == ObjectId(id):
                continue

            # Extract attributes with defaults
            resume_skills = set(resume.get('skills', []))
            resume_experience = resume.get('experience') or 0  # Default to 0 if null
            resume_education = set(resume.get('education', []))

            # Debugging Logs
            print(f"Comparing with Resume: Skills: {resume_skills}, Experience: {resume_experience}, Education: {resume_education}")

            # Calculate similarity metrics
            matching_skills = len(selected_skills.intersection(resume_skills))
            total_skills = len(selected_skills.union(resume_skills))
            skills_similarity = (total_skills > 0) and (matching_skills / total_skills) >= 0.5

            experience_similarity = abs(resume_experience - selected_experience) <= 1
            education_similarity = len(selected_education.intersection(resume_education)) > 0

            # Debugging Logs
            print(f"Matching Skills: {matching_skills}, Total Skills: {total_skills}, Skills Similarity: {skills_similarity}")
            print(f"Experience Similarity: {experience_similarity}, Education Similarity: {education_similarity}")

            # Add resume if it meets all criteria
            if skills_similarity and experience_similarity and education_similarity:
                resume['_id'] = str(resume['_id'])  # Convert ObjectId to string
                similar_resumes.append(resume)

        return jsonify(similar_resumes), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

















# from flask import Blueprint, jsonify, request
# from bson.objectid import ObjectId
# from bson.errors import InvalidId
# from app.db import get_db
# import logging

# # Initialize Blueprint and MongoDB
# routes = Blueprint('routes', __name__)
# db = get_db()
# resumes_collection = db['resumes']

# # Configure Logging
# logging.basicConfig(level=logging.DEBUG)

# # Utility Function for Similarity Calculation
# def calculate_similarity(selected, candidate):
#     skills_similarity = (
#         len(selected['skills'].intersection(candidate['skills'])) /
#         len(selected['skills'].union(candidate['skills'])) >= 0.5
#     )
#     experience_similarity = abs(candidate['experience'] - selected['experience']) <= 1
#     education_similarity = len(selected['education'].intersection(candidate['education'])) > 0

#     return skills_similarity and experience_similarity and education_similarity

# @routes.route('/resumes', methods=['GET'])
# def fetch_all_resumes():
#     try:
#         page = int(request.args.get('page', 1))
#         limit = int(request.args.get('limit', 10))
#         skip = (page - 1) * limit

#         resumes = []
#         for resume in resumes_collection.find().skip(skip).limit(limit):
#             resume['_id'] = str(resume['_id'])
#             resumes.append(resume)

#         return jsonify(resumes), 200
#     except Exception as e:
#         logging.error(f"Error fetching resumes: {e}")
#         return jsonify({"error": "Unable to fetch resumes"}), 500

# @routes.route('/resumes/<id>/similar', methods=['GET'])
# def fetch_similar_resumes(id):
#     try:
#         try:
#             resume_id = ObjectId(id)
#         except InvalidId:
#             return jsonify({"error": "Invalid resume ID"}), 400

#         selected_resume = resumes_collection.find_one({"_id": resume_id})
#         if not selected_resume:
#             return jsonify({"error": "Resume not found"}), 404

#         selected = {
#             "skills": set(selected_resume.get('skills', [])),
#             "experience": selected_resume.get('experience', 0),
#             "education": set(selected_resume.get('education', []))
#         }

#         similar_resumes = []
#         for resume in resumes_collection.find():
#             if resume['_id'] == resume_id:
#                 continue

#             candidate = {
#                 "skills": set(resume.get('skills', [])),
#                 "experience": resume.get('experience', 0),
#                 "education": set(resume.get('education', []))
#             }

#             if calculate_similarity(selected, candidate):
#                 resume['_id'] = str(resume['_id'])
#                 similar_resumes.append(resume)

#         return jsonify(similar_resumes), 200
#     except Exception as e:
#         logging.error(f"Error fetching similar resumes: {e}")
#         return jsonify({"error": str(e)}), 500


