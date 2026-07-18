from google import genai
from google.genai import types, errors as genai_errors
import os, json
from dotenv import load_dotenv
from resume_parser import extract_resume_text, normalize_text
from jd_handler import validate_jd

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def test_gemini_connection():
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say hello in one sentence."
    )
    return response.text

def build_scoring_prompt(resume_text: str, jd_text: str) -> str:
    prompt = f"""You are an ATS (Applicant Tracking System) resume scoring expert.

Compare the RESUME against the JOB DESCRIPTION below and evaluate how well it matches.
IMPORTANT: When identifying "keywords," ONLY include concrete technical skills, tools, technologies, programming languages, frameworks, certifications, or specific methodologies (e.g., "Java", "React", "AWS", "Spring Boot", "TDD", "Kubernetes").
DO NOT include generic responsibility phrases, soft skills, or common verbs (e.g., "design", "develop", "collaborate", "communication skills", "secure code", "team player"). These are NOT keywords, even if they appear in both texts.
ALSO carefully check the resume text for ATS formatting issues. Look specifically for: leftover icon-label text (e.g., words like "Phone-Alt", "Envelope", "Map-marker-alt" that come from icon fonts not rendering as icons), inconsistent bullet point formatting, missing standard section headers (like "Experience" or "Education"), or any oddly fragmented text that suggests a multi-column or table-based layout. If NONE of these issues are present, return an empty list - do not invent warnings that aren't there.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Respond ONLY with a valid JSON object (no markdown, no backticks, no extra text) with exactly this structure:
{{
  "match_score": <integer 0-100>,
  "matched_keywords": [<list of important keywords/skills from the JD that ARE found in the resume>],
  "missing_keywords": [<list of important keywords/skills from the JD that are NOT found in the resume>],
  "formatting_warnings": [<list of any resume formatting issues that could hurt ATS parsing>],
  "summary": "<one or two sentence plain-English verdict>"
}}"""

    return prompt

def score_resume(resume_text: str, jd_text: str) -> dict:
    prompt = build_scoring_prompt(resume_text, jd_text)
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0,
            )
        )
    except genai_errors.APIError as e:
        raise RuntimeError(f"Gemini API call failed: {e}")
    
    if not response.text:
        raise RuntimeError("Gemini returned an empty response. This may be due to a safety filter or content issue.")
    
    raw_text = response.text.strip()
    
    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        raise ValueError(f"Gemini did not return valid JSON. Raw response:\n{raw_text}")
    
    return result

if __name__ == "__main__":
    # Real resume file
    resume_raw = extract_resume_text("Himanshu_Agarwal_React2.pdf")
    resume_text = normalize_text(resume_raw)

    # Paste a real JD here
    jd_text = """
Job Role:- Software Engineer/Senior Software Engineer
Job Location:- Gurgaon/Chennai/Bangalore/Pune/Bhopal/Jaipur/Hyderabad
Experience:- 5-12 Years

Roles & Responsibilities
- Design, develop, and maintain high-quality, production-grade software.
- Deliver end-to-end features from concept, development, testing to deployment and support.
- Specialize in frontend or backend development while contributing toward full-stack capabilities.
- Write clean, secure, testable, and maintainable code following best practices.
- Apply clean architecture, design patterns, and coding standards.
- Implement unit, integration, and automated testing.
- Contribute to CI/CD pipelines and DevOps practices.
- Participate in code reviews, pair programming, and knowledge sharing.
- Collaborate with cross-functional teams in Agile environments.
- Continuously learn and adopt emerging technologies and industry best practices.

Required Skills
- Strong experience in Frontend or Backend development (with willingness to work across the stack).
- Backend: Java (7+), Spring Boot, REST APIs, WebSockets.
- Frontend: JavaScript/TypeScript, React or Vue, HTML/CSS.
- Understanding of software design principles and clean architecture.
- Experience with unit testing, integration testing, BDD/TDD.
- Exposure to Cloud platforms (AWS preferred).
- Familiarity with CI/CD pipelines, Git, and DevOps practices.
- Strong communication and teamwork skills.

Requirements
- Bachelor's degree in Computer Science or equivalent experience.
- Experience working in Agile (Scrum/Kanban) environments.
- Ability to deliver secure, scalable, and high-quality production software.
- Commitment to continuous improvement and team collaboration.
    """
    jd_text = validate_jd(jd_text)

    result = score_resume(resume_text, jd_text)

    print(f"Match Score: {result['match_score']}")
    print(f"\nMatched Keywords: {result['matched_keywords']}")
    print(f"\nMissing Keywords: {result['missing_keywords']}")
    print(f"\nFormatting Warnings: {result['formatting_warnings']}")
    print(f"\nSummary: {result['summary']}")