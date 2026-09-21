import json
import re
from typing import Any, Dict, List

from .gemini import GeminiService


# ============================================================
# RESEARCH AGENT
# ============================================================

class ResearchAgent:
    def __init__(self, gemini=None):
        self.gemini = gemini or GeminiService()

    def run(self, brand: str, platform: str, topic: str, language: str = "English") -> str:
        prompt = f"""
You are the Research Agent for JA Assure.

Brand: {brand}
Platform: {platform}
Topic: {topic}
Language: {language}

Research:
1. Current industry context
2. Audience pain points
3. Competitor/content opportunities
4. Useful content angles
5. Compliance-sensitive areas

Do not invent statistics, insurance coverage, prices, guarantees,
regulatory approvals, or product claims.

Return a concise research brief.
"""

        try:
            result = self.gemini.generate(prompt, use_search=True)

            if result and result.strip():
                return result

        except Exception as e:
            print(f"Research Agent fallback: {e}")

        # Reliable local fallback
        return f"""
JA Assure Research Brief

Brand:
{brand}

Platform:
{platform}

Topic:
{topic}

Language:
{language}

Audience focus:
- Customers interested in protection, wellbeing and risk management
- Businesses looking for practical insurance-related solutions
- Decision-makers who prefer clear and trustworthy information

Content opportunities:
- Educational content
- Practical prevention tips
- Awareness campaigns
- Customer pain points
- Simple explanations of insurance-related topics

Compliance focus:
- Avoid unsupported guarantees
- Avoid invented statistics
- Avoid promising coverage without verified product information
- Avoid misleading or exaggerated claims
- Human approval is required before publishing
""".strip()


# ============================================================
# CONTENT AGENT
# ============================================================

