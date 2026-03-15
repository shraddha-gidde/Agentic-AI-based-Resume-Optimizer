import os
import asyncio
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class ResumeRewriterAgent:

    WEAK_OPENERS = {
        'worked on':       'Contributed to',
        'helped with':     'Collaborated on',
        'responsible for': 'Managed',
        'did':             'Executed',
        'made':            'Developed',
    }

    KNOWN_SKILLS = [
        'Python', 'SQL', 'Excel', 'Tableau', 'Power BI', 'R', 'AWS', 'Azure',
        'Machine Learning', 'Statistics', 'ETL', 'Spark', 'Docker',
        'JavaScript', 'Java', 'NLP', 'TF-IDF', 'FAISS', 'Scikit-learn',
        'Pandas', 'NumPy', 'Streamlit', 'FastAPI', 'Git',
    ]

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self._gemini_ready = False
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self._model = genai.GenerativeModel("gemini-1.5-flash")
                self._gemini_ready = True
                print("✅ ResumeRewriterAgent: Gemini API ready")
            except Exception as e:
                print(f"⚠️  ResumeRewriterAgent: Gemini init failed — {e}. Will use local fallback.")
        else:
            print("⚠️  ResumeRewriterAgent: GEMINI_API_KEY not set. Will use local fallback.")

    # ------------------------------------------------------------------ #
    #  Public entry point
    # ------------------------------------------------------------------ #

    async def rewrite_resume(
        self,
        resume_text: str,
        job_description: str = None,
        target_role: str = "",
        location: str = "",
    ) -> str:
        """
        Rewrite the resume using Gemini API if available.
        Falls back to the local enhancer so the comparison view always
        receives a real string — never an error message.
        """
        if not resume_text or len(resume_text.strip()) < 10:
            return "Please provide a resume to optimize."

        try:
            if self._gemini_ready:
                result = await self._gemini_rewrite(resume_text, job_description, target_role, location)
                if result and len(result.strip()) > 50:
                    return result
                print("⚠️  Gemini returned empty — using local fallback")
        except Exception as e:
            print(f"⚠️  Gemini rewrite failed ({e}) — using local fallback")

        # Local fallback always returns the original + enhancements,
        # never an error string
        return self._local_enhance(resume_text, job_description, target_role, location)

    # ------------------------------------------------------------------ #
    #  Gemini rewrite
    # ------------------------------------------------------------------ #

    async def _gemini_rewrite(
        self,
        resume: str,
        jd: Optional[str],
        target_role: str,
        location: str,
    ) -> str:
        jd_section = f"\n\nJOB DESCRIPTION:\n{jd.strip()}" if jd and jd.strip() else ""
        role_line  = f"\nTarget role: {target_role}" if target_role else ""
        loc_line   = f"\nLocation: {location}" if location else ""

        prompt = f"""You are a professional resume writer helping a job seeker improve their resume.

Rewrite the resume below so it is better aligned with the job description provided.

Rules:
- Keep all real information — do not invent jobs, skills, or dates
- Replace weak openers like "responsible for" or "worked on" with strong action verbs
- Add quantifiable context where the original bullet is vague (use placeholders like [X%] if the number is unknown)
- Make the Professional Summary specifically match the target role
- Add any skills from the job description that are genuinely present in the resume but not currently mentioned
- Keep formatting clean — use plain text with section headers in CAPS
- Return the full rewritten resume only, no commentary{role_line}{loc_line}

ORIGINAL RESUME:
{resume.strip()}
{jd_section}

REWRITTEN RESUME:"""

        response = await asyncio.to_thread(
            self._model.generate_content, prompt
        )
        return response.text.strip()

    # ------------------------------------------------------------------ #
    #  Local fallback (no API needed)
    # ------------------------------------------------------------------ #

    def _local_enhance(
        self,
        resume: str,
        jd: Optional[str],
        target_role: str,
        location: str,
    ) -> str:
        """
        Rule-based enhancement. Always returns a valid non-empty string.
        This is what gets shown in the comparison view when Gemini is
        unavailable — it will show real changes rather than an error.
        """
        parts = []

        # Inject summary if missing
        if 'summary' not in resume.lower() and 'objective' not in resume.lower():
            role_label = target_role or "professional"
            depth = "extensive" if len(resume.split()) > 300 else "solid"
            parts.append(
                "PROFESSIONAL SUMMARY\n"
                f"Results-driven {role_label} with a {depth} background "
                "in data analysis, process improvement, and cross-functional "
                "collaboration. Proven ability to transform complex data into "
                "actionable business insights."
            )

        # Replace weak openers line by line
        enhanced_lines = []
        for line in resume.strip().splitlines():
            stripped = line.strip()
            for weak, strong in self.WEAK_OPENERS.items():
                if stripped.lower().startswith(weak):
                    line = line.replace(stripped[:len(weak)], strong, 1)
                    break
            enhanced_lines.append(line)

        # Nudge for missing metrics
        if not any(ch.isdigit() for ch in resume):
            enhanced_lines.append(
                "\n[Tip: Add metrics — e.g. \"Reduced processing time by X%\" "
                "or \"Managed a dataset of X rows\"]"
            )

        parts.append("\n".join(enhanced_lines))

        # JD-aligned skills block
        if jd:
            jd_lower = jd.lower()
            found = [s for s in self.KNOWN_SKILLS if s.lower() in jd_lower]
            if found:
                parts.append("KEY SKILLS (JD-Aligned)\n" + ", ".join(found[:10]))

        # Location line
        if location and location.lower() not in resume.lower():
            parts.append(f"Location Preference: {location}")

        return "\n\n".join(parts)