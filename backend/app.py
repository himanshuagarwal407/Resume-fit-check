import gradio as gr
import logging

from resume_parser import extract_resume_text, normalize_text
from jd_handler import validate_jd
from scorer import score_resume

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


def run_scan(resume_file, jd_text, progress=gr.Progress()):
    if resume_file is None:
        return "Please upload a resume file."

    try:
        progress(0.1, desc="Reading resume file...")
        logger.info("Extracting text from resume")
        raw_text = extract_resume_text(resume_file)

        if not raw_text or not raw_text.strip():
            return "Could not extract any text from the resume. It may be a scanned/image-based file."

        progress(0.3, desc="Cleaning extracted text...")
        resume_text = normalize_text(raw_text)

        progress(0.5, desc="Validating job description...")
        cleaned_jd = validate_jd(jd_text)

        progress(0.7, desc="Scoring resume against job description (calling Gemini)...")
        logger.info("Calling Gemini API for scoring")
        result = score_resume(resume_text, cleaned_jd)

        progress(1.0, desc="Done!")
        logger.info(f"Scan complete. Match score: {result['match_score']}")

    except ValueError as e:
        logger.warning(f"Input error: {e}")
        return f"Input error: {e}"
    except RuntimeError as e:
        logger.error(f"Scoring error: {e}")
        return f"Scoring error: {e}"

    exp = result["experience_match"]

    output = f"""## Match Score: {result['match_score']}/100

### Experience
- **Required:** {exp['required_experience']}
- **Candidate's Experience:** {exp['candidate_experience']}
- **Meets Requirement:** {'✅ Yes' if exp['meets_requirement'] else '❌ No'}
- {exp['reasoning']}

### Strong Matches (demonstrated with real usage)
{', '.join(result['strong_matches']) if result['strong_matches'] else 'None'}

### Weak Matches (only listed, no demonstrated usage)
{', '.join(result['weak_matches']) if result['weak_matches'] else 'None'}

### Missing Keywords
{', '.join(result['missing_keywords']) if result['missing_keywords'] else 'None'}

### Formatting Warnings
{chr(10).join('- ' + w for w in result['formatting_warnings']) if result['formatting_warnings'] else 'None'}

### Summary
{result['summary']}
"""
    return output


demo = gr.Interface(
    fn=run_scan,
    inputs=[
        gr.File(label="Upload Resume (PDF or DOCX)"),
        gr.Textbox(label="Paste Job Description", lines=10)
    ],
    outputs=gr.Markdown(label="Results"),
    title="ResumeFitCheck",
    description="Upload your resume and paste a job description to get an ATS match score."
)

if __name__ == "__main__":
    demo.launch()