class ContentAgent:
    def __init__(self, gemini=None):
        self.gemini = gemini or GeminiService()

    def run(
        self,
        brand: str,
        platform: str,
        objective: str,
        topic: str,
        language: str,
        research: str,
        feedback: str = "",
    ) -> str:

        platform_rules = {
            "LinkedIn": """
Create professional LinkedIn content.
Use a strong opening.
Use short paragraphs.
Give useful educational information.
End with a natural CTA.
Use 3–5 relevant hashtags.
""",
            "Instagram": """
Create Instagram content.
Use an attention-grabbing opening.
Use short readable sections.
Use suitable emojis.
End with a natural CTA.
Use 5–8 relevant hashtags.
""",
            "X": """
Create concise X content.
Focus on one main message.
Keep it easy to read.
Use a short CTA.
Use 2–4 relevant hashtags.
""",
            "Blog": """
Create a structured blog article.
Include:
- Title
- Introduction
- Main sections
- Practical points
- Conclusion
- CTA
""",
            "Reel": """
Create a 30–60 second Reel/video script.
Include:
- Hook
- Main message
- Key points
- CTA
"""
        }

        language_rules = {
            "English": "Write completely in English.",
            "Malay": "Write completely in Malay. Translate the topic naturally into Malay.",
            "Bahasa Indonesia": "Write completely in Bahasa Indonesia. Translate the topic naturally into Bahasa Indonesia.",
            "Thai": "Write completely in Thai script. Translate the topic naturally into Thai.",
            "Chinese": "Write completely in Chinese characters. Translate the topic naturally into Chinese."
        }

        rules = platform_rules.get(platform, platform_rules["LinkedIn"])
        lang_rule = language_rules.get(language, language_rules["English"])

        prompt = f"""
You are the AI Content Agent for JA Assure.

Brand:
{brand}

Platform:
{platform}

Objective:
{objective}

Original Topic:
{topic}

Required Language:
{language}

Research:
{research}

Previous Human Feedback:
{feedback if feedback else "No previous feedback."}

LANGUAGE REQUIREMENT:
{lang_rule}

IMPORTANT:
- The topic itself must also be adapted/translated into the selected language.
- Do not leave English topic text inside a non-English result unless it is a proper brand/product name.
- Keep brand names such as JA Assure, DoctorShield, Jade and Jaguar Transit unchanged.
- Do not invent insurance coverage.
- Do not invent prices.
- Do not invent guarantees.
- Do not invent statistics.
- Do not claim regulatory approval unless verified.
- Do not make unsupported medical or financial claims.
- Use a professional and trustworthy tone.

PLATFORM REQUIREMENTS:
{rules}

Generate the final marketing content only.
"""

        try:
            result = self.gemini.generate(prompt, use_search=False)

            if result and result.strip():
                return result.strip()

        except Exception as e:
            message = str(e)
            print(f"Content Agent Gemini unavailable: {message}")

        # Always return local demo content if Gemini is unavailable
        return self._demo_content(
            brand=brand,
            platform=platform,
            objective=objective,
            topic=topic,
            language=language,
            feedback=feedback,
        )

    # --------------------------------------------------------
    # DEMO CONTENT
    # --------------------------------------------------------

    def _demo_content(
        self,
        brand: str,
        platform: str,
        objective: str,
        topic: str,
        language: str,
        feedback: str = "",
    ) -> str:

        # Demo translations for the default hackathon topic.
        # Gemini will translate arbitrary topics when available.
        topic_map = {
            "English": "Preventive health and employee wellbeing.",
            "Malay": "Kesihatan pencegahan dan kesejahteraan pekerja.",
            "Bahasa Indonesia": "Kesehatan preventif dan kesejahteraan karyawan.",
            "Thai": "สุขภาพเชิงป้องกันและสุขภาวะของพนักงาน",
            "Chinese": "预防性健康与员工福祉。"
        }

        localized_topic = topic_map.get(language, topic)

        # ====================================================
        # ENGLISH
        # ====================================================

        if language == "English":

            if platform == "LinkedIn":
                return f"""Protecting people starts with prevention.

At {brand}, we believe awareness and proactive wellbeing can help people make better-informed decisions.

Today's focus: {localized_topic}

Practical awareness, early attention and informed decisions can make an important difference in everyday wellbeing.

Learn more and explore how {brand} can support your protection needs.

#JAAssure #Wellbeing #Prevention #Insurance #Awareness"""

            elif platform == "Instagram":
                return f"""🌿 Prevention starts with awareness.

Today's focus:
{localized_topic}

Small, informed steps can support better wellbeing and help people think ahead.

Stay informed. Stay prepared. 💙

Learn more with {brand}.

#JAAssure #Wellbeing #Prevention #HealthAwareness #Insurance #StayPrepared"""

            elif platform == "X":
                return f"""Prevention starts with awareness.

{localized_topic}

Stay informed, think ahead and make decisions based on reliable information.

Learn more with {brand}.

#JAAssure #Wellbeing #Prevention"""

            elif platform == "Blog":
                return f"""# {localized_topic}

## Introduction

Prevention and awareness are important parts of building healthier and more prepared communities.

## Why It Matters

Understanding potential risks can help people make informed decisions and take practical steps early.

## Practical Approach

- Stay informed
- Pay attention to wellbeing
- Understand available protection options
- Seek professional advice when necessary

## Conclusion

Prevention begins with awareness and informed decision-making.

Learn more about {brand} and its solutions.

"""

            elif platform == "Reel":
                return f"""🎬 REEL SCRIPT

HOOK:
"What if prevention started before a problem appeared?"

MAIN MESSAGE:
Today's focus is {localized_topic}

KEY POINTS:
1. Awareness matters.
2. Early attention can support better decisions.
3. Being informed helps people prepare.

CTA:
Learn more with {brand}.

#JAAssure #Prevention #Wellbeing"""

        # ====================================================
        # MALAY
        # ====================================================

        elif language == "Malay":

            if platform == "LinkedIn":
                return f"""Kesihatan yang lebih baik bermula dengan pencegahan.

Di {brand}, kesedaran dan kesejahteraan yang proaktif boleh membantu orang ramai membuat keputusan yang lebih bermaklumat.

Fokus hari ini:
{localized_topic}

Kesedaran, perhatian awal dan keputusan yang tepat boleh memainkan peranan penting dalam kesejahteraan harian.

Ketahui lebih lanjut tentang {brand}.

#JAAssure #Kesihatan #Kesejahteraan #Pencegahan #Insurans"""

            elif platform == "Instagram":
                return f"""🌿 Pencegahan bermula dengan kesedaran.

Fokus hari ini:
{localized_topic}

Langkah kecil yang bermaklumat boleh membantu menyokong kesejahteraan yang lebih baik. 💙

Kekal bermaklumat. Kekal bersedia.

Ketahui lebih lanjut dengan {brand}.

#JAAssure #Kesihatan #Kesejahteraan #Pencegahan #Insurans"""

            elif platform == "X":
                return f"""Pencegahan bermula dengan kesedaran.

{localized_topic}

Kekal bermaklumat dan buat keputusan berdasarkan maklumat yang boleh dipercayai.

Ketahui lebih lanjut dengan {brand}.

#JAAssure #Pencegahan #Kesejahteraan"""

            elif platform == "Blog":
                return f"""# {localized_topic}

## Pengenalan

Pencegahan dan kesedaran merupakan bahagian penting dalam membina kesejahteraan yang lebih baik.

## Mengapa Ia Penting

Maklumat yang tepat boleh membantu orang ramai membuat keputusan yang lebih bermaklumat.

## Pendekatan Praktikal

- Kekal bermaklumat
- Beri perhatian kepada kesejahteraan
- Fahami pilihan perlindungan yang tersedia
- Dapatkan nasihat profesional apabila diperlukan

## Kesimpulan

Pencegahan bermula dengan kesedaran dan keputusan yang bermaklumat.

Ketahui lebih lanjut tentang {brand}."""

            elif platform == "Reel":
                return f"""🎬 SKRIP REEL

HOOK:
"Bagaimana jika pencegahan bermula sebelum masalah berlaku?"

MESEJ UTAMA:
Fokus hari ini ialah {localized_topic}

PERKARA UTAMA:
1. Kesedaran adalah penting.
2. Perhatian awal boleh membantu membuat keputusan.
3. Maklumat yang tepat membantu persediaan.

CTA:
Ketahui lebih lanjut dengan {brand}."""

        # ====================================================
        # BAHASA INDONESIA
        # ====================================================

        elif language == "Bahasa Indonesia":

            if platform == "LinkedIn":
                return f"""Perlindungan yang lebih baik dimulai dari pencegahan.

Di {brand}, kesadaran dan kesejahteraan yang proaktif dapat membantu orang membuat keputusan yang lebih tepat.

Fokus hari ini:
{localized_topic}

Kesadaran, perhatian sejak dini, dan informasi yang tepat dapat mendukung kesejahteraan sehari-hari.

Pelajari lebih lanjut tentang {brand}.

#JAAssure #Kesehatan #Kesejahteraan #Pencegahan #Asuransi"""

            elif platform == "Instagram":
                return f"""🌿 Pencegahan dimulai dari kesadaran.

Fokus hari ini:
{localized_topic}

Langkah kecil dengan informasi yang tepat dapat membantu mendukung kesejahteraan. 💙

Tetap terinformasi. Tetap siap.

Pelajari lebih lanjut bersama {brand}.

#JAAssure #Kesehatan #Kesejahteraan #Pencegahan #Asuransi"""

            elif platform == "X":
                return f"""Pencegahan dimulai dari kesadaran.

{localized_topic}

Tetap terinformasi dan buat keputusan berdasarkan informasi yang dapat dipercaya.

Pelajari lebih lanjut bersama {brand}.

#JAAssure #Pencegahan #Kesejahteraan"""

            elif platform == "Blog":
                return f"""# {localized_topic}

## Pendahuluan

Pencegahan dan kesadaran merupakan bagian penting dalam membangun kesejahteraan yang lebih baik.

## Mengapa Ini Penting

Informasi yang tepat dapat membantu masyarakat membuat keputusan yang lebih baik.

## Pendekatan Praktis

- Tetap terinformasi
- Perhatikan kesejahteraan
- Pahami pilihan perlindungan yang tersedia
- Konsultasikan dengan profesional jika diperlukan

## Kesimpulan

Pencegahan dimulai dari kesadaran dan pengambilan keputusan yang tepat.

Pelajari lebih lanjut tentang {brand}."""

            elif platform == "Reel":
                return f"""🎬 SKRIP REEL

HOOK:
"Bagaimana jika pencegahan dimulai sebelum masalah terjadi?"

PESAN UTAMA:
Fokus hari ini adalah {localized_topic}

POIN UTAMA:
1. Kesadaran itu penting.
2. Perhatian sejak dini dapat membantu.
3. Informasi yang tepat membantu persiapan.

CTA:
Pelajari lebih lanjut bersama {brand}."""

        # ====================================================
        # THAI
        # ====================================================

        elif language == "Thai":

            if platform == "LinkedIn":
                return f"""การดูแลสุขภาพที่ดีเริ่มต้นจากการป้องกัน

ที่ {brand} ความตระหนักรู้และการดูแลสุขภาพเชิงรุกสามารถช่วยให้ผู้คนตัดสินใจได้อย่างมีข้อมูลมากขึ้น

หัวข้อวันนี้:
{localized_topic}

การใส่ใจตั้งแต่เนิ่น ๆ และการได้รับข้อมูลที่เหมาะสมสามารถช่วยสนับสนุนคุณภาพชีวิตในแต่ละวัน

เรียนรู้เพิ่มเติมเกี่ยวกับ {brand}

#JAAssure #สุขภาพ #การป้องกัน #ความเป็นอยู่ที่ดี #ประกันภัย"""

            elif platform == "Instagram":
                return f"""🌿 การป้องกันเริ่มต้นจากความตระหนักรู้

หัวข้อวันนี้:
{localized_topic}

การใส่ใจเรื่องสุขภาพและการเตรียมตัวอย่างเหมาะสมสามารถช่วยสนับสนุนความเป็นอยู่ที่ดีได้ 💙

รู้ข้อมูล เตรียมพร้อม และดูแลตัวเอง

เรียนรู้เพิ่มเติมกับ {brand}

#JAAssure #สุขภาพ #การป้องกัน #ความเป็นอยู่ที่ดี #ประกันภัย"""

            elif platform == "X":
                return f"""การป้องกันเริ่มต้นจากความตระหนักรู้

{localized_topic}

รับข้อมูลที่น่าเชื่อถือและตัดสินใจอย่างรอบคอบ

เรียนรู้เพิ่มเติมกับ {brand}

#JAAssure #การป้องกัน #สุขภาพ"""

            elif platform == "Blog":
                return f"""# {localized_topic}

## บทนำ

การป้องกันและความตระหนักรู้เป็นส่วนสำคัญของการดูแลสุขภาพและความเป็นอยู่ที่ดี

## ทำไมจึงสำคัญ

ข้อมูลที่เหมาะสมสามารถช่วยให้ผู้คนตัดสินใจได้อย่างมีข้อมูลมากขึ้น

## แนวทางที่ทำได้จริง

- ติดตามข้อมูลที่น่าเชื่อถือ
- ใส่ใจสุขภาพ
- ทำความเข้าใจทางเลือกด้านการคุ้มครอง
- ขอคำแนะนำจากผู้เชี่ยวชาญเมื่อจำเป็น

## สรุป

การป้องกันเริ่มต้นจากความตระหนักรู้และการตัดสินใจอย่างมีข้อมูล

เรียนรู้เพิ่มเติมเกี่ยวกับ {brand}"""

            elif platform == "Reel":
                return f"""🎬 สคริปต์ REEL

HOOK:
"ถ้าการป้องกันเริ่มต้นก่อนที่จะเกิดปัญหาจะเป็นอย่างไร?"

ข้อความหลัก:
หัวข้อวันนี้คือ {localized_topic}

ประเด็นสำคัญ:
1. ความตระหนักรู้มีความสำคัญ
2. การใส่ใจตั้งแต่เนิ่น ๆ ช่วยสนับสนุนการตัดสินใจ
3. ข้อมูลที่เหมาะสมช่วยให้เตรียมตัวได้ดีขึ้น

CTA:
เรียนรู้เพิ่มเติมกับ {brand}"""

        # ====================================================
        # CHINESE
        # ====================================================

        elif language == "Chinese":

            if platform == "LinkedIn":
                return f"""更好的健康保障，从预防开始。

在 {brand}，提高健康意识和主动关注员工福祉，可以帮助人们做出更加明智的决定。

今天的主题：
{localized_topic}

及时关注、获取可靠信息并采取适当措施，有助于支持日常健康与福祉。

了解更多关于 {brand} 的信息。

#JAAssure #健康 #预防 #员工福祉 #保险"""

            elif platform == "Instagram":
                return f"""🌿 预防，从提高健康意识开始。

今天的主题：
{localized_topic}

从小事做起，关注健康并提前做好准备。💙

保持了解，做好准备。

了解更多 {brand} 的信息。

#JAAssure #健康 #预防 #员工福祉 #保险"""

            elif platform == "X":
                return f"""预防始于健康意识。

{localized_topic}

获取可靠信息，并根据实际情况做出明智决定。

了解更多 {brand} 的信息。

#JAAssure #预防 #健康"""

            elif platform == "Blog":
                return f"""# {localized_topic}

## 引言

预防和健康意识是支持个人与员工福祉的重要组成部分。

## 为什么重要

可靠的信息可以帮助人们更好地了解风险，并做出更加明智的决定。

## 实用方法

- 关注可靠的信息
- 重视健康与福祉
- 了解可获得的保障选择
- 必要时咨询专业人士

## 结论

预防始于健康意识和明智决策。

了解更多关于 {brand} 的信息。"""

            elif platform == "Reel":
                return f"""🎬 REEL 视频脚本

HOOK：
"如果预防可以在问题发生之前开始呢？"

核心信息：
今天的主题是 {localized_topic}

主要内容：
1. 健康意识非常重要。
2. 提前关注有助于更好地做出决定。
3. 可靠的信息有助于做好准备。

CTA：
了解更多 {brand} 的信息。"""

        # ====================================================
        # FINAL FALLBACK
        # ====================================================

        return f"""JA Assure Marketing Content

Brand: {brand}
Platform: {platform}
Language: {language}

{topic}

Please review and approve this content before publishing.
"""


