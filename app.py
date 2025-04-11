import streamlit as st
import requests
import re
import tweepy
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

# Set page config as the first command
st.set_page_config(page_title="ElevatIQ", page_icon="📚", layout="wide")

# Load Google Fonts and Custom CSS
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
        font-family: 'Inter', sans-serif;
        padding: 30px;
        min-height: 100vh;
    }

    /* Typography */
    h1 {
        color: #1a202c;
        font-size: 2.8em;
        font-weight: 800;
        text-align: center;
        margin-bottom: 15px;
        letter-spacing: -0.5px;
    }
    h2 {
        color: #2d3748;
        font-size: 1.9em;
        font-weight: 600;
        margin: 30px 0 15px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
    }
    p {
        color: #4a5568;
        font-size: 1.1em;
        line-height: 1.6;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #4c51bf, #667eea);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 12px 35px;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(76, 81, 191, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #434190, #5a67d8);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(76, 81, 191, 0.4);
    }

    /* Forms */
    .stForm {
        background: #ffffff;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
        margin-bottom: 30px;
        transition: transform 0.2s ease;
    }
    .stForm:hover {
        transform: translateY(-5px);
    }
    .stTextInput>input, .stTextArea>textarea, .stSelectbox select {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
        background-color: #f7fafc;
        transition: border-color 0.3s ease;
    }
    .stTextInput>input:focus, .stTextArea>textarea:focus {
        border-color: #4c51bf;
        box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
    }

    /* Notifications */
    .stSuccess {
        background: #e6fffa;
        color: #1a202c;
        border-radius: 10px;
        padding: 15px;
        border-left: 4px solid #38b2ac;
    }
    .stError {
        background: #fff5f5;
        color: #1a202c;
        border-radius: 10px;
        padding: 15px;
        border-left: 4px solid #e53e3e;
    }

    /* Recommendations Section */
    .recommendations {
        background: #ffffff;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.07);
        margin-top: 30px;
        transition: all 0.3s ease;
    }
    .recommendations:hover {
        transform: translateY(-5px);
    }
    .phase-header {
        font-size: 1.7em;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 15px;
        border-left: 4px solid #4c51bf;
        padding-left: 10px;
    }
    .skill-item {
        margin-bottom: 15px;
        padding: 15px;
        background: #f7fafc;
        border-radius: 10px;
        border-left: 5px solid #4c51bf;
        transition: background 0.3s ease;
    }
    .skill-item:hover {
        background: #edf2f7;
    }
    .skill-title {
        font-weight: 600;
        color: #2d3748;
        font-size: 1.2em;
    }
    .resource-details {
        color: #718096;
        font-size: 0.95em;
        line-height: 1.5;
    }

    /* Sidebar */
    .stSidebar {
        background: #2d3748;
        border-radius: 10px;
        padding: 20px;
        color: #edf2f7;
    }
    .stSidebar h1 {
        color: #ffffff;
        font-size: 1.8em;
        text-align: left;
    }
    .stSidebar .stSelectbox select {
        background: #4a5568;
        color: #ffffff;
        border: none;
        border-radius: 8px;
    }

    /* Tooltips */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 220px;
        background: #2d3748;
        color: #ffffff;
        text-align: center;
        border-radius: 8px;
        padding: 8px;
        position: absolute;
        z-index: 10;
        bottom: 125%;
        left: 50%;
        margin-left: -110px;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }

    /* Star Rating */
    .star-rating {
        font-size: 22px;
        color: #e2e8f0;
    }
    .star-rating .filled {
        color: #f6ad55;
    }

    /* Footer */
    footer {
        text-align: center;
        margin-top: 40px;
        color: #718096;
        font-size: 0.9em;
    }
    footer a {
        color: #4c51bf;
        text-decoration: none;
    }
    footer a:hover {
        text-decoration: underline;
    }

    /* Expander */
    .stExpander {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        background: #ffffff;
        margin-bottom: 15px;
    }
    .stExpander summary {
        font-weight: 600;
        color: #2d3748;
        padding: 15px;
    }

    /* Fade-In Animation */
    .stMultiSelect div {
        animation: fadeIn 0.5s ease-in;
    }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)

# Google Gemini API Setup
GEMINI_API_KEY = st.secrets["api_keys"]["gemini_api_key"]
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

client = tweepy.Client(bearer_token=st.secrets["x_api"]["bearer_token"])

