import os
import re
import json
import spacy
from pymongo import MongoClient
from PyPDF2 import PdfReader

# MongoDB connection
client = MongoClient("mongodb+srv://adityae18385:Aditya%400010@cluster0.ezb2c.mongodb.net/")  # Replace with your MongoDB connection string
db = client["view_similar_resumes"]
collection = db["resumes"]

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Folder containing resumes
CV_FOLDER = "cvs"

# Function to extract details from a resume
def extract_details_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # Extract details using regex patterns and NLP
        details = {
            "name": extract_name(text),
            "email": extract_email(text),
            "skills": extract_skills(text),
            "experience": extract_experience(text),
            "education": extract_education(text),
        }

        # Check if all details were successfully extracted
        if not details["name"] or not details["email"]:
            print(f"Warning: Incomplete data for file {file_path}")
            return None

        return details
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# Helper functions for extracting specific fields
def extract_name(text):
    lines = text.split("\n")
    return lines[0].strip() if lines else None

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None

def extract_skills(text):
    doc = nlp(text)
    skills = set()
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"]:
            skills.add(token.text)
    return list(skills)

def extract_experience(text):
    # Match experience in formats like "X years", "X+ years"
    match = re.search(r"(\d+)\+?\s+years? of experience", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None



def extract_education(text):
    education_patterns = [
        r"(Bachelor(?:'s)?\s+of\s+[A-Za-z]+)",  # e.g., Bachelor's of Science
        r"(Master(?:'s)?\s+of\s+[A-Za-z]+)",  # e.g., Master's of Computer Science
        r"(B\.?Tech|M\.?Tech|PhD|Diploma|Associate's Degree|MBA)",  # Short forms
        r"(Bachelor|Master|Doctorate|Graduate|Undergraduate)",  # Generic terms
    ]
    education = set()
    for pattern in education_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        education.update(matches)

    institution_pattern = r"\b(?:University|Institute|College)\b.*?(?=\n|$)"
    institutions = re.findall(institution_pattern, text, re.IGNORECASE)
    if institutions:
        education.update(institutions)

    return list(education)

# Function to upload resumes to MongoDB
def upload_to_mongodb(details):
    try:
        result = collection.insert_one(details)
        print(f"Uploaded to MongoDB with ID: {result.inserted_id}")
    except Exception as e:
        print(f"Error uploading to MongoDB: {e}")

# Function to process each resume
def process_resume(file_path):
    # Extract details from resume PDF
    details = extract_details_from_pdf(file_path)
    if details:
        # Upload the details to MongoDB
        upload_to_mongodb(details)

# Main function
CV_FOLDER = os.path.join(os.getcwd(), "cvs")

def process_resumes():
    if not os.path.exists(CV_FOLDER):
        print(f"Error: The folder '{CV_FOLDER}' does not exist.")
        return

    for file_name in os.listdir(CV_FOLDER):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(CV_FOLDER, file_name)
            print(f"Processing: {file_path}")
            try:
                # Call your resume processing logic here
                process_resume(file_path)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    process_resumes()