# ============================================================
# COMPLIANCE AGENT
# ============================================================

class ComplianceAgent:
    def __init__(self, gemini=None):
        self.gemini = gemini or GeminiService()

    def run(self, content: str, brand: str, topic: str) -> Dict[str, Any]:

        prompt = f"""
You are an insurance marketing compliance checker.

Brand:
{brand}

Topic:
{topic}

Content:
{content}

Check for:
1. Unsupported insurance claims
2. Guaranteed outcomes
3. Misleading statements
4. Invented statistics
5. Unsupported coverage statements
6. Unverified regulatory/legal claims
7. Unrealistic promises

Return JSON:
{{
    "status": "PASS" or "FAIL",
    "issues": [],
    "safe_edits": []
}}
"""

        try:
            result = self.gemini.json_generate(prompt)

            if result and isinstance(result, dict) and "status" in result:
                status = str(result.get("status", "PASS")).upper()

                if status not in ["PASS", "FAIL"]:
                    status = "PASS"

                return {
                    "status": status,
                    "issues": result.get("issues", []),
                    "safe_edits": result.get("safe_edits", [])
                }

        except Exception as e:
            print(f"Compliance Agent fallback: {e}")

        # Reliable local compliance check
        risky_terms = [
            "guaranteed",
            "guarantee",
            "100% covered",
            "always covered",
            "no risk",
            "best insurance",
            "number one",
            "cure",
            "certain cure",
            "guaranteed protection",
        ]

        found = []

        content_lower = content.lower()

        for term in risky_terms:
            if term.lower() in content_lower:
                found.append(
                    f"Potentially risky wording detected: '{term}'"
                )

        if found:
            return {
                "status": "FAIL",
                "issues": found,
                "safe_edits": [
                    "Replace absolute claims with neutral educational wording.",
                    "Verify product and coverage information before publishing."
                ]
            }

        return {
            "status": "PASS",
            "issues": [],
            "safe_edits": [
                "Human approval is still required before publishing."
            ]
        }