@st.cache_data
def get_gemini_response(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(GEMINI_ENDPOINT, headers=headers, json=body)
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            return f"Error: Received status code {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

def get_trending_skills(profession: str) -> list:
    try:
        query = f"trending skills {profession} -is:retweet"
        tweets = client.search_recent_tweets(query=query, max_results=50, tweet_fields=["created_at"])

        skill_keywords = ["python", "javascript", "java", "cloud", "ai", "machine learning", "data analysis", "devops", "design"]
        trending_skills = []
        skill_count = {}

        for tweet in tweets.data or []:
            text = tweet.text.lower()
            for skill in skill_keywords:
                if skill in text and skill not in trending_skills:
                    skill_count[skill] = skill_count.get(skill, 0) + 1
                    if skill_count[skill] > 1 and len(trending_skills) < 5:
                        trending_skills.append(skill.title())

        if not trending_skills:
            trending_skills = ["No trending skills found"]
        return trending_skills[:5]
    except tweepy.TweepyException as e:
        st.error(f"Error fetching trending skills from X: {e}")
        return ["Error fetching trends"]
    except Exception as e:
        st.error(f"Unexpected error fetching trending skills from X: {e}")
        return ["Error fetching trends"]

# Language Support
LANGUAGES = {
    "English": {
        "title": "Your Personalized Learning Journey",
        "sidebar": "ElevatIQ",
        "welcome": "Tell us about yourself, assess your skills, and get tailored course recommendations.",
        "step1": "Step 1: Enter Your Details",
        "name": "Your Name",
        "email": "Email",
        "profession": "Your Profession",
        "submit": "Submit Details",
        "step2": "Step 2: Select and Rate Your Skills",
        "suggested": "Based on your profession, here are some suggested skills:",
        "add_skill": "Add a custom skill",
        "confirm": "Confirm Skills and Rate",
        "rate": "Rate Your Skills",
        "step3": "Step 3: Verify Your Skills",
        "verify_intro": "Answer these questions to verify your proficiency:",
        "step4": "Step 4: Your Course Recommendations",
        "start_over": "Start Over",
        "export": "Export as PDF",
        "trending": "See Trending Skills on X"
    },
    "Hindi": {
        "title": "आपकी व्यक्तिगत शिक्षण यात्रा",
        "sidebar": "डायनामिक LMS",
        "welcome": "हमें अपने बारे में बताएं, अपने कौशल का मूल्यांकन करें, और अनुकूलित पाठ्यक्रम सुझाव प्राप्त करें।",
        "step1": "चरण 1: अपनी जानकारी दर्ज करें",
        "name": "आपका नाम",
        "email": "ईमेल",
        "profession": "आपका पेशा",
        "submit": "विवरण जमा करें",
        "step2": "चरण 2: अपने कौशल का चयन और मूल्यांकन करें",
        "suggested": "आपके पेशे के आधार पर, यहाँ कुछ सुझाए गए कौशल हैं:",
        "add_skill": "एक कस्टम कौशल जोड़ें",
        "confirm": "कौशल की पुष्टि करें और मूल्यांकन करें",
        "rate": "अपने कौशल का मूल्यांकन करें",
        "step3": "चरण 3: अपने कौशल की पुष्टि करें",
        "verify_intro": "अपनी दक्षता की पुष्टि के लिए इन सवालों के जवाब दें:",
        "step4": "चरण 4: आपके पाठ्यक्रम सुझाव",
        "start_over": "फिर से शुरू करें",
        "export": "PDF के रूप में निर्यात करें",
        "trending": "X पर ट्रेंडिंग कौशल देखें"
    }
}

# Session State Initialization
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
    st.session_state.name = ""
    st.session_state.email = ""
    st.session_state.profession = ""
    st.session_state.suggested_skills = []
    st.session_state.selected_skills = {}
    st.session_state.verification_questions = {}
    st.session_state.verification_answers = {}
    st.session_state.verification_scores = {}
    st.session_state.skills_verified = False
    st.session_state.language = "English"
    st.session_state.trending_skills = []
    st.session_state.prerequisites = {}

# Functions
def validate_input(name: str, email: str, profession: str) -> bool:
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return (name.strip() != "" and 
            re.match(email_pattern, email) is not None and 
            profession.strip() != "")

def submit_details():
    if validate_input(st.session_state.input_name, st.session_state.input_email, st.session_state.input_profession):
        st.session_state.name = st.session_state.input_name
        st.session_state.email = st.session_state.input_email
        st.session_state.profession = st.session_state.input_profession
        st.session_state.form_submitted = True
        suggest_skills()
        st.success(f"{lang['welcome']} Let's get started, {st.session_state.name}!")
    else:
        st.error("Please provide a valid name, email, and profession.")

def suggest_skills():
    prompt = (
        f"You are an expert career advisor. For a '{st.session_state.profession}', "
        f"suggest 8-10 key skills that are essential for success in this profession. "
        f"Return the skills as a comma-separated list (e.g., 'Python, Machine Learning, Data Analysis')."
    )
    skills_response = get_gemini_response(prompt)
    st.session_state.suggested_skills = [skill.strip() for skill in skills_response.split(",") if skill.strip()]

def get_verification_questions_and_prerequisites(skills: dict) -> tuple:
    skill_ratings = "\n".join([f"{skill}: {rating}/10" for skill, rating in skills.items()])
    prompt = (
        f"You are an expert in skill assessment. For a {st.session_state.profession}, "
        f"the user has rated their skills as follows:\n{skill_ratings}\n"
        f"1. Generate one open-ended question per skill to verify proficiency. "
        f"2. Provide a brief hint for each question. "
        f"3. For skills rated below 5/10, suggest one prerequisite skill. "
        f"Return in format: 'Skill: Question | Hint | Prerequisite (if applicable)' (one per line)."
    )
    response = get_gemini_response(prompt)
    questions = {}
    prerequisites = {}
    for line in response.split("\n"):
        line = line.strip()
        if line and ": " in line and "|" in line:
            try:
                skill, rest = line.split(": ", 1)
                parts = rest.split(" | ")
                question, hint = parts[0], parts[1]
                prereq = parts[2] if len(parts) > 2 else None
                questions[skill.strip()] = {"question": question.strip(), "hint": hint.strip()}
                if prereq:
                    prerequisites[skill.strip()] = prereq.strip()
            except ValueError:
                st.warning(f"Skipping malformed line: {line}")
    return questions, prerequisites

def score_verification_answers(answers: dict) -> dict:
    if not answers:
        st.error("No verification answers provided. Please enter answers for each skill.")
        return {}
    
    prompt = (
        f"You are an expert assessor. You are given the following verification answers for a {st.session_state.profession}. "
        f"Evaluate each answer based on depth and relevance and score it out of 10. The answers are:\n" +
        "\n".join([f"{skill}: {answer}" for skill, answer in answers.items()]) +
        "\nReturn the scores in the format: 'Skill: Score' (one per line), where Score is a single integer (e.g., 'Prioritization: 7')."
    )
    response = get_gemini_response(prompt)
    scores = {}
    for line in response.split("\n"):
        line = line.strip()
        if line and ": " in line:
            try:
                skill, score = line.split(": ", 1)
                score = score.strip()
                if score.isdigit():
                    scores[skill.strip()] = int(score)
                else:
                    st.warning(f"Skipping invalid score for {skill}: '{score}' is not a number")
            except ValueError as e:
                st.warning(f"Error processing line '{line}': {e}")
    if not scores:
        st.error("No valid scores were extracted. Please try again.")
    return scores

def get_dynamic_recommendations(profession: str, skills: dict, answers: dict, scores: dict, prerequisites: dict, trending_skills: list) -> str:
    skill_info = "\n".join([f"{skill}: Self-rated {rating}/10, Verification: {answers.get(skill, 'Not provided')}, Score: {scores.get(skill, 'N/A')}/10, Prerequisite: {prerequisites.get(skill, 'None')}" 
                           for skill, rating in skills.items()])
    trending_info = f"Trending skills on X for {profession}: {', '.join(trending_skills)}"
    prompt = (
        f"You are an expert education consultant. For a '{profession}', "
        f"the user has this skill profile:\n{skill_info}\n"
        f"Additionally, consider these trending skills from X: {trending_info}\n"
        f"Provide a detailed, personalized learning path with 3 phases (Beginner, Intermediate, Advanced). "
        f"Use this format for each phase:\n"
        f"- Phase: [Phase Name] - [Duration]\n"
        f"  - Focus: [Brief description of focus]\n"
        f"  - [Skill]: [Resource Type] | [Resource Name] | [URL (if available)] | [Rationale]\n"
        f"Ensure the output is plain text with one recommendation per line."
    )
    return get_gemini_response(prompt)

def export_to_pdf(name: str, profession: str, skills: dict, verification_scores: dict, recommendations: str, trending_skills: list):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch, rightMargin=0.75*inch, leftMargin=0.75*inch)
    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle('Header', parent=styles['Heading1'], fontSize=26, textColor=colors.Color(76/255, 81/255, 191/255), spaceAfter=15, fontName='Helvetica-Bold')
    subheader_style = ParagraphStyle('Subheader', parent=styles['Heading2'], fontSize=16, textColor=colors.grey, spaceAfter=10, fontName='Helvetica')
    body_style = ParagraphStyle('Body', parent=styles['BodyText'], fontSize=11, textColor=colors.black, leading=14, fontName='Helvetica')
    
    story = []

    # Header
    try:
        logo = Image("assets/images/logo.png", width=1.2*inch, height=1.2*inch)
        story.append(logo)
    except:
        story.append(Paragraph("ElevatIQ", header_style))
    story.append(Paragraph("Your Personalized Learning Path", header_style))
    story.append(Paragraph("Empowering Your Career Growth", body_style))
    story.append(Spacer(1, 0.3*inch))

    # User Details
    story.append(Paragraph(f"Prepared for: {name}", subheader_style))
    story.append(Paragraph(f"Profession: {profession}", body_style))
    story.append(Spacer(1, 0.25*inch))

    # Skills Table
    skills_data = [["Skill", "Self-Rating", "Verification Score"]]
    for skill, rating in skills.items():
        v_score = verification_scores.get(skill, "N/A")
        skills_data.append([skill, f"{rating}/10", f"{v_score}/10" if v_score != "N/A" else "N/A"])
    skills_table = Table(skills_data, colWidths=[2.5*inch, 1.2*inch, 1.3*inch])
    skills_table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(76/255, 81/255, 191/255)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    story.append(Paragraph("Your Skill Profile", subheader_style))
    story.append(skills_table)
    story.append(Spacer(1, 0.25*inch))

    # Trending Skills
    story.append(Paragraph("Trending Skills on X", subheader_style))
    trending_text = f"For {profession}: {', '.join(trending_skills) if trending_skills and trending_skills[0] != 'Error fetching trends' else 'No trending skills available'}"
    story.append(Paragraph(trending_text, body_style))
    story.append(Spacer(1, 0.25*inch))

    # Recommendations
    story.append(Paragraph("Recommended Learning Path", subheader_style))
    phases = ["Beginner", "Intermediate", "Advanced"]
    current_phase = None
    for line in recommendations.split("\n"):
        line = line.strip()
        if not line:
            continue
        if any(phase.lower() in line.lower() for phase in phases):
            current_phase = next((phase for phase in phases if phase.lower() in line.lower()), None)
            story.append(Paragraph(line, subheader_style))
        elif current_phase:
            story.append(Paragraph(line.replace("\n", "<br />"), body_style))
        else:
            story.append(Paragraph(line.replace("\n", "<br />"), body_style))
    story.append(Spacer(1, 0.25*inch))

    # Footer
    story.append(Paragraph("Generated by ElevatIQ | © 2025 ElevatIQ", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

def render_star_rating(skill: str, rating: int):
    stars = "".join(["★" if i < rating else "☆" for i in range(10)])
    return f"<div class='star-rating'>{stars}</div>"

# Main App
def main():
    global lang
    lang = LANGUAGES[st.session_state.language]

    # Sidebar
    with st.sidebar:
        st.image("assets/images/logo.png", width=150)
        st.markdown("<h1 style='color: #ffffff;'>ElevatIQ</h1>", unsafe_allow_html=True)
        st.markdown("""
            <div style='margin-top: 20px;'>
                <a href='#' style='color: #edf2f7; text-decoration: none; font-size: 1.1em; display: block; margin: 10px 0;'>🏠 Home</a>
                <a href='#' style='color: #edf2f7; text-decoration: none; font-size: 1.1em; display: block; margin: 10px 0;'>👤 Profile</a>
                <a href='#' style='color: #edf2f7; text-decoration: none; font-size: 1.1em; display: block; margin: 10px 0;'>📚 Recommendations</a>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.language = st.selectbox("🌐 Language / भाषा", ["English", "Hindi"], format_func=lambda x: f"{x} ({'EN' if x == 'English' else 'HI'})")

    # Main Content
    st.title(lang["title"])
    st.write(lang["welcome"])

    # Progress Tracker
    progress_steps = ["Details", "Skills", "Rate Skills", "Verify Skills", "Recommendations"]
    current_step = 0
    if st.session_state.form_submitted:
        current_step = 1
        if st.session_state.selected_skills:
            current_step = 2
            if st.session_state.verification_questions:
                current_step = 3
                if st.session_state.skills_verified:
                    current_step = 4
    st.markdown("""
        <div style='display: flex; justify-content: space-between; margin: 20px 0;'>
            {steps}
        </div>
    """.format(steps="".join([f"<div style='flex: 1; text-align: center; padding: 10px; background: {'#4c51bf' if i <= current_step else '#e2e8f0'}; color: {'#ffffff' if i <= current_step else '#4a5568'}; border-radius: 8px; margin: 0 5px;'>{step}</div>" for i, step in enumerate(progress_steps)]))), unsafe_allow_html=True)

    # Step 1: User Details
    if not st.session_state.form_submitted:
        st.subheader(lang["step1"])
        with st.form("user_details_form"):
            st.markdown("<div class='stForm'>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.text_input(lang["name"], key="input_name", placeholder="e.g., John Doe")
            with col2:
                st.text_input(lang["email"], key="input_email", placeholder="e.g., john.doe@example.com")
            st.text_input(lang["profession"], key="input_profession", placeholder="e.g., Software Engineer")
            st.markdown(f"<div class='tooltip'>Submit to begin<span class='tooltiptext'>{lang['welcome']}</span></div>", unsafe_allow_html=True)
            submit_clicked = st.form_submit_button(f"🚀 {lang['submit']}")
            st.markdown("</div>", unsafe_allow_html=True)
        if submit_clicked:
            submit_details()
    else:
        # User Profile Card
        st.markdown(f"""
            <div style='background: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px;'>
                <h3 style='margin: 0; color: #2d3748;'>Welcome, {st.session_state.name}!</h3>
                <p style='color: #718096; margin: 5px 0;'>📧 {st.session_state.email}</p>
                <p style='color: #718096; margin: 5px 0;'>💼 {st.session_state.profession}</p>
            </div>
        """, unsafe_allow_html=True)

        # Step 2: Select Skills
        if not st.session_state.selected_skills:
            st.subheader(lang["step2"])
            st.write(lang["suggested"])
            if st.button("🔄 Suggest More Skills"):
                suggest_skills()
                st.rerun()
            selected = st.multiselect(lang["suggested"], st.session_state.suggested_skills, default=st.session_state.suggested_skills[:5])
            custom_skill = st.text_input(lang["add_skill"], key="custom_skill", placeholder="e.g., Blockchain")
            if st.button("➕ Add Custom Skill") and custom_skill.strip():
                st.session_state.suggested_skills.append(custom_skill)
                selected.append(custom_skill)
                st.rerun()
            if selected and st.button(f"✅ {lang['confirm']}"):
                for skill in selected:
                    st.session_state.selected_skills[skill] = 5
                st.success("Skills confirmed! Now rate them.")
                st.rerun()

        # Step 3: Rate Skills
        elif not st.session_state.verification_questions:
            st.subheader(lang["rate"])
            for skill in st.session_state.selected_skills:
                rating = st.slider(f"{skill}", 1, 10, st.session_state.selected_skills[skill], key=f"slider_{skill}")
                st.session_state.selected_skills[skill] = rating
                st.markdown(render_star_rating(skill, rating), unsafe_allow_html=True)
            if st.button("📊 Submit Ratings"):
                questions, prereqs = get_verification_questions_and_prerequisites(st.session_state.selected_skills)
                st.session_state.verification_questions = questions
                st.session_state.prerequisites = prereqs
                st.success("Ratings submitted! Verify your skills next.")
                st.rerun()

        # Step 4: Verify Skills
        elif not st.session_state.skills_verified:
            st.subheader(lang["step3"])
            st.write(lang["verify_intro"])
            for skill, data in st.session_state.verification_questions.items():
                answer = st.text_area(f"{skill}: {data['question']}", key=f"verify_{skill}", placeholder="Provide a detailed answer...")
                st.markdown(f"<div class='hint'>Hint: {data['hint']}</div>", unsafe_allow_html=True)
                st.session_state.verification_answers[skill] = answer
                if st.session_state.prerequisites.get(skill):
                    st.info(f"Prerequisite for {skill}: {st.session_state.prerequisites[skill]}")
            if st.button("✔️ Submit Verification"):
                st.session_state.verification_scores = score_verification_answers(st.session_state.verification_answers)
                st.session_state.skills_verified = True
                st.success("Verification complete! Check your recommendations.")
                st.rerun()

        # Step 5: Recommendations
        else:
            st.subheader(lang["step4"])
            with st.spinner("<div style='display: flex; align-items: center;'><img src='https://loading.io/assets/mod/spinner/spinner/lg.gif' width='30'> Generating recommendations...</div>"):
                if not st.session_state.trending_skills:
                    st.session_state.trending_skills = get_trending_skills(st.session_state.profession)
                recommendations = get_dynamic_recommendations(
                    st.session_state.profession, st.session_state.selected_skills, 
                    st.session_state.verification_answers, st.session_state.verification_scores, 
                    st.session_state.prerequisites, st.session_state.trending_skills
                )
                recommendations = re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank">\1</a>', recommendations)

            st.markdown("<div class='recommendations'>", unsafe_allow_html=True)
            phases = {"Beginner": None, "Intermediate": None, "Advanced": None}
            current_phase = None
            phase_content = {"Beginner": [], "Intermediate": [], "Advanced": []}

            for line in recommendations.split("\n"):
                line = line.strip()
                if not line:
                    continue
                for phase in phases.keys():
                    if phase.lower() in line.lower():
                        current_phase = phase
                        phases[phase] = st.expander(f"📚 {phase} Phase", expanded=True)
                        break
                if current_phase and line:
                    phase_content[current_phase].append(line)

            for phase, expander in phases.items():
                if expander:
                    with expander:
                        if phase_content[phase]:
                            st.markdown(f"<div class='phase-header'>{phase_content[phase][0]}</div>", unsafe_allow_html=True)
                            for item in phase_content[phase][1:]:
                                if ": " in item:
                                    skill, details = item.split(": ", 1)
                                    parts = [d.strip() for d in details.split(" | ")]
                                    if len(parts) >= 3:
                                        resource_type = parts[0]
                                        resource_name = parts[1]
                                        url = parts[2] if len(parts) > 2 and parts[2] else "N/A"
                                        rationale = parts[3] if len(parts) > 3 else "No rationale provided"
                                        st.markdown(f"""
                                            <div class='skill-item'>
                                                <div class='skill-title'>📖 {skill}</div>
                                                <div class='resource-details'>
                                                    <strong>Type:</strong> {resource_type}<br>
                                                    <strong>Resource:</strong> {resource_name} {f'<a href="{url}" target="_blank">Link</a>' if url != "N/A" else ''}<br>
                                                    <strong>Rationale:</strong> {rationale}
                                                </div>
                                            </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.warning(f"Skipping malformed recommendation: {item}")
                        else:
                            st.write("No recommendations available for this phase.")
            st.markdown("</div>", unsafe_allow_html=True)

            # Filters
            st.markdown("<h3>🔎 Filter Recommendations</h3>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                free_filter = st.checkbox("Free Only", key="free_filter")
            with col2:
                short_filter = st.checkbox("Short Courses", key="short_filter")
            if free_filter or short_filter:
                st.info("Filters applied. Recommendations may be limited.")

            # Trending Skills
            if st.button(f"📈 {lang['trending']}"):
                with st.spinner("<div style='display: flex; align-items: center;'><img src='https://loading.io/assets/mod/spinner/spinner/lg.gif' width='30'> Fetching trending skills...</div>"):
                    st.session_state.trending_skills = get_trending_skills(st.session_state.profession)
                st.write(f"Trending skills on X for {st.session_state.profession}:")
                for skill in st.session_state.trending_skills:
                    st.write(f"- {skill}")
                st.info("These trending skills have been incorporated into your recommendations.")

            # Export PDF
            if st.button(f"📄 {lang['export']}"):
                pdf_buffer = export_to_pdf(
                    st.session_state.name,
                    st.session_state.profession,
                    st.session_state.selected_skills,
                    st.session_state.verification_scores,
                    recommendations,
                    st.session_state.trending_skills
                )
                st.download_button("Download PDF", pdf_buffer, "learning_path.pdf", "application/pdf")

            # Start Over
            if st.button(f"🔄 {lang['start_over']}"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

    # Footer
    st.markdown("""
        <footer>
            <hr style='border: 1px solid #dcdcdc;'>
            <p>ElevatIQ | Developed with 💗 by Harpinder Singh © 2025</p>
        </footer>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()