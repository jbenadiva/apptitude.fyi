import os
from flask import Flask, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, validators
from werkzeug.utils import secure_filename
from docx import Document
from PyPDF2 import PdfFileReader 
import openai
import logging
from dotenv import load_dotenv
from flask_cors import CORS
import json
from pymongo import MongoClient

load_dotenv() 
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'mytemporarykey'
app.config['UPLOAD_FOLDER'] = 'C:/Users/Josh Benadiva/git/Apptitude/uploads'
app.config['MONGO_URI'] = os.getenv('MONGO_URI')

try:
    client = MongoClient(app.config['MONGO_URI'], serverSelectionTimeoutMS=5000)  # Timeout for MongoDB connection
    client.server_info()  # Attempt to get server info to check connection
    print("Connected to MongoDB")
except Exception as e:
    print("An error occurred while connecting to MongoDB:", str(e))

db = client.apptitude  # Assume 'apptitude' is the correct database name

openai.api_key = os.environ.get("OPENAI_API_KEY")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx'}

def read_docx(file):
    doc = Document(file)
    return ' '.join([paragraph.text for paragraph in doc.paragraphs])

def read_pdf(path):
    pdf = PdfFileReader(path) 
    text = ''
    for page in pdf.pages:
        text += page.extract_text()
    return text

def insert_user_data(user_data):
    """ Insert or update user data in MongoDB """
    try:
        result = db['apptitude-collection'].update_one(
            {"userId": user_data["userId"]},
            {"$set": user_data},
            upsert=True
        )
        print("Data inserted successfully:", result.upserted_id)
        return result
    except Exception as e:
        print("An error occurred while inserting data:", str(e))
        return None

def parse_recommendations(text):
    """ Parse the plain text recommendations into a structured dictionary """
    recommendations = {}
    lines = text.split('\n')
    current_key = None
    for line in lines:
        if line.strip().startswith(tuple(f"{i}." for i in range(1, 6))):  # Look for lines starting with "1.", "2.", etc.
            parts = line.split(':', 1)
            if len(parts) == 2:
                current_key = parts[0].split('.')[0].strip()  # Key is the number before the period
                recommendations[current_key] = {
                    'title': parts[0].split('.', 1)[1].strip(),  # Everything after the number and before the colon
                    'description': parts[1].strip()  # Everything after the colon
                }
        elif current_key and 'description' in recommendations[current_key]:
            recommendations[current_key]['description'] += ' ' + line.strip()

    return recommendations

class JobForm(FlaskForm):
    class Meta:
        csrf = False  # Disable CSRF for this form

    work_pace = StringField('Enter your work-life balance', [validators.DataRequired()])
    work_styles = StringField('Enter your work style', [validators.DataRequired()])
    interaction_styles = StringField('Enter your interaction style', [validators.DataRequired()])
    resume = FileField('Upload your resume', [validators.DataRequired()])
    submit = SubmitField('Generate Job Recommendations')

@app.route("/", methods=["POST"])
def index():
    print("Request received")
    form = JobForm(request.form, meta={'csrf': False})  # Ensure CSRF is disabled

    # Check if the post request has the file part
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file part'}), 400
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        print(f"Filename: {filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Saving file to {filepath}")
        file.save(filepath)
        print(f"File saved to {filepath}")
        
        # Process the file based on its extension
        if filename.endswith('.pdf'):
            text = read_pdf(filepath)
            print(text)
        elif filename.endswith('.docx'):
            text = read_docx(filepath)
            print(text)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        work_pace = request.form['work_pace']
        work_pace_text = "relaxed pace" if int(work_pace) < 30 else "medium pace" if int(work_pace) <= 70 else "fast-paced"
        work_styles = json.loads(request.form['work_styles'])  # Parse the JSON string
        interaction_styles = json.loads(request.form['interaction_styles'])  # Parse the JSON string

        # Print out the form data
        print(work_pace)
        print(work_styles)
        print(interaction_styles)

        # Include the resume content in the prompt
        prompt = generate_prompt(work_pace_text, work_styles, interaction_styles, text)
        # Check the prompt
        print(prompt)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an excellent career consultant, in fact known as one of the best in the world. You have decades of experience matching high-potential clients with jobs that fit their experience and interests.  Every one of your customers has loved the job opportunities you’ve found that fit them! You have a new client."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        print(response)
        raw_recommendations = response.choices[0].message.content
        structured_recommendations = parse_recommendations(raw_recommendations)        
        user_data = {
            "userId": str(os.urandom(16)),  # Generate a random ID for the user
            "preferences": {
                "workPace": work_pace_text,
                "workStyle": work_styles,
                "interactionStyle": interaction_styles,
                "location": "Unknown"
            },
            "resume": {
                "originalFilename": filename,
                "parsedText": text
            },
            "recommendations": structured_recommendations
        }
        insert_user_data(user_data)
        return jsonify({"result": structured_recommendations})
        
    else:
        errors = form.errors
        return jsonify(errors)

@app.route("/regenerate", methods=["POST"])
def regenerate():
    form = JobForm(request.form, meta={'csrf': False})  # Ensure CSRF is disabled

    # Check if the post request has the file part
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file part'}), 400
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if filename.endswith('.pdf'):
            text = read_pdf(filepath)
        elif filename.endswith('.docx'):
            text = read_docx(filepath)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        work_pace = request.form['work_pace']
        work_pace_text = "relaxed pace" if int(work_pace) < 30 else "medium pace" if int(work_pace) <= 70 else "fast-paced"
        work_styles = json.loads(request.form['work_styles'])  # Parse the JSON string
        interaction_styles = json.loads(request.form['interaction_styles'])  # Parse the JSON string
        ratings = json.loads(request.form['ratings'])  # Parse the JSON string
        recommendations = json.loads(request.form['recommendations'])  # Parse the JSON string

        # Use ratings to generate new prompt
        ratings_summary = "\n".join([f"Recommendation {key}: {recommendations[key]['title']}: {value}/10" for key, value in ratings.items()])
        prompt = generate_prompt(work_pace_text, work_styles, interaction_styles, text, ratings_summary)
        print(prompt)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an excellent career consultant, in fact known as one of the best in the world. You have decades of experience matching high-potential clients with jobs that fit their experience and interests. Every one of your customers has loved the job opportunities you’ve found that fit them! You have a new client."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        raw_recommendations = response.choices[0].message.content
        structured_recommendations = parse_recommendations(raw_recommendations)
        # print the recommendations
        print(structured_recommendations)
                # Store the ratings in the database
        user_data = {
            "userId": str(os.urandom(16)),  # Generate a random ID for the user
            "preferences": {
                "workPace": work_pace_text,
                "workStyle": work_styles,
                "interactionStyle": interaction_styles,
                "location": "Unknown"
            },
            "resume": {
                "originalFilename": filename,
                "parsedText": text
            },
            "recommendations": structured_recommendations,
            "ratings": ratings
        }
        insert_user_data(user_data)
        return jsonify({"result": structured_recommendations})

    else:
        errors = form.errors
        return jsonify(errors)
    

def generate_prompt(work_pace, work_styles, interaction_styles, resume_content, ratings_summary=None):
    # Include resume_content and ratings_summary in your prompt
    ratings_text = f"\nPrevious ratings:\n{ratings_summary}" if ratings_summary else ""
    return f"""
    Your client enjoys a pace of work that is {work_pace} and has a strong preference to work in the following styles: {work_styles}. Your client also enjoys the following day-to-day interactions in their job: {interaction_styles}.
    
    The client's resume content is as follows:

    {resume_content}
    
    {ratings_text}

    You need to generate five job recommendations for this new client that is most fitting to them based on their background, preferences and goals. Your recommendations should include the job title, and 3-4 sentences about why this job is fitting for the client. Be as specific as possible to the client’s preferences and resume. Here is an example output of a different client that used you in the past. Please use the same format (numbered 1,2,3,4,5). Keep in mind this is NOT your current client: 

1. Senior Product Manager/ Director of Product: Given your experience as a VP of Product in a startup and your recent internship at Amazon Web Services, a leadership role in product management at a tech firm or startup would be a good fit. This could be either a continuation at Amazon or a similar role in another tech giant or promising startup. 

2. Venture Capitalist: Your experience at Viola Group and your technical background make you an excellent candidate for a role in a venture capital firm, specifically in a fund that focuses on fintech or technology investments. 

3. Tech-focused Management Consultant: Consulting firms are always looking for individuals with a solid understanding of technology and management. Your education and experience make you a strong candidate for these roles. 

4. Product Strategy: Companies, especially in the tech and startup domain, need strategists who understand the product side well. Your background makes you suitable for a product strategy role. 

5. Startup Founder/Co-founder: Given your entrepreneurial studies at Wharton, along with your experience as a founding team member at Giraffe Invest, you might consider launching your own venture.
    """

if __name__ == "__main__":
    app.run(debug=True)
