from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

class SkillMatcher:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        # Attempt to load the Sentence Transformer model
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            self.model_loaded = True
            print(f"Successfully loaded Sentence Transformer model: {model_name}")
        except Exception as e:
            print(f"Warning: Could not load Sentence Transformer model locally ({e}). "
                  "Skill matching will fall back to keyword-based. For full functionality, ensure `transformers` and model are available or integrate with Vertex AI.")
            self.model_loaded = False

    def get_embedding(self, text: str):
        """Generates embedding for a given text using the loaded model."""
        if not self.model_loaded:
            return None # Fallback if model isn't loaded

        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        # Use mean pooling over token embeddings
        sentence_embedding = torch.mean(outputs.last_hidden_state, dim=1).squeeze().cpu().numpy()
        return sentence_embedding

    def calculate_skill_match_score(self, resume_skills: list, job_skills: list) -> float:
        """
        Calculates a semantic similarity score between resume skills and job skills.
        If the embedding model isn't loaded, falls back to a simple keyword match.
        """
        if not resume_skills or not job_skills:
            return 0.0

        if self.model_loaded:
            # Generate embeddings for skills that are not empty strings
            resume_skill_embeddings = [self.get_embedding(skill) for skill in resume_skills if skill.strip() and self.get_embedding(skill) is not None]
            job_skill_embeddings = [self.get_embedding(skill) for skill in job_skills if skill.strip() and self.get_embedding(skill) is not None]

            if resume_skill_embeddings and job_skill_embeddings:
                similarity_matrix = cosine_similarity(resume_skill_embeddings, job_skill_embeddings)
                # A simple aggregation: average of maximum similarity for each resume skill
                # This ensures that if a resume has at least one strong match, it gets credit.
                score = np.mean(np.max(similarity_matrix, axis=1))
                return float(score)
            else:
                # Fallback if embeddings couldn't be generated for some reason (e.g., empty skills)
                return self._simple_keyword_match(resume_skills, job_skills)
        else:
            return self._simple_keyword_match(resume_skills, job_skills)

    def _simple_keyword_match(self, resume_skills: list, job_skills: list) -> float:
        """Fallback to simple keyword matching if semantic model is not available."""
        matched_count = 0
        job_skills_lower = [s.lower() for s in job_skills]
        for r_skill in resume_skills:
            r_skill_lower = r_skill.lower()
            # Check if resume skill is in job skills or vice-versa (partial match)
            if any(r_skill_lower in js for js in job_skills_lower) or \
               any(js in r_skill_lower for js in job_skills_lower):
                matched_count += 1
        # Return proportion of job skills that were matched
        return matched_count / len(job_skills) if job_skills else 0.0