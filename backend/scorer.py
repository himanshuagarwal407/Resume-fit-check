from google import genai
from google.genai import types, errors as genai_errors
import os, json
from dotenv import load_dotenv
from resume_parser import extract_resume_text, normalize_text
from jd_handler import validate_jd
from datetime import date

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def test_gemini_connection():
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say hello in one sentence."
    )
    return response.text

def build_scoring_prompt(resume_text: str, jd_text: str) -> str:
    today = date.today().strftime("%B %d, %Y")
    prompt = f"""You are an ATS (Applicant Tracking System) resume scoring expert.

Compare the RESUME against the JOB DESCRIPTION below and evaluate how well it matches.

IMPORTANT - SKILL DEPTH: For each technical skill found in the resume, distinguish between:
- STRONG matches: skills demonstrated with real context - used in a specific project, role, or achievement with concrete details (e.g., "Built a REST API using Spring Boot handling 5K+ requests/day" shows real Spring Boot usage).
- WEAK matches: skills only mentioned in a skills/tools list with no demonstrated usage or project context (e.g., just listed as "Skills: Spring Boot, Docker" with no elaboration anywhere else).
IMPORTANT - EXPERIENCE: Extract the required years of experience from the JOB DESCRIPTION (if stated). Calculate the candidate's TOTAL professional experience by summing ONLY full-time roles from the resume's work history - EXCLUDE any role explicitly titled or labeled as "Intern," "Internship," (default to excluding internships). Use today's date ({today}) for any role marked "Present" or "Current". Determine if the candidate meets the requirement.
IMPORTANT - FORMATTING: Carefully check the resume text for ATS formatting issues: leftover icon-label text (e.g., "Phone-Alt", "Envelope"), missing section headers, or fragmented text suggesting a multi-column/table layout. Return an empty list if none are found - do not invent issues.
When calculating the overall match_score (0-100), weigh STRONG matches more heavily than WEAK matches, and factor in whether the experience requirement is met.
RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Respond ONLY with a valid JSON object (no markdown, no backticks, no extra text) with exactly this structure:
{{
  "match_score": <integer 0-100>,
  "experience_match": {{
    "required_experience": "<extracted from JD, or 'Not specified' if absent>",
    "candidate_experience": "<estimated from resume work history>",
    "meets_requirement": <true or false>,
    "reasoning": "<brief explanation>"
  }},
  "strong_matches": [<technical skills demonstrated with real project/role context>],
  "weak_matches": [<technical skills only listed without demonstrated usage>],
  "missing_keywords": [<technical skills from JD not found anywhere in resume>],
  "formatting_warnings": [<specific ATS formatting issues, or empty list if none>],
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
    print(f"\nExperience Match: {result['experience_match']}")
    print(f"\nStrong Matches: {result['strong_matches']}")
    print(f"\nWeak Matches: {result['weak_matches']}")
    print(f"\nMissing Keywords: {result['missing_keywords']}")
    print(f"\nFormatting Warnings: {result['formatting_warnings']}")
    print(f"\nSummary: {result['summary']}")