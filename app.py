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
import time
from sqlalchemy import create_engine, Column, Integer, String, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="ElevatIQ", page_icon="📚", layout="wide")

# Load Custom CSS
with open("styles.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Splash Screen
st.markdown("""
    <style>
        .splash-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            z-index: 1000;
            animation: fadeOut 1s ease-in-out forwards;
            animation-delay: 3s;
        }
        .logo-animation {
            width: 200px;
            height: 200px;
            animation: pulse 1.5s infinite alternate, rotate 4s linear infinite;
        }
        @keyframes pulse {
            from { transform: scale(1); }
            to { transform: scale(1.1); }
        }
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        @keyframes fadeOut {
            to { opacity: 0; visibility: hidden; }
        }
        .main-content {
            opacity: 0;
            animation: fadeIn 1s ease-in-out forwards;
            animation-delay: 3.5s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
    <div class="splash-screen">
        <img src="https://raw.githubusercontent.com/MrSingh529/elevatiq/main/assets/images/logo.png" alt="ElevatIQ Logo" class="logo-animation">
        <p style="color: #4c51bf; font-size: 24px; margin-top: 20px;">Loading ElevatIQ...</p>
    </div>
    <div class="main-content">
""", unsafe_allow_html=True)

# Database Setup
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    profession = Column(String)

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    content = Column(JSON)  # List of modules

class Progress(Base):
    __tablename__ = 'progress'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    completion = Column(Float)

class Badge(Base):
    __tablename__ = 'badges'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    badge_name = Column(String)

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(String)

engine = create_engine('sqlite:///elevatiq.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# API Setup
GEMINI_API_KEY = st.secrets.get("api_keys", {}).get("gemini_api_key", "your_key_here")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
client = tweepy.Client(bearer_token=st.secrets.get("x_api", {}).get("bearer_token", "your_token_here"))

@st.cache_data
def get_gemini_response(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(GEMINI_ENDPOINT, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        st.error(f"Error with Gemini API: {e}")
        return "Error fetching response"

def get_trending_skills(profession: str) -> list:
    try:
        query = f"trending skills {profession} -is:retweet"
        tweets = client.search_recent_tweets(query=query, max_results=50, tweet_fields=["created_at"])
        skill_keywords = ["python", "javascript", "java", "cloud", "ai", "machine learning", "data analysis", "devops", "design"]
        skill_count = {}
        trending_skills = []
        for tweet in tweets.data or []:
            text = tweet.text.lower()
            for skill in skill_keywords:
                if skill in text:
                    skill_count[skill] = skill_count.get(skill, 0) + 1
                    if skill_count[skill] > 1 and len(trending_skills) < 5:
                        trending_skills.append(skill.title())
        return trending_skills or ["No trending skills found"]
    except Exception as e:
        st.error(f"Error fetching trends: {e}")
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
        "trending": "See Trending Skills on X",
        "courses": "Manage Courses",
        "dashboard": "Learner Dashboard",
        "discussion": "Discussion Board"
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
        "trending": "X पर ट्रेंडिंग कौशल देखें",
        "courses": "पाठ्यक्रम प्रबंधन",
        "dashboard": "शिक्षार्थी डैशबोर्ड",
        "discussion": "चर्चा बोर्ड"
    }
}

# Session State Initialization
if "user_id" not in st.session_state:
    st.session_state.user_id = None
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

# Helper Functions
def validate_input(name: str, email: str, profession: str) -> bool:
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return (name.strip() and re.match(email_pattern, email) and profession.strip())

def submit_details():
    if validate_input(st.session_state.input_name, st.session_state.input_email, st.session_state.input_profession):
        session = Session()
        user = session.query(User).filter_by(email=st.session_state.input_email).first()
        if not user:
            user = User(name=st.session_state.input_name, email=st.session_state.input_email, profession=st.session_state.input_profession)
            session.add(user)
            session.commit()
        st.session_state.user_id = user.id
        st.session_state.name = user.name
        st.session_state.email = user.email
        st.session_state.profession = user.profession
        st.session_state.form_submitted = True
        suggest_skills()
        st.success(f"{lang['welcome']} Let's get started, {st.session_state.name}!")
    else:
        st.error("Please provide valid name, email, and profession.")

def suggest_skills():
    prompt = f"Suggest 8-10 key skills for a {st.session_state.profession} as a comma-separated list."
    skills_response = get_gemini_response(prompt)
    st.session_state.suggested_skills = [skill.strip() for skill in skills_response.split(",") if skill.strip()]

def get_verification_questions_and_prerequisites(skills: dict) -> tuple:
    skill_ratings = "\n".join([f"{skill}: {rating}/10" for skill, rating in skills.items()])
    prompt = (
        f"For a {st.session_state.profession}, user rated:\n{skill_ratings}\n"
        f"1. Generate one open-ended question per skill to verify proficiency.\n"
        f"2. Provide a brief hint for each question.\n"
        f"3. For skills rated below 5/10, suggest one prerequisite skill.\n"
        f"Return in format: 'Skill: Question | Hint | Prerequisite (if applicable)' (one per line)."
    )
    response = get_gemini_response(prompt)
    questions = {}
    prerequisites = {}
    for line in response.split("\n"):
        if line and ": " in line and "|" in line:
            try:
                skill, rest = line.split(": ", 1)
                parts = rest.split(" | ")
                question, hint = parts[0], parts[1]
                prereq = parts[2] if len(parts) > 2 else None
                questions[skill.strip()] = {"question": question.strip(), "hint": hint.strip()}
                if prereq:
                    prerequisites[skill.strip()] = prereq.strip()
            except:
                st.warning(f"Skipping malformed line: {line}")
    return questions, prerequisites

def score_verification_answers(answers: dict) -> dict:
    if not answers:
        st.error("Please provide answers for each skill.")
        return {}
    prompt = (
        f"Assess these answers for a {st.session_state.profession}:\n" +
        "\n".join([f"{skill}: {answer}" for skill, answer in answers.items()]) +
        "\nScore each out of 10 in format: 'Skill: Score' (one per line)."
    )
    response = get_gemini_response(prompt)
    scores = {}
    for line in response.split("\n"):
        if line and ": " in line:
            try:
                skill, score = line.split(": ")
                scores[skill.strip()] = int(score.strip())
            except:
                st.warning(f"Skipping invalid score: {line}")
    return scores

def get_dynamic_recommendations(profession: str, skills: dict, answers: dict, scores: dict, prerequisites: dict, trending_skills: list) -> str:
    skill_info = "\n".join([f"{skill}: Self-rated {rating}/10, Verification: {scores.get(skill, 'N/A')}/10, Prerequisite: {prerequisites.get(skill, 'None')}" 
                           for skill, rating in skills.items()])
    trending_info = f"Trending skills: {', '.join(trending_skills)}"
    prompt = (
        f"For a '{profession}', user profile:\n{skill_info}\n{trending_info}\n"
        f"Provide a learning path with 3 phases (Beginner, Intermediate, Advanced).\n"
        f"Format:\n- Phase: [Name] - [Duration]\n  - Focus: [Description]\n  - [Skill]: [Resource Type] | [Name] | [URL] | [Rationale]\n"
        f"One recommendation per line."
    )
    return get_gemini_response(prompt)

def export_to_pdf(name: str, profession: str, skills: dict, verification_scores: dict, recommendations: str, trending_skills: list):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle('Header', parent=styles['Heading1'], fontSize=26, textColor=colors.Color(76/255, 81/255, 191/255), spaceAfter=15, alignment=1)
    subheader_style = ParagraphStyle('Subheader', parent=styles['Heading2'], fontSize=16, textColor=colors.grey, spaceAfter=10)
    body_style = ParagraphStyle('Body', parent=styles['BodyText'], fontSize=11, leading=14)
    phase_style = ParagraphStyle('Phase', parent=styles['Heading2'], fontSize=14, textColor=colors.Color(45/255, 55/255, 72/255), spaceAfter=8)
    story = []
    try:
        logo = Image("assets/images/logo.png", width=1.2*inch, height=1.2*inch)
        story.append(logo)
    except:
        story.append(Paragraph("ElevatIQ", header_style))
    story.append(Paragraph("Personalized Learning Path", header_style))
    story.append(Paragraph(f"Name: {name}", body_style))
    story.append(Paragraph(f"Profession: {profession}", body_style))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("Skill Assessment", subheader_style))
    skills_data = [["Skill", "Self-Rating", "Verification Score"]]
    for skill, rating in skills.items():
        skills_data.append([skill, f"{rating}/10", f"{verification_scores.get(skill, 'N/A')}/10"])
    skills_table = Table(skills_data, colWidths=[2.5*inch, 1.2*inch, 1.3*inch])
    skills_table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(76/255, 81/255, 191/255)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    story.append(skills_table)
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("Trending Skills", subheader_style))
    story.append(Paragraph(f"{', '.join(trending_skills)}", body_style))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("Learning Path", subheader_style))
    for line in recommendations.split("\n"):
        if line.strip():
            if "Phase:" in line:
                story.append(Paragraph(line, phase_style))
            else:
                story.append(Paragraph(line.replace("\n", "<br />"), body_style))
    story.append(Paragraph("Generated by ElevatIQ © 2025", body_style))
    doc.build(story)
    buffer.seek(0)
    return buffer

