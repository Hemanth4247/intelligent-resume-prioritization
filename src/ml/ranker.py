from typing import List, Dict
import re

class ResumeRanker:
    def __init__(self, skill_weight: float = 0.6, experience_weight: float = 0.3, education_weight: float = 0.1):
        self.skill_weight = skill_weight
        self.experience_weight = experience_weight
        self.education_weight = education_weight

    def estimate_experience_years(self, experience_keywords: List[str]) -> float:
        """
        Estimates total years of experience from parsed experience keywords.
        This is a highly simplified heuristic for demo. In reality, you'd parse dates
        from work history entries (e.g., "Jan 2020 - Present") or use ML models trained on experience data.
        """
        # Look for explicit "X years"
        years_keywords = [int(re.findall(r'\d+', kw)[0]) for kw in experience_keywords if 'years' in kw and re.findall(r'\d+', kw)]
        if years_keywords:
            return max(years_keywords) # Return highest mentioned "years"

        # Heuristics based on role indicators
        if any(kw in ['senior', 'lead', 'manager', 'architect'] for kw in experience_keywords):
            return 5.0 # Assume senior roles imply at least 5 years
        elif any(kw in ['junior', 'associate', 'entry-level'] for kw in experience_keywords):
            return 1.0 # Assume junior roles imply 1-2 years
        elif experience_keywords: # Just presence of general experience keywords
            return 2.0 # Assume some experience if keywords are there
        return 0.0 # No experience indicated

    def calculate_score(self, resume_data: Dict, job_requirements: Dict, skill_matcher_score: float) -> float:
        """
        Calculates a composite score for a resume based on job requirements.
        Each component (skill, experience, education) contributes to the total score.
        """
        total_score = 0.0

        # Skill Score (comes from SkillMatcher, already 0-1)
        total_score += self.skill_weight * skill_matcher_score

        # Experience Score (0-1)
        candidate_experience_years = self.estimate_experience_years(resume_data.get("experience", []))
        required_experience_years = job_requirements.get("min_experience_years", 0)

        experience_score = 0.0
        if required_experience_years > 0:
            # Candidate meets or exceeds required experience
            if candidate_experience_years >= required_experience_years:
                experience_score = 1.0
            else: # Candidate has some experience but less than required
                experience_score = min(candidate_experience_years / required_experience_years, 1.0)
        elif candidate_experience_years > 0: # If job has no min req but candidate has experience
            experience_score = 0.5 # Give a baseline score for having experience

        total_score += self.experience_weight * experience_score

        # Education Score (0-1)
        education_score = 0.0
        required_education = job_requirements.get("required_education", [])
        if required_education:
            # Check for matches in candidate's education keywords
            candidate_education_lower = [e.lower() for e in resume_data.get("education", [])]
            # Check if any required education keyword is present in candidate's education keywords
            if any(req_edu.lower() in cand_edu for req_edu in required_education for cand_edu in candidate_education_lower):
                education_score = 1.0 # Direct match or strong relevance
            # Broad check for presence of any degree if specific not found
            elif any(degree_type in cand_edu for degree_type in ['bachelor', 'master', 'phd'] for cand_edu in candidate_education_lower):
                education_score = 0.5 # Has a degree, but maybe not the specific required type

        total_score += self.education_weight * education_score

        # Normalize total score to be out of 100
        # The weights sum to 1.0, so total_score is already between 0 and 1.
        # Multiply by 100 for a 0-100 scale.
        return min(100, round(total_score * 100))


    def rank_resumes(self, processed_resumes: List[Dict], job_requirements: Dict, skill_matcher) -> List[Dict]:
        """Ranks a list of processed resumes based on job requirements."""
        ranked_resumes = []
        for resume in processed_resumes:
            # Get skills from the processed resume data
            resume_skills = resume.get("parsed_data", {}).get("skills", [])

            # Use job_requirements extracted in app.py
            job_skills = job_requirements.get("required_skills", [])

            # Calculate skill match score using the provided skill_matcher instance
            skill_match_score = skill_matcher.calculate_skill_match_score(resume_skills, job_skills)

            # Calculate overall score for the resume
            overall_score = self.calculate_score(
                resume_data=resume.get("parsed_data", {}),
                job_requirements=job_requirements,
                skill_matcher_score=skill_match_score
            )
            ranked_resumes.append({
                "resume_id": resume.get("resume_id"),
                "original_source": resume.get("original_source"),
                "score": overall_score,
                "skill_match_score": round(skill_match_score * 100), # Convert to percentage for display
                "estimated_experience_years": self.estimate_experience_years(resume.get("parsed_data", {}).get('experience', [])),
                "parsed_data": resume.get("parsed_data", {})
            })

        # Sort in descending order of score
        ranked_resumes.sort(key=lambda x: x["score"], reverse=True)
        return ranked_resumes