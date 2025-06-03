from flask import Flask, request, jsonify
from flask_cors import CORS
from autogen import (
    AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, config_list_from_json
)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback

import requests
import json
from datetime import datetime, timedelta
from base64 import b64encode
import os
from dotenv import load_dotenv
from docx import Document

# -------- Flask App --------
app = Flask(__name__)
CORS(app)

# -------- Load OpenAI Config --------
config_list_openai = config_list_from_json(
    "config.json",
    filter_dict={"model": ["gpt-3.5-turbo"]}
)

# -------- Email Sending --------
def send_email(to, subject, body):
    try:
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        SMTP_USERNAME = os.getenv("SMTP_USERNAME")
        SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"\n📧 Email sent to: {to}\nSubject: {subject}\n")
    except Exception as e:
        print(f"❌ Failed to send email to {to}: {e}")
        traceback.print_exc()



# -------- Interview Scheduling --------
def schedule_interview(candidate_name, candidate_email, hr_email, availability):
    # Zoom Server-to-Server OAuth credentials
    ACCOUNT_ID = os.getenv("ACCOUNT_ID")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    # Step 1: Get Access Token
    token_url = f'https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}'
    token_headers = {
        'Authorization': 'Basic ' + b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    token_response = requests.post(token_url, headers=token_headers)
    access_token = token_response.json().get('access_token')

    if not access_token:
        print("❌ Failed to retrieve access token")
        print("Response:", token_response.text)
        return

    # Step 2: Create Zoom Meeting
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    start_time = (datetime.utcnow() + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    meeting_data = {
        "topic": "AutoGen Interview",
        "type": 2,
        "start_time": start_time,
        "duration": 30,
        "timezone": "UTC",
        "agenda": "Auto-generated interview",
        "settings": {
            "host_video": True,
            "participant_video": True,
            "join_before_host": False,
            "mute_upon_entry": True,
            "auto_recording": "cloud"
        }
    }

    response = requests.post(
        'https://api.zoom.us/v2/users/me/meetings',
        headers=headers,
        data=json.dumps(meeting_data)
    )

    if response.status_code != 201:
        print("\n❌ Failed to create meeting")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        return

    meeting = response.json()
    meeting_link = meeting['join_url']
    meeting_password = meeting['password']

    # Step 3: Send emails with meeting info
    message = (
        f"Interview scheduled for {candidate_name}\n"
        f"🕒 Time: {availability}\n"
        f"🔗 Link: {meeting_link}\n"
        f"🔑 Password: {meeting_password}\n"
    )

    send_email(candidate_email, "Interview Schedule", message)
    send_email(hr_email, "Interview Schedule", message)

    print("✅ Interview scheduled and emails sent.")

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    all_text = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            all_text.append(text)

    return "\n".join(all_text)


# -------- Setup Agents --------
summary_agent = AssistantAgent(
    name="SummaryAndEmailHR",
    llm_config={
        "config_list": config_list_openai,
        "seed": 42,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "Send an email with subject and body to a recipient",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {"type": "string"},
                            "subject": {"type": "string"},
                            "body": {"type": "string"}
                        },
                        "required": ["to", "subject", "body"]
                    }
                }
            }
        ]
    },
    function_map={"send_email": send_email}
)

scheduler_agent = AssistantAgent(
    name="InterviewScheduler",
    llm_config={
        "config_list": config_list_openai,
        "seed": 42,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "schedule_interview",
                    "description": "Schedules an interview with a candidate and HR",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "candidate_name": {"type": "string"},
                            "candidate_email": {"type": "string"},
                            "hr_email": {"type": "string"},
                            "availability": {"type": "string"}
                        },
                        "required": ["candidate_name", "candidate_email", "hr_email", "availability"]
                    }
                }
            }
        ]
    },
    function_map={"schedule_interview": schedule_interview}
)

scheduler_agent.default_auto_reply = lambda msg: "Interview scheduled."

user_proxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",  
    code_execution_config={"use_docker": False}
)

