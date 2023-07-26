import os
from flask import Flask, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from werkzeug.utils import secure_filename
from docx import Document
import PyPDF2
import openai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mytemporarykey'
app.config['UPLOAD_FOLDER'] = 'C:/Users/Josh Benadiva/git/Apptitude/uploads'

openai.api_key = os.getenv("OPENAI_API_KEY")

class JobForm(FlaskForm):
    preference = StringField('Enter what you like to do', [validators.DataRequired()])
    work_life_balance = StringField('Enter your work-life balance', [validators.DataRequired()])
    salary_desire = StringField('Enter your desired salary', [validators.DataRequired()])
    resume = FileField('Upload your resume', [validators.DataRequired()])
    submit = SubmitField('Generate Job Recommendations')

@app.route("/", methods=("GET", "POST"))
def index():
    form = JobForm()
    if form.validate_on_submit():
        # Save the uploaded file
        resume_file = form.resume.data
        filename = secure_filename(resume_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume_file.save(filepath)

        # Read the file content
        if filename.endswith('.docx'):
            resume_content = read_docx(filepath)
        elif filename.endswith('.pdf'):
            resume_content = read_pdf(filepath)
        else:
            return "Invalid file format. Please upload a .docx or .pdf file."

        preference = form.preference.data
        work_life_balance = form.work_life_balance.data
        salary_desire = form.salary_desire.data

        # Include the resume content in the prompt
        prompt = generate_prompt(preference, work_life_balance, salary_desire, resume_content)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an excellent career consultant, in fact known as one of the best in the world. You have decades of experience matching high-potential clients with jobs that fit their experience and interests.  Everyone of your customers has loved the job opportunities you’ve found that fit them! You have a new client."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return redirect(url_for("index", result=response['choices'][0]['message']['content'].strip()))

    result = request.args.get("result")
    return render_template("index.html", form=form, result=result)


def read_docx(file):
    doc = Document(file)
    return ' '.join([paragraph.text for paragraph in doc.paragraphs])

def read_pdf(file):
    pdfFileObj = open(file, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    text = ''
    for page_num in range(pdfReader.numPages):
        pageObj = pdfReader.getPage(page_num)
        text += pageObj.extractText()
    pdfFileObj.close()
    return text

def generate_prompt(preference, work_life_balance, salary_desire, resume_content):
    # Include resume_content in your prompt
    return f"""
    Your client {preference} and has a {work_life_balance} and a salary preference in the range of {salary_desire}. The client's resume content is as follows:

    {resume_content}

    You need to generate five job recommendations for this new client that is most fitting to them based on their background, preferences and goals. Your recommendations should include the job title, and 3-4 sentences about why this job is fitting for the client. Be as specific as possible to the client’s preferences and resume. Here is an example output of a different client that used you in the past. Keep in mind this is NOT your current client.:
    ...
    """

if __name__ == "__main__":
    app.run(debug=True)