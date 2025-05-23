import re
from io import StringIO, BytesIO
from pdfminer.high_level import extract_text_to_fp # For PDF parsing
from docx import Document # For DOCX parsing

class ResumeParser:
    def parse_pdf(self, file_stream: BytesIO) -> str:
        """Extracts text from a PDF file stream."""
        output_string = StringIO()
        try:
            # pdfminer.six expects a file-like object
            extract_text_to_fp(file_stream, output_string)
            return output_string.getvalue()
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return ""

    def parse_docx(self, file_stream: BytesIO) -> str:
        """Extracts text from a DOCX file stream."""
        try:
            # python-docx expects a file-like object
            document = Document(file_stream)
            full_text = []
            for para in document.paragraphs:
                full_text.append(para.text)
            return '\n'.join(full_text)
        except Exception as e:
            print(f"Error parsing DOCX: {e}")
            return ""

    def parse_text(self, text_content: str) -> dict:
        """
        Parses raw text content to extract structured information.
        This is a highly simplified example and needs robust NLP for production.
        """
        parsed_data = {
            "skills": [],
            "experience": [], # Simplified for demo, would be detailed entries
            "education": [],  # Simplified for demo, would be detailed entries
            "contact": {"email": None, "phone": None},
            "rawContent": text_content # Keep raw content for display
        }

        lower_case_text = text_content.lower()

        # Regex for email and phone (very basic)
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', lower_case_text)
        if email_match:
            parsed_data["contact"]["email"] = email_match.group(0)

        phone_match = re.search(r'(\d{3}[-.\s]??\d{3}[-.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-.\s]??\d{4}|\d{10})', lower_case_text)
        if phone_match:
            parsed_data["contact"]["phone"] = phone_match.group(0)

        # Placeholder for skill extraction (would use NLP models)
        # For demonstration, let's assume a simple keyword list
        common_skills = ["python", "machine learning", "data science", "rpa", "vertex ai", "tensorflow", "pytorch", "sql", "java", "javascript", "react", "cloud", "aws", "azure", "gcp", "nlp", "deep learning", "statistics", "docker", "kubernetes", "ai", "ml", "big data", "spark", "hadoop"]
        for skill in common_skills:
            if skill in lower_case_text:
                parsed_data["skills"].append(skill)

        # Placeholder for experience & education keywords (for ranking contribution)
        experience_indicators = ['experience', 'worked as', 'developed', 'implemented', 'managed', 'led', 'senior', 'junior', 'associate', 'engineer', 'scientist', 'analyst', 'specialist', 'years']
        parsed_data["experience"] = [kw for kw in experience_indicators if kw in lower_case_text]

        education_indicators = ['education', 'university', 'college', 'bachelor', 'master', 'ph.d', 'degree', 'graduate', 'alumni', 'b.tech', 'm.tech', 'mba', 'computer science', 'engineering', 'statistics', 'mathematics']
        parsed_data["education"] = [kw for kw in education_indicators if kw in lower_case_text]

        return parsed_data