# AI Resume Tailorer: ATS Optimizer

A Streamlit web app that tailors resumes to job descriptions (JDs) using AI, generating ATS-friendly PDF resumes. It extracts keywords from a JD (text input) and modifies a resume (PDF input) to include them naturally, ensuring compatibility with Applicant Tracking Systems (ATS).

## Features

- Upload a resume (PDF) and paste a JD (text).
- Extracts keywords from JD using spaCy.
- Suggests or adds missing keywords to resume sections (e.g., SKILLS).
- Optional OpenAI integration for rephrasing experience bullets (requires API key).
- Outputs an ATS-compliant PDF (Arial, 11pt, simple formatting, no tables/graphics).
- Dockerized for easy setup without manual dependency installation.

## Prerequisites

- Docker installed.

## Setup and Running with Docker

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/MoominRasool/Resume-ATS-Optimizer.git
   cd Resume-ATS-Optimizer
   ```

2. **Build the Docker Image**:

   ```bash
   docker build -t ai-resume-tailorer .
   ```

3. **Run the Docker Container**:

   ```bash
   docker run -p 8501:8501 ai-resume-tailorer
   ```

4. **Access the App**:

   - Open your browser to `http://localhost:8501`.
   - Upload a resume PDF, paste a JD, and optionally provide an OpenAI API key for advanced rephrasing.

## Usage

- **Resume**: Upload a PDF with sections like CONTACT, SKILLS, EXPERIENCE, EDUCATION.
- **JD**: Paste the job description in the text area (e.g., "Python developer with machine learning experience").
- **Output**: Download an ATS-friendly PDF resume with integrated JD keywords.

## Optional: OpenAI Integration

- Get an API key from OpenAI.
- Enter it in the app's sidebar to enable smarter rephrasing of resume content.

## Notes

- **ATS Compliance**: The output PDF uses Arial, ALL CAPS headers, simple bullets, and avoids tables/graphics per ATS best practices.
- **Dependencies**: Managed via Docker; no manual installation needed.
- **Extending**: Add features like advanced NLP (e.g., cosine similarity) or custom UI styling.