# -------- API Endpoint --------
@app.route('/scheduler', methods=['POST'])
def schedule():
    try:
        # Handle file upload
        resume_file = request.files.get("file")  
        if resume_file and resume_file.filename:
            upload_dir = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, resume_file.filename)
            resume_file.save(file_path)
            resume_text = extract_text_from_docx(file_path)
            JD = """
                We are looking for a skilled **Python Developer** to join our data engineering team. The ideal candidate will have experience in building scalable data pipelines and migrating ETL workflows. You will work closely with cross-functional teams to design, develop, and maintain data processing systems using modern frameworks.

                **Key Responsibilities:**
                - Develop and maintain ETL pipelines using PySpark.
                - Migrate existing workflows from Talend to PySpark.
                - Collaborate with data analysts, engineers, and stakeholders to understand requirements.
                - Optimize data processing for performance and scalability.
                - Ensure data quality and consistency.

                **Required Skills:**
                - 2+ years of experience with Python.
                - Strong understanding of PySpark and distributed data processing.
                - Experience with ETL tools like Talend.
                - Familiarity with data warehousing concepts.
                - Experience working with cloud platforms such as AWS or Azure is a plus.
                - Excellent problem-solving and communication skills.

                **Preferred Qualifications:**
                - Bachelor’s degree in Computer Science, Engineering, or related field.
                - Familiarity with CI/CD pipelines and version control tools like Git.

                **Location:** Remote  
                **Job Type:** Full-time  
                **Salary:** Competitive, based on experience
                """
        else:
            print("No resume uploaded.")


        data =  data = {
            "name": request.form.get("name"),
            "experience": request.form.get("experience"),
            "skills": request.form.get("skills"),
            "roles": request.form.get("roles"),
            "availability": request.form.get("availability"),
            "email": request.form.get("email")
        }

        required_fields = ["name", "experience", "skills", "roles", "availability", "email"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing one or more required fields."}), 400

        candidate_questions = [
            "What is your full name?",
            "How many years of experience do you have?",
            "What are your key technical skills?",
            "What roles are you interested in?",
            "What is your availability for interview?",
            "What is your email address?"
        ]

        group_chat = GroupChat(
            agents=[user_proxy, summary_agent, scheduler_agent],
            messages=[],
            max_round=10,
        )

        manager = GroupChatManager(
            groupchat=group_chat,
            llm_config={"config_list": config_list_openai, "seed": 42}
        )

        # Trigger chat
    
        user_proxy.initiate_chat(manager, message=f"""
            You are collaborating with two assistant agents:

            1. **SummaryAndEmailHR** — responsible for evaluating the candidate's eligibility and emailing a summary to HR.
            2. **InterviewScheduler** — responsible for scheduling interviews.

            ## Inputs:

            - **Job Description (JD):**  
                {JD}

            - **Candidate Resume Text:**  
                {resume_text}

            - **Candidate Responses:**  
            Questions: {candidate_questions}  
            Answers: {data}

            ## Instructions:

            ### ➤ Task for Agent `SummaryAndEmailHR`:

            1. Analyze whether the candidate meets the job requirements by comparing the JD and the resume content.
            2. Provide a **clear eligibility decision** (Eligible / Not Eligible) with professional reasoning.
            3. Compose a short, formal summary suitable for HR.
            4. You **MUST** call the `send_email` function via native function calling immediately after the summary is created. This step is **mandatory**.

            Use the following parameters:
            - `to`: "sureshnenavath938@gmail.com"
            - `subject`: "Candidate Evaluation Summary"
            - `body`: the summary content you wrote

            ---

            ### ➤ Task for Agent `InterviewScheduler`:

            1. Use the provided answers to extract:
            - `candidate_name`: extract full name from {data['name']}
            - `candidate_email`: extract just the email from {data['email']}
            - `availability`: extract/convert {data['availability']} to standard datetime or keep as-is if clear
            2. Call the `schedule_interview` function using native function calling (not Python code), with:
            - `candidate_name`
            - `candidate_email`
            - `hr_email`: "sureshnenavath938@gmail.com"
            - `availability`

            ---

            All function calls must be done **only** via native function calling. Do not skip any of the required steps.
            """)


        return jsonify({"status": "success", "message": "Interview scheduled and email is sent"}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=1122, host='0.0.0.0')
