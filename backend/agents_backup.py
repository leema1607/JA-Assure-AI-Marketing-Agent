from .gemini import GeminiService


class ResearchAgent:
    def __init__(self, ai: GeminiService):
        self.ai = ai

    def run(self, brand: str, topic: str, platform: str, language: str) -> str:
        # Lightweight research brief for the prototype.
        # This avoids an additional Gemini API call.
        return f"""
Research Brief for {brand}

Topic: {topic}
Platform: {platform}
Language: {language}

Audience considerations:
- Focus on practical customer needs and awareness.
- Use clear, trustworthy insurance/health-related language.
- Avoid unsupported statistics, guarantees, or specific coverage claims.

Content opportunities:
- Educational awareness
- Preventive actions
- Employee/customer wellbeing
- Practical tips and questions for the audience

Verification:
- Product coverage, pricing, statistics, regulatory claims and guarantees
  must be verified before publication.
"""


class ContentAgent:
    def __init__(self, ai: GeminiService):
        self.ai = ai

    def run(self, brand, platform, objective, topic, language, research, feedback):
        prompt = f"""
You are JA Assure's Content Agent.

Brand: {brand}
Platform: {platform}
Objective: {objective}
Topic: {topic}
Language: {language}

Research brief:
{research}

Previous human feedback:
{feedback or "No previous feedback."}

Create professional marketing content suitable for the selected platform.

Rules:
- Do not invent insurance coverage.
- Do not invent prices.
- Do not make guarantees.
- Do not invent statistics.
- Do not claim regulatory approval.
- Do not make unsupported product claims.
- Use a trustworthy and professional tone.

Return:
1. Final content
2. Short rationale
"""

        return self.ai.generate(prompt, use_search=False)


class ComplianceAgent:
    def __init__(self, ai: GeminiService):
        self.ai = ai

    def run(self, content, brand, research):
        # Lightweight local compliance check for the prototype.
        # This avoids another Gemini API call.
        risky_terms = [
            "guaranteed",
            "100% guaranteed",
            "always covered",
            "never denied",
            "zero risk",
            "instant claim",
            "best insurance",
            "cheapest insurance",
        ]

        content_lower = content.lower()
        issues = []

        for term in risky_terms:
            if term in content_lower:
                issues.append(
                    f"Potentially risky wording detected: '{term}'"
                )

        if issues:
            status = "FAIL"
        else:
            status = "PASS"

        return {
            "status": status,
            "issues": issues,
            "safe_edits": [
                "Verify all product, coverage, pricing and statistical claims before publication.",
                "Obtain human approval before publishing."
            ]
        }


class LeadAgent:
    def __init__(self, ai: GeminiService):
        self.ai = ai

    def run(self, brand, industry, location, count):
        prompt = f"""
You are JA Assure's Lead Generation Agent.

Find up to {count} potential business prospects for {brand}.

Target industry: {industry}
Location: {location}

Use public web sources only.
Do not provide private/personal data.
Do not invent leads or URLs.

Return JSON with:
{{
  "leads": []
}}
"""

        return self.ai.json_generate(prompt)