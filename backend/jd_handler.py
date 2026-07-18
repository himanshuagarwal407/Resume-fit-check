def validate_jd(jd_text: str) -> str:
    """
    Validates the job description text.
    Returns the cleaned JD if valid, raises ValueError if not.
    """
    if not jd_text or not jd_text.strip():
        raise ValueError("Job description cannot be empty.")

    cleaned = jd_text.strip()

    if len(cleaned) < 50:
        raise ValueError("Job description seems too short to be meaningful. Please paste the full description.")

    if len(cleaned) > 20000:
        raise ValueError("Job description is too long. Please paste only the relevant description text.")

    return cleaned

if __name__ == "__main__":
    test_cases = ["", "   ", "Short JD", "A" * 25000]

    for case in test_cases:
        try:
            result = validate_jd(case)
            print(f"Valid! Length: {len(result)}")
        except ValueError as e:
            print(f"Rejected: {e}")