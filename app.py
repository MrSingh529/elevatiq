import streamlit as st
import requests
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

# Set page config as the first command
st.set_page_config(page_title="Dynamic LMS", page_icon="📚")  # Branding

# Custom CSS with Tooltips, Visual Ratings, and Theming
st.markdown("""
    <style>
    .main { background-color: #f5f7fa; font-family: 'Roboto', sans-serif; padding: 20px; }
    h1 { color: #2c3e50; font-size: 2.5em; font-weight: 700; text-align: center; margin-bottom: 10px; }
    h2 { color: #34495e; font-size: 1.8em; font-weight: 500; margin-top: 20px; }
    .stButton>button { background-color: #3498db; color: white; border: none; border-radius: 10px; padding: 12px 30px; font-size: 16px; font-weight: 500; transition: background-color 0.3s ease; }
    .stButton>button:hover { background-color: #2980b9; cursor: pointer; }
    .stForm { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-bottom: 20px; }
    .stSuccess { background-color: #d4edda; color: #155724; border-radius: 8px; padding: 10px; }
    .stError { background-color: #f8d7da; color: #721c24; border-radius: 8px; padding: 10px; }
    .recommendations { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); margin-top: 20px; }
    .hint { color: #7f8c8d; font-size: 0.9em; margin-top: 5px; }
    .tooltip { position: relative; display: inline-block; }
    .tooltip .tooltiptext { visibility: hidden; width: 200px; background-color: #555; color: #fff; text-align: center; border-radius: 6px; padding: 5px; position: absolute; z-index: 1; bottom: 125%; left: 50%; margin-left: -100px; opacity: 0; transition: opacity 0.3s; }
    .tooltip:hover .tooltiptext { visibility: visible; opacity: 1; }
    .star-rating { display: inline-block; font-size: 24px; color: #ddd; }
    .star-rating .filled { color: #f39c12; }
    </style>
    """, unsafe_allow_html=True)

# Google Gemini API Setup
GEMINI_API_KEY = st.secrets["api_keys"]["gemini_api_key"]
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

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