def award_badge(user_id: int, badge_name: str):
    session = Session()
    badge = Badge(user_id=user_id, badge_name=badge_name)
    session.add(badge)
    session.commit()
    st.balloons()
    st.success(f"Badge earned: {badge_name}!")

def show_progress(user_id: int):
    session = Session()
    progress = session.query(Progress).filter_by(user_id=user_id).all()
    total = len(progress)
    completed = sum(1 for p in progress if p.completion >= 1.0)
    if total > 0:
        st.progress(completed / total)
        st.write(f"Progress: {int((completed / total) * 100)}%")
    else:
        st.write("No progress yet.")

# New Features
def create_course():
    st.subheader(lang["courses"])
    with st.form("course_form"):
        title = st.text_input("Course Title")
        description = st.text_area("Description")
        modules = st.text_area("Modules (JSON format, e.g., [{'title': 'Intro', 'content': 'Text'}])")
        if st.form_submit_button("Save Course"):
            try:
                session = Session()
                course = Course(title=title, description=description, content=eval(modules))
                session.add(course)
                session.commit()
                st.success("Course created!")
                award_badge(st.session_state.user_id, "Course Creator")
            except Exception as e:
                st.error(f"Error saving course: {e}")

def discussion_board(course_id: int):
    st.subheader(lang["discussion"])
    session = Session()
    with st.form("post_form"):
        post = st.text_area("Your Post")
        if st.form_submit_button("Submit"):
            session.add(Post(course_id=course_id, user_id=st.session_state.user_id, content=post))
            session.commit()
            st.success("Posted!")
    posts = session.query(Post).filter_by(course_id=course_id).all()
    for post in posts:
        st.markdown(f"**User {post.user_id}**: {post.content}")

