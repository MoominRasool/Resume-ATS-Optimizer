import streamlit as st
import spacy
import pdfplumber
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
import re
import io
import openai  # Optional: Comment out if not using

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_file):
    """Extract text from an uploaded PDF resume."""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = '\n'.join(page.extract_text() for page in pdf.pages if page.extract_text())
        return text
    except Exception as e:
        st.error(f"Error reading resume PDF: {str(e)}")
        return None

def extract_keywords_from_jd(jd_text):
    """Extract key nouns/phrases from JD text using spaCy."""
    if not jd_text.strip():
        st.error("Job description cannot be empty.")
        return []
    doc = nlp(jd_text.lower())
    keywords = [chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 1]
    return list(set(keywords))  # Deduplicate

def parse_resume_sections(resume_text):
    """Split resume into sections using regex."""
    sections = {'CONTACT': '', 'SKILLS': '', 'EXPERIENCE': '', 'EDUCATION': ''}
    current_section = None
    lines = resume_text.split('\n')
    
    for line in lines:
        line_clean = line.strip().upper()
        if line_clean in sections:
            current_section = line_clean
            continue
        if current_section and line.strip():
            sections[current_section] += line + '\n'
    
    return sections

def tailor_resume(resume_text, keywords, use_openai=False):
    """Suggest modifications to add missing keywords."""
    doc = nlp(resume_text.lower())
    resume_words = [token.text for token in doc if token.is_alpha]
    missing_keywords = [kw for kw in keywords if kw not in ' '.join(resume_words)]
    
    suggestions = {}
    if missing_keywords:
        suggestions['SKILLS'] = f"Add to SKILLS: {', '.join(missing_keywords)}"
        
        # Optional: Use OpenAI for rephrasing EXPERIENCE
        if use_openai and openai.api_key:
            prompt = f"Rephrase this resume snippet to naturally include these keywords: {missing_keywords}\nResume: {resume_text[:500]}"
            try:
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
                suggestions['EXPERIENCE'] = response.choices[0].message.content
            except Exception as e:
                st.warning(f"OpenAI error: {str(e)}. Skipping rephrasing.")
    
    return suggestions

def generate_ats_pdf(resume_sections, suggestions):
    """Generate ATS-friendly PDF in memory."""
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Define ATS-friendly styles
    header_style = ParagraphStyle(
        name='Header',
        fontName='Arial',
        fontSize=11,
        leading=14,
        spaceAfter=10,
        alignment=TA_LEFT
    )
    body_style = ParagraphStyle(
        name='Body',
        fontName='Arial',
        fontSize=11,
        leading=14,
        spaceAfter=8,
        bulletIndent=10,
        leftIndent=20,
        alignment=TA_LEFT
    )
    
    story = []
    
    # CONTACT section
    story.append(Paragraph('CONTACT INFORMATION', header_style))
    contact_text = resume_sections.get('CONTACT', 'Your Name, Email, Phone')
    story.append(Paragraph(contact_text.replace('\n', '<br/>'), body_style))
    story.append(Spacer(1, 12))
    
    # SKILLS section with suggestions
    story.append(Paragraph('SKILLS', header_style))
    skills_text = resume_sections.get('SKILLS', '').strip()
    if 'SKILLS' in suggestions:
        skills_text += f"\n{suggestions['SKILLS']}"
    if skills_text:
        for skill in skills_text.split('\n'):
            if skill.strip():
                story.append(Paragraph(f'• {skill.strip()}', body_style))
    else:
        story.append(Paragraph('• Python, AI, NLP', body_style))  # Placeholder
    story.append(Spacer(1, 12))
    
    # EXPERIENCE section
    story.append(Paragraph('EXPERIENCE', header_style))
    exp_text = suggestions.get('EXPERIENCE', resume_sections.get('EXPERIENCE', '• Placeholder experience')).strip()
    for line in exp_text.split('\n'):
        if line.strip():
            story.append(Paragraph(f'• {line.strip()}', body_style))
    story.append(Spacer(1, 12))
    
    # EDUCATION section
    story.append(Paragraph('EDUCATION', header_style))
    edu_text = resume_sections.get('EDUCATION', '• Placeholder education').strip()
    for line in edu_text.split('\n'):
        if line.strip():
            story.append(Paragraph(f'• {line.strip()}', body_style))
    
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer

# Streamlit App
st.set_page_config(page_title="AI Resume Tailorer: ATS Optimizer", layout="wide")

st.title("AI Resume Tailorer: ATS Optimizer")
st.markdown("""
Upload your resume (PDF) and paste the job description (JD) below. The app will analyze the JD for key keywords, tailor your resume to include them naturally, and generate an ATS-friendly PDF output.
- **ATS Best Practices**: Simple formatting, keyword integration, Arial font, no tables/graphics.
- **Optional AI Rephrasing**: Enable OpenAI for smarter bullet point rephrasing (requires API key).
""")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    use_openai = st.checkbox("Use OpenAI for Advanced Rephrasing", value=False)
    if use_openai:
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        if openai_api_key:
            openai.api_key = openai_api_key
        else:
            st.warning("Enter your OpenAI API key to enable rephrasing.")

# Inputs
col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
with col2:
    jd_text = st.text_area("Paste Job Description", height=200, placeholder="Enter the job description here...")

if st.button("Tailor Resume") and resume_file and jd_text:
    with st.spinner("Processing..."):
        resume_text = extract_text_from_pdf(resume_file)
        
        if resume_text:
            keywords = extract_keywords_from_jd(jd_text)
            if keywords:
                st.subheader("Extracted JD Keywords")
                st.write(", ".join(keywords))
                
                resume_sections = parse_resume_sections(resume_text)
                suggestions = tailor_resume(resume_text, keywords, use_openai=use_openai)
                
                st.subheader("Suggested Changes")
                for section, suggestion in suggestions.items():
                    st.write(f"**{section}**: {suggestion}")
                
                pdf_buffer = generate_ats_pdf(resume_sections, suggestions)
                
                st.success("Tailored resume generated!")
                st.download_button(
                    label="Download Tailored Resume (PDF)",
                    data=pdf_buffer,
                    file_name="tailored_resume.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("No keywords extracted from JD. Please provide a detailed job description.")
        else:
            st.error("Failed to process resume. Please check the PDF and try again.")

st.info("Built with Streamlit, spaCy, and ReportLab. For issues or extensions, check the code on GitHub.")