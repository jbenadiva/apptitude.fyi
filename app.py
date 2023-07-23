import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        preference = request.form["preference"]
        work_life_balance = request.form["work_life_balance"]
        salary_desire = request.form["salary_desire"]

        prompt = generate_prompt(preference, work_life_balance, salary_desire)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an excellent career consultant, in fact known as one of the best in the world.You have decades of experience matching high-potential clients with jobs that fit their experience and interests.  Everyone of your customers has loved the job opportunities you’ve found that fit them! You have a new client."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return redirect(url_for("index", result=response['choices'][0]['message']['content'].strip()))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(preference, work_life_balance, salary_desire):
    return f"""

    Your client {preference} and has a {work_life_balance} and a salary preference in the range of {salary_desire}.

You need to generate five job recommendations for this new client that is most fitting to them based on their background, preferences and goals. Your recommendations should include the job title, and 3-4 sentences about why this job is fitting for the client. Be as specific as possible to the client’s preferences and resume. Here is an example output of a different client that used you in the past. Keep in mind this is NOT your current client.: 

Senior Product Manager/ Director of Product: Given your experience as a VP of Product in a startup and your recent internship at Amazon Web Services, a leadership role in product management at a tech firm or startup would be a good fit. This could be either a continuation at Amazon or a similar role in another tech giant or promising startup. 

Venture Capitalist: Your experience at Viola Group and your technical background make you an excellent candidate for a role in a venture capital firm, specifically in a fund that focuses on fintech or technology investments. 

Tech-focused Management Consultant: Consulting firms are always looking for individuals with a solid understanding of technology and management. Your education and experience make you a strong candidate for these roles. 

Product Strategy: Companies, especially in the tech and startup domain, need strategists who understand the product side well. Your background makes you suitable for a product strategy role. 

Startup Founder/Co-founder: Given your entrepreneurial studies at Wharton, along with your experience as a founding team member at Giraffe Invest, you might consider launching your own venture.
    """

if __name__ == "__main__":
    app.run(debug=True)