# Language Support
LANGUAGES = {
    "English": {
        "title": "Your Personalized Learning Journey",
        "sidebar": "Dynamic LMS Demo",
        "welcome": "Tell us about yourself, assess your skills, and get tailored course recommendations.",
        "step1": "Step 1: Enter Your Details",
        "name": "Your Name",
        "email": "Email",
        "profession": "Your Profession (e.g., Graphic Designer, Teacher)",
        "submit": "Submit Details",
        "step2": "Step 2: Select and Rate Your Skills",
        "suggested": "Based on your profession, here are some suggested skills:",
        "add_skill": "Add a custom skill (optional)",
        "confirm": "Confirm Skills and Rate",
        "rate": "Rate Your Skills",
        "step3": "Step 3: Verify Your Skills",
        "verify_intro": "Provide detailed answers to these questions to verify your proficiency:",
        "step4": "Step 4: Your Course Recommendations",
        "start_over": "Start Over",
        "export": "Export Recommendations as PDF",
        "trending": "See what’s trending on X for your profession"
    },
    "Hindi": {
        "title": "आपकी व्यक्तिगत शिक्षण यात्रा",
        "sidebar": "डायनामिक LMS डेमो",
        "welcome": "हमें अपने बारे में बताएं, अपने कौशल का मूल्यांकन करें, और अनुकूलित पाठ्यक्रम सुझाव प्राप्त करें।",
        "step1": "चरण 1: अपनी जानकारी दर्ज करें",
        "name": "आपका नाम",
        "email": "ईमेल",
        "profession": "आपका पेशा (उदाहरण: ग्राफिक डिजाइनर, शिक्षक)",
        "submit": "विवरण जमा करें",
        "step2": "चरण 2: अपने कौशल का चयन और मूल्यांकन करें",
        "suggested": "आपके पेशे के आधार पर, यहाँ कुछ सुझाए गए कौशल हैं:",
        "add_skill": "एक कस्टम कौशल जोड़ें (वैकल्पिक)",
        "confirm": "कौशल की पुष्टि करें और मूल्यांकन करें",
        "rate": "अपने कौशल का मूल्यांकन करें",
        "step3": "चरण 3: अपने कौशल की पुष्टि करें",
        "verify_intro": "अपनी दक्षता की पुष्टि के लिए इन सवालों के विस्तृत जवाब दें:",
        "step4": "चरण 4: आपके पाठ्यक्रम सुझाव",
        "start_over": "फिर से शुरू करें",
        "export": "सुझावों को PDF के रूप में निर्यात करें",
        "trending": "अपने पेशे के लिए X पर ट्रेंडिंग देखें"
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
        st.success(f"{lang['welcome']} Great job taking the first step!")
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
    prompt = (
        f"You are an expert assessor. Evaluate these verification answers for a {st.session_state.profession}:\n" +
        "\n".join([f"{skill}: {answer}" for skill, answer in answers.items()]) +
        "\nScore each answer out of 10 based on depth and relevance. Return in format: 'Skill: Score' (one per line)."
    )
    response = get_gemini_response(prompt)
    scores = {}
    for line in response.split("\n"):
        if ": " in line:
            skill, score = line.split(": ")
            scores[skill.strip()] = int(score.strip())
    return scores

def get_dynamic_recommendations(profession: str, skills: dict, answers: dict, scores: dict, prerequisites: dict) -> str:
    skill_info = "\n".join([f"{skill}: Self-rated {rating}/10, Verification: {answers.get(skill, 'Not provided')}, Score: {scores.get(skill, 'N/A')}/10, Prerequisite: {prerequisites.get(skill, 'None')}" 
                           for skill, rating in skills.items()])
    prompt = (
        f"You are an expert education consultant. For a '{profession}', "
        f"the user has this skill profile:\n{skill_info}\n"
        f"Provide a detailed, personalized learning path with 3 phases (Beginner, Intermediate, Advanced). "
        f"For each phase, recommend free online courses, books, YouTube channels, or other resources. "
        f"Include URLs where possible and explain why each resource fits."
    )
    return get_gemini_response(prompt)

def export_to_pdf(name: str, profession: str, skills: dict, verification_scores: dict, recommendations: str):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    header_style = ParagraphStyle('Header', parent=styles['Heading1'], fontSize=24, textColor=colors.darkblue, spaceAfter=12)
    subheader_style = ParagraphStyle('Subheader', parent=styles['Heading2'], fontSize=16, textColor=colors.grey, spaceAfter=8)
    body_style = styles['BodyText']
    body_style.fontSize = 10
    body_style.leading = 14
    
    story = []

    # Header with Logo and LMS Name
    try:
        logo = Image("assets/images/logo.png", width=1*inch, height=1*inch)
        story.append(logo)
    except:
        story.append(Paragraph("Dynamic LMS", header_style))
    story.append(Paragraph("Dynamic LMS - Personalized Learning Path", header_style))
    story.append(Spacer(1, 0.2*inch))

    # User Details
    story.append(Paragraph(f"Prepared for: {name}", subheader_style))
    story.append(Paragraph(f"Profession: {profession}", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Skills Table
    skills_data = [["Skill", "Self-Rating", "Verification Score"]]
    for skill, rating in skills.items():
        v_score = verification_scores.get(skill, "N/A")
        skills_data.append([skill, f"{rating}/10", f"{v_score}/10" if v_score != "N/A" else "N/A"])
    skills_table = Table(skills_data, colWidths=[3*inch, 1*inch, 1*inch])
    skills_table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    story.append(Paragraph("Your Skill Set", subheader_style))
    story.append(skills_table)
    story.append(Spacer(1, 0.2*inch))

    # Recommendations
    story.append(Paragraph("Recommended Learning Path", subheader_style))
    phases = ["Beginner", "Intermediate", "Advanced"]
    current_phase = None
    for line in recommendations.split("\n"):
        line = line.strip()
        if any(phase in line for phase in phases):
            current_phase = line
            story.append(Paragraph(line, subheader_style))
        elif line and current_phase:
            story.append(Paragraph(line.replace("\n", "<br />"), body_style))
        else:
            story.append(Paragraph(line.replace("\n", "<br />"), body_style))
    story.append(Spacer(1, 0.2*inch))

    # Footer
    story.append(Paragraph("Generated by Dynamic LMS © 2025", body_style))

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

    with st.sidebar:
        st.title(lang["sidebar"])
        st.image("assets/images/logo.png")
        st.session_state.language = st.selectbox("Language / भाषा", ["English", "Hindi"])

    st.title(lang["title"])
    st.write(lang["welcome"])

    # Step 1: User Details Form
    if not st.session_state.form_submitted:
        st.subheader(lang["step1"])
        with st.form("user_details_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input(lang["name"], key="input_name")
            with col2:
                st.text_input(lang["email"], key="input_email")
            st.text_input(lang["profession"], key="input_profession")
            st.markdown("<div class='tooltip'>Submit to begin<span class='tooltiptext'>Enter your details to get personalized suggestions.</span></div>", unsafe_allow_html=True)
            st.form_submit_button(lang["submit"], on_click=submit_details)
    else:
        st.success(f"Hello {st.session_state.name}! Your profession: **{st.session_state.profession}**.")

        # Step 2: Select and Rate Skills
        if not st.session_state.selected_skills:
            st.subheader(lang["step2"])
            st.write(lang["suggested"])
            if st.button("Suggest More Skills"):
                suggest_skills()
                st.rerun()
            selected = st.multiselect(lang["suggested"], st.session_state.suggested_skills, default=st.session_state.suggested_skills[:5])
            custom_skill = st.text_input(lang["add_skill"], key="custom_skill")
            if st.button("Add Custom Skill") and custom_skill.strip():
                st.session_state.suggested_skills.append(custom_skill)
                selected.append(custom_skill)
                st.rerun()
            if selected and st.button(lang["confirm"]):
                for skill in selected:
                    st.session_state.selected_skills[skill] = 5
                st.success("Skills confirmed! Now rate them.")
                st.rerun()

        # Rate Selected Skills
        elif not st.session_state.verification_questions:
            st.subheader(lang["rate"])
            for skill in st.session_state.selected_skills:
                rating = st.slider(f"{skill}", 1, 10, st.session_state.selected_skills[skill], key=f"slider_{skill}")
                st.session_state.selected_skills[skill] = rating
                st.markdown(render_star_rating(skill, rating), unsafe_allow_html=True)
            if st.button("Submit Ratings"):
                questions, prereqs = get_verification_questions_and_prerequisites(st.session_state.selected_skills)
                st.session_state.verification_questions = questions
                st.session_state.prerequisites = prereqs
                st.success("Ratings submitted! Verify your skills next.")
                st.rerun()

        # Step 3: Skill Verification
        elif not st.session_state.skills_verified:
            st.subheader(lang["step3"])
            st.write(lang["verify_intro"])
            for skill, data in st.session_state.verification_questions.items():
                answer = st.text_area(f"{skill}: {data['question']}", key=f"verify_{skill}")
                st.markdown(f"<div class='hint'>Hint: {data['hint']}</div>", unsafe_allow_html=True)
                st.session_state.verification_answers[skill] = answer
                if st.session_state.prerequisites.get(skill):
                    st.info(f"Prerequisite for {skill}: {st.session_state.prerequisites[skill]}")
            if st.button("Submit Verification"):
                st.session_state.verification_scores = score_verification_answers(st.session_state.verification_answers)
                st.session_state.skills_verified = True
                st.success("Verification complete! Check your recommendations.")
                st.rerun()

        # Step 4: Course Recommendations
        else:
            st.subheader(lang["step4"])
            with st.spinner("Generating personalized recommendations..."):
                recommendations = get_dynamic_recommendations(
                    st.session_state.profession, st.session_state.selected_skills, 
                    st.session_state.verification_answers, st.session_state.verification_scores, 
                    st.session_state.prerequisites
                )
                # Convert URLs to clickable links
                recommendations = re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank">\1</a>', recommendations)
            st.markdown(f"<div class='recommendations'>{recommendations}</div>", unsafe_allow_html=True)

            # Interactive Filters
            filter_option = st.multiselect("Filter Recommendations", ["Free Only", "Short Courses"], key="filters")

            # Community Integration (Mock X Search)
            if st.button(lang["trending"]):
                st.write("Trending on X: (Mock) Python tutorials, AI workshops.")

            # Export to PDF
            if st.button(lang["export"]):
                pdf_buffer = export_to_pdf(
                    st.session_state.name,
                    st.session_state.profession,
                    st.session_state.selected_skills,
                    st.session_state.verification_scores,
                    recommendations
                )
                st.download_button("Download PDF", pdf_buffer, "learning_path.pdf", "application/pdf")

            if st.button(lang["start_over"]):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

    st.markdown("<hr style='border: 1px solid #dcdcdc;'><p style='text-align: center; color: #7f8c8d;'>Developed with 💗 by Harpinder Singh © 2025</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()