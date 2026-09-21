from typing import Any, Dict

from .agents import (
    ResearchAgent,
    ContentAgent,
    ComplianceAgent,
    LeadAgent,
)
from .database import SessionLocal
from .models import (
    Content,
    ComplianceResult,
    Feedback,
    Lead,
    Review,
)


# ============================================================
# MARKETING WORKFLOW
# ============================================================

class MarketingWorkflow:

    def __init__(self, gemini=None):
        self.research_agent = ResearchAgent(gemini)
        self.content_agent = ContentAgent(gemini)
        self.compliance_agent = ComplianceAgent(gemini)
        self.lead_agent = LeadAgent(gemini)

    # --------------------------------------------------------
    # GET PREVIOUS FEEDBACK
    # --------------------------------------------------------

    def get_feedback_memory(
        self,
        brand: str,
        platform: str,
    ) -> str:

        db = SessionLocal()

        try:
            rows = (
                db.query(Feedback)
                .join(Content, Feedback.content_id == Content.id)
                .filter(
                    Content.brand == brand,
                    Content.platform == platform
                )
                .order_by(Feedback.created_at.desc())
                .limit(10)
                .all()
            )

            if not rows:
                return ""

            feedback_lines = []

            for row in rows:
                line = row.reason

                if row.details:
                    line += f": {row.details}"

                feedback_lines.append(line)

            return "\n".join(feedback_lines)

        finally:
            db.close()

    # --------------------------------------------------------
    # MAIN WORKFLOW
    # --------------------------------------------------------

    def run(
        self,
        gemini=None,
        brand: str = "",
        platform: str = "LinkedIn",
        objective: str = "Create Content",
        topic: str = "",
        language: str = "English",
    ) -> Dict[str, Any]:

        db = SessionLocal()

        try:

            # ================================================
            # 1. FEEDBACK MEMORY
            # ================================================

            previous_feedback = self.get_feedback_memory(
                brand,
                platform
            )

            # ================================================
            # 2. RESEARCH
            # ================================================

            research = self.research_agent.run(
                brand=brand,
                platform=platform,
                topic=topic,
                language=language,
            )

            # ================================================
            # 3. CONTENT GENERATION
            # ================================================

            content_text = self.content_agent.run(
                brand=brand,
                platform=platform,
                objective=objective,
                topic=topic,
                language=language,
                research=research,
                feedback=previous_feedback,
            )

            # Never allow empty content
            if not content_text or not content_text.strip():
                content_text = self._absolute_fallback(
                    brand,
                    platform,
                    topic,
                    language,
                )

            # ================================================
            # 4. STORE CONTENT
            # ================================================

            content_row = Content(
                brand=brand,
                platform=platform,
                objective=objective,
                topic=topic,
                language=language,
                content=content_text,
                status="generated",
            )

            db.add(content_row)
            db.commit()
            db.refresh(content_row)

            # ================================================
            # 5. COMPLIANCE
            # ================================================

            compliance = self.compliance_agent.run(
                content=content_text,
                brand=brand,
                topic=topic,
            )

            compliance_status = compliance.get(
                "status",
                "PASS"
            )

            compliance_issues = compliance.get(
                "issues",
                []
            )

            if not isinstance(compliance_issues, list):
                compliance_issues = [str(compliance_issues)]

            compliance_row = ComplianceResult(
                content_id=content_row.id,
                status=compliance_status,
                issues="\n".join(
                    str(x) for x in compliance_issues
                ),
            )

            db.add(compliance_row)
            db.commit()

            # ================================================
            # 6. FINAL RESPONSE
            # ================================================

            return {
                "content_id": content_row.id,
                "research": research,
                "content": content_text,
                "compliance_status": compliance_status,
                "compliance_issues": compliance_issues,
                "language": language,
                "demo_mode": False,
            }

        except Exception as e:

            db.rollback()

            print(
                f"\nWORKFLOW ERROR: "
                f"{type(e).__name__}: {e}\n"
            )

            # Last-resort content so UI never stays blank
            fallback = self._absolute_fallback(
                brand,
                platform,
                topic,
                language,
            )

            try:
                content_row = Content(
                    brand=brand,
                    platform=platform,
                    objective=objective,
                    topic=topic,
                    language=language,
                    content=fallback,
                    status="demo",
                )

                db.add(content_row)
                db.commit()
                db.refresh(content_row)

                return {
                    "content_id": content_row.id,
                    "research": (
                        "Demo research mode is active. "
                        "The external AI service was unavailable."
                    ),
                    "content": fallback,
                    "compliance_status": "PASS",
                    "compliance_issues": [],
                    "language": language,
                    "demo_mode": True,
                }

            except Exception as final_error:

                print(
                    f"FINAL DATABASE ERROR: "
                    f"{type(final_error).__name__}: "
                    f"{final_error}"
                )

                return {
                    "content_id": 0,
                    "research": (
                        "Demo research mode is active."
                    ),
                    "content": fallback,
                    "compliance_status": "PASS",
                    "compliance_issues": [],
                    "language": language,
                    "demo_mode": True,
                }

        finally:
            db.close()

    # --------------------------------------------------------
    # LEAD GENERATION
    # --------------------------------------------------------

    def generate_leads(
        self,
        brand: str,
        target_industry: str,
        location: str,
        count: int = 5,
    ):

        leads = self.lead_agent.run(
            brand=brand,
            target_industry=target_industry,
            location=location,
            count=count,
        )

        db = SessionLocal()

        try:

            saved = []

            for item in leads:

                lead = Lead(
                    name=item.get("name", ""),
                    company=item.get("company", ""),
                    industry=item.get("industry", target_industry),
                    location=item.get("location", location),
                    fit_score=int(
                        item.get("fit_score", 0) or 0
                    ),
                    source_url=item.get("source_url", ""),
                    outreach=item.get("outreach", ""),
                )

                db.add(lead)

                saved.append(item)

            db.commit()

            return saved

        except Exception as e:

            db.rollback()

            print(
                f"Lead storage error: "
                f"{type(e).__name__}: {e}"
            )

            return leads

        finally:
            db.close()

    # --------------------------------------------------------
    # REVIEW
    # --------------------------------------------------------

    def save_review(
        self,
        content_id: int,
        decision: str,
        comments: str = "",
        edited_content: str = "",
    ):

        db = SessionLocal()

        try:

            row = Review(
                content_id=content_id,
                decision=decision,
                comments=comments,
            )

            db.add(row)

            # If human edited the content,
            # save the edited version.
            if decision == "edit" and edited_content:

                content = (
                    db.query(Content)
                    .filter(Content.id == content_id)
                    .first()
                )

                if content:
                    content.content = edited_content
                    content.status = "edited"

            elif decision == "approve":

                content = (
                    db.query(Content)
                    .filter(Content.id == content_id)
                    .first()
                )

                if content:
                    content.status = "approved"

            elif decision == "reject":

                content = (
                    db.query(Content)
                    .filter(Content.id == content_id)
                    .first()
                )

                if content:
                    content.status = "rejected"

            db.commit()

            return {
                "status": "Review saved successfully."
            }

        except Exception as e:

            db.rollback()

            return {
                "status": f"Review error: {e}"
            }

        finally:
            db.close()

    # --------------------------------------------------------
    # FEEDBACK
    # --------------------------------------------------------

    def save_feedback(
        self,
        content_id: int,
        reason: str,
        details: str = "",
    ):

        db = SessionLocal()

        try:

            row = Feedback(
                content_id=content_id,
                reason=reason,
                details=details,
            )

            db.add(row)
            db.commit()

            return {
                "status": "Feedback stored in SQLite memory."
            }

        except Exception as e:

            db.rollback()

            return {
                "status": f"Feedback error: {e}"
            }

        finally:
            db.close()

    # --------------------------------------------------------
    # ABSOLUTE FALLBACK
    # --------------------------------------------------------

    def _absolute_fallback(
        self,
        brand: str,
        platform: str,
        topic: str,
        language: str,
    ) -> str:

        translations = {

            "English":
                "Preventive health and employee wellbeing.",

            "Malay":
                "Kesihatan pencegahan dan kesejahteraan pekerja.",

            "Bahasa Indonesia":
                "Kesehatan preventif dan kesejahteraan karyawan.",

            "Thai":
                "สุขภาพเชิงป้องกันและสุขภาวะของพนักงาน",

            "Chinese":
                "预防性健康与员工福祉。",
        }

        localized_topic = translations.get(
            language,
            topic
        )

        if language == "Malay":

            return f"""🌿 Kesedaran adalah langkah pertama ke arah kesejahteraan yang lebih baik.

Fokus:
{localized_topic}

Maklumat yang tepat dan perhatian awal boleh membantu orang ramai membuat keputusan yang lebih bermaklumat.

Ketahui lebih lanjut dengan {brand}.

#JAAssure #Kesihatan #Kesejahteraan #Pencegahan"""

        if language == "Bahasa Indonesia":

            return f"""🌿 Kesadaran adalah langkah awal menuju kesejahteraan yang lebih baik.

Fokus:
{localized_topic}

Informasi yang tepat dan perhatian sejak dini dapat membantu masyarakat membuat keputusan yang lebih tepat.

Pelajari lebih lanjut bersama {brand}.

#JAAssure #Kesehatan #Kesejahteraan #Pencegahan"""

        if language == "Thai":

            return f"""🌿 ความตระหนักรู้คือจุดเริ่มต้นของความเป็นอยู่ที่ดี

หัวข้อ:
{localized_topic}

ข้อมูลที่เหมาะสมและการใส่ใจตั้งแต่เนิ่น ๆ สามารถช่วยให้ผู้คนตัดสินใจได้ดีขึ้น

เรียนรู้เพิ่มเติมกับ {brand}

#JAAssure #สุขภาพ #การป้องกัน #ความเป็นอยู่ที่ดี"""

        if language == "Chinese":

            return f"""🌿 提高健康意识，是迈向更好生活的重要一步。

主题：
{localized_topic}

可靠的信息和及时的关注，可以帮助人们做出更加明智的决定。

了解更多 {brand} 的信息。

#JAAssure #健康 #预防 #员工福祉"""

        return f"""🌿 Awareness is an important first step toward better wellbeing.

Today's focus:
{localized_topic}

Reliable information and early attention can help people make more informed decisions.

Learn more with {brand}.

#JAAssure #Wellbeing #Prevention #Awareness"""