# ============================================================
# LEAD AGENT
# ============================================================

class LeadAgent:
    def __init__(self, gemini=None):
        self.gemini = gemini or GeminiService()

    def run(
        self,
        brand: str,
        target_industry: str,
        location: str,
        count: int = 5,
    ) -> List[Dict[str, Any]]:

        prompt = f"""
You are a B2B lead generation agent for JA Assure.

Brand:
{brand}

Target industry:
{target_industry}

Location:
{location}

Find up to {count} potential business prospects using public information.

Do not provide:
- Private personal information
- Sensitive personal information
- Invented businesses
- Invented websites

Return JSON array with:
name
company
industry
location
fit_score
source_url
why_fit
outreach
"""

        try:
            result = self.gemini.json_generate(prompt)

            if isinstance(result, list):
                return result

            if isinstance(result, dict) and isinstance(result.get("leads"), list):
                return result["leads"]

        except Exception as e:
            print(f"Lead Agent fallback: {e}")

        # Demo leads so the application never becomes blank
        demo_companies = {
            "Doctors / Clinics": [
                "Demo Medical Clinic",
                "Demo Family Healthcare",
                "Demo Specialist Centre",
            ],
            "Jewellers": [
                "Demo Jewellery Group",
                "Demo Jewellers",
                "Demo Gold House",
            ],
            "SMEs": [
                "Demo Business Solutions",
                "Demo Enterprise Group",
                "Demo SME Services",
            ],
            "Couriers / Logistics": [
                "Demo Logistics",
                "Demo Courier Services",
                "Demo Transport Solutions",
            ],
        }

        names = demo_companies.get(
            target_industry,
            ["Demo Business"]
        )

        leads = []

        for i in range(min(count, len(names))):
            company = names[i]

            leads.append({
                "name": "Public Business Contact",
                "company": company,
                "industry": target_industry,
                "location": location,
                "fit_score": 70 - (i * 5),
                "source_url": "Public-source research required",
                "why_fit": (
                    f"Demo prospect for {target_industry} "
                    f"in {location}."
                ),
                "outreach": (
                    f"Hello, we are exploring how {brand} "
                    f"solutions could support businesses in "
                    f"{target_industry}. We would be happy to "
                    f"share more information."
                )
            })

        return leads