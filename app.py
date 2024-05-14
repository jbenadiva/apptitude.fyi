import os
from flask import Flask, request, jsonify, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, validators
from werkzeug.utils import secure_filename
from docx import Document
from PyPDF2 import PdfReader
from openai import OpenAI
import logging
from dotenv import load_dotenv
from flask_cors import CORS
load_dotenv()  # This loads the environment variables from the .env file into the environment
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

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx'}

def read_docx(file):
    doc = Document(file)
    return ' '.join([paragraph.text for paragraph in doc.paragraphs])

def read_pdf(path):
    pdf = PdfReader(path)
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



class JobForm(FlaskForm):
    class Meta:
        csrf = False  # Disable CSRF for this form

    preference = StringField('Enter what you like to do', [validators.DataRequired()])
    work_life_balance = StringField('Enter your work-life balance', [validators.DataRequired()])
    salary_desire = StringField('Enter your desired salary', [validators.DataRequired()])
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

        preference = form.preference.data
        work_life_balance = form.work_life_balance.data
        salary_desire = form.salary_desire.data
        # print out the form data
        print(preference)
        print(work_life_balance)
        print(salary_desire)

        # Include the resume content in the prompt
        prompt = generate_prompt(preference, work_life_balance, salary_desire, text)
        #check the prompt
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
        recommendations = response.choices[0].message.content
        user_data = {
            "userId": str(os.urandom(16)),  # Generate a random ID for the user
            "preferences": {
                "workStyle": request.form['work_life_balance'],
                "salaryRange": request.form['salary_desire'],
                "workLifeBalance": request.form['work_life_balance'],
                "location": "Unknown"
            },
            "resume": {
                "originalFilename": filename,
                "parsedText": text
            },
            "recommendations": recommendations
        }
        insert_user_data(user_data)
        return jsonify({"result": recommendations})
        
    else:
        errors = form.errors
        return jsonify(errors)
def read_docx(file):
    doc = Document(file)
    return ' '.join([paragraph.text for paragraph in doc.paragraphs])


def read_pdf(path):
    pdf = PdfReader(path)
    text = ''
    for page in pdf.pages:
        text += page.extract_text()
    return text

def generate_prompt(preference, work_life_balance, salary_desire, resume_content):
    # Include resume_content in your prompt
    return f"""
    Your client {preference} and has a {work_life_balance} and a salary preference in the range of {salary_desire}. The client's resume content is as follows:

    {resume_content}

    You need to generate five job recommendations for this new client that is most fitting to them based on their background, preferences and goals. Your recommendations should include the job title, and 3-4 sentences about why this job is fitting for the client. Be as specific as possible to the client’s preferences and resume. Here is an example output of a different client that used you in the past. Please use the same format (numbered 1,2,3,4,5). Keep in mind this is NOT your current client: 

1. Senior Product Manager/ Director of Product: Given your experience as a VP of Product in a startup and your recent internship at Amazon Web Services, a leadership role in product management at a tech firm or startup would be a good fit. This could be either a continuation at Amazon or a similar role in another tech giant or promising startup. 

2. Venture Capitalist: Your experience at Viola Group and your technical background make you an excellent candidate for a role in a venture capital firm, specifically in a fund that focuses on fintech or technology investments. 

3. Tech-focused Management Consultant: Consulting firms are always looking for individuals with a solid understanding of technology and management. Your education and experience make you a strong candidate for these roles. 

4. Product Strategy: Companies, especially in the tech and startup domain, need strategists who understand the product side well. Your background makes you suitable for a product strategy role. 

5. Startup Founder/Co-founder: Given your entrepreneurial studies at Wharton, along with your experience as a founding team member at Giraffe Invest, you might consider launching your own venture.
    """

if __name__ == "__main__":
    app.run(debug=True)