def learner_dashboard(user_id: int):
    st.subheader(lang["dashboard"])
    session = Session()
    progress = session.query(Progress).filter_by(user_id=user_id).all()
    if progress:
        df = pd.DataFrame([(p.course_id, p.completion * 100) for p in progress], columns=["Course", "Completion (%)"])
        fig = px.bar(df, x="Course", y="Completion (%)", title="Course Progress")
        st.plotly_chart(fig)
    badges = session.query(Badge).filter_by(user_id=user_id).all()
    if badges:
        st.write("Your Badges:")
        for badge in badges:
            st.markdown(f"- 🏅 {badge.badge_name}")
    show_progress(user_id)

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
                <a href='#' style='color: #edf2f7; text-decoration: none; font-size: 1.1em; display: block; margin: 10px 0;'>📚 Courses</a>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.language = st.selectbox("🌐 Language", ["English", "Hindi"])

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Learn", "Create Courses", "Discuss", "Dashboard"])

    with tab1:
        st.title(lang["title"])
        st.write(lang["welcome"])
        if not st.session_state.form_submitted:
            st.subheader(lang["step1"])
            with st.form("user_details_form"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input(lang["name"], key="input_name")
                with col2:
                    st.text_input(lang["email"], key="input_email")
                st.text_input(lang["profession"], key="input_profession")
                if st.form_submit_button(lang["submit"]):
                    submit_details()
        else:
            st.markdown(f"""
                <div style='background: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
                    <h3>Welcome, {st.session_state.name}!</h3>
                    <p>📧 {st.session_state.email}</p>
                    <p>💼 {st.session_state.profession}</p>
                </div>
            """, unsafe_allow_html=True)

            if not st.session_state.selected_skills:
                st.subheader(lang["step2"])
                st.write(lang["suggested"])
                if st.button("🔄 Suggest More Skills"):
                    suggest_skills()
                    st.rerun()
                selected = st.multiselect(lang["suggested"], st.session_state.suggested_skills, default=st.session_state.suggested_skills[:5])
                custom_skill = st.text_input(lang["add_skill"])
                if st.button("➕ Add Custom Skill") and custom_skill.strip():
                    st.session_state.suggested_skills.append(custom_skill)
                    selected.append(custom_skill)
                    st.rerun()
                if selected and st.button(lang["confirm"]):
                    for skill in selected:
                        st.session_state.selected_skills[skill] = 5
                    st.success("Skills confirmed!")
                    st.rerun()

            elif not st.session_state.verification_questions:
                st.subheader(lang["rate"])
                for skill in st.session_state.selected_skills:
                    rating = st.slider(f"{skill}", 1, 10, st.session_state.selected_skills[skill], key=f"slider_{skill}")
                    st.session_state.selected_skills[skill] = rating
                if st.button("📊 Submit Ratings"):
                    questions, prereqs = get_verification_questions_and_prerequisites(st.session_state.selected_skills)
                    st.session_state.verification_questions = questions
                    st.session_state.prerequisites = prereqs
                    st.success("Ratings submitted!")
                    st.rerun()

            elif not st.session_state.skills_verified:
                st.subheader(lang["step3"])
                st.write(lang["verify_intro"])
                for skill, data in st.session_state.verification_questions.items():
                    answer = st.text_area(f"{skill}: {data['question']}", key=f"verify_{skill}")
                    st.markdown(f"<div class='hint'>Hint: {data['hint']}</div>", unsafe_allow_html=True)
                    st.session_state.verification_answers[skill] = answer
                    if st.session_state.prerequisites.get(skill):
                        st.info(f"Prerequisite: {st.session_state.prerequisites[skill]}")
                if st.button("✔️ Submit Verification"):
                    st.session_state.verification_scores = score_verification_answers(st.session_state.verification_answers)
                    st.session_state.skills_verified = True
                    award_badge(st.session_state.user_id, "Skill Verifier")
                    st.success("Verification complete!")
                    st.rerun()

            else:
                st.subheader(lang["step4"])
                with st.spinner("Generating recommendations..."):
                    if not st.session_state.trending_skills:
                        st.session_state.trending_skills = get_trending_skills(st.session_state.profession)
                    recommendations = get_dynamic_recommendations(
                        st.session_state.profession, st.session_state.selected_skills,
                        st.session_state.verification_answers, st.session_state.verification_scores,
                        st.session_state.prerequisites, st.session_state.trending_skills
                    )
                for phase in ["Beginner", "Intermediate", "Advanced"]:
                    with st.expander(f"📚 {phase} Phase"):
                        for line in recommendations.split("\n"):
                            if phase.lower() in line.lower() or "- " in line:
                                st.markdown(line)
                if st.button(lang["export"]):
                    pdf_buffer = export_to_pdf(
                        st.session_state.name, st.session_state.profession,
                        st.session_state.selected_skills, st.session_state.verification_scores,
                        recommendations, st.session_state.trending_skills
                    )
                    st.download_button("Download PDF", pdf_buffer, "learning_path.pdf", "application/pdf")
                if st.button(lang["start_over"]):
                    for key in list(st.session_state.keys()):
                        if key != "user_id":
                            del st.session_state[key]
                    st.rerun()

    with tab2:
        create_course()

    with tab3:
        session = Session()
        courses = session.query(Course).all()
        course_id = st.selectbox("Select Course", [c.id for c in courses], format_func=lambda x: next(c.title for c in courses if c.id == x))
        if course_id:
            discussion_board(course_id)

    with tab4:
        if st.session_state.user_id:
            learner_dashboard(st.session_state.user_id)
        else:
            st.warning("Please submit your details to view the dashboard.")

    # Footer
    st.markdown("""
        </div>
        <footer>
            <hr style='border: 1px solid #dcdcdc;'>
            <p>ElevatIQ | Developed with 💗 by Harpinder Singh © 2025</p>
        </footer>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()