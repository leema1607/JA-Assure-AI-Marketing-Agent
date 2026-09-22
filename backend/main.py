from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Content, Review, Feedback, ComplianceResult, Lead
from .schemas import (
    WorkflowRequest, ReviewRequest, FeedbackRequest,
    LeadRequest, ComplianceRequest
)
from .gemini import GeminiService
from .agents import LeadAgent, ComplianceAgent
from .workflow import MarketingWorkflow

Base.metadata.create_all(bind=engine)

app = FastAPI(title="JA Assure AI Marketing Agent", version="1.0.0")

def get_ai():
    return GeminiService()

@app.get("/")
def root():
    return {"name": "JA Assure AI Marketing Agent", "status": "running"}

@app.post("/workflow")
def workflow(req: WorkflowRequest, db: Session = Depends(get_db)):
    try:
        return MarketingWorkflow(get_ai()).run(
            db, req.brand, req.platform, req.objective, req.topic, req.language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/research")
def research(req: WorkflowRequest):
    try:
        from .agents import ResearchAgent
        return {"research": ResearchAgent(get_ai()).run(
            req.brand, req.topic, req.platform, req.language
        )}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-content")
def generate_content(req: WorkflowRequest, db: Session = Depends(get_db)):
    try:
        from .agents import ResearchAgent, ContentAgent
        ai = get_ai()
        r = ResearchAgent(ai).run(req.brand, req.topic, req.platform, req.language)
        f = MarketingWorkflow(ai).feedback_memory(db, req.brand, req.platform)
        c = ContentAgent(ai).run(
            req.brand, req.platform, req.objective, req.topic, req.language, r, f
        )
        return {"research": r, "content": c}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compliance-check")
def compliance(req: ComplianceRequest):
    try:
        result = ComplianceAgent(get_ai()).run(req.content, "JA Assure", "")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/review")
def review(req: ReviewRequest, db: Session = Depends(get_db)):
    content = db.get(Content, req.content_id)
    if not content:
        raise HTTPException(404, "Content not found")

    if req.decision == "edit" and req.edited_content.strip():
        content.content = req.edited_content
        content.status = "edited_pending_approval"
    elif req.decision == "approve":
        content.status = "approved"
    else:
        content.status = "rejected"

    db.add(Review(
        content_id=content.id,
        decision=req.decision,
        comments=req.comments,
    ))
    db.commit()
    return {"content_id": content.id, "status": content.status}

@app.post("/feedback")
def feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    content = db.get(Content, req.content_id)
    if not content:
        raise HTTPException(404, "Content not found")
    db.add(Feedback(
        content_id=req.content_id,
        reason=req.reason,
        details=req.details,
    ))
    db.commit()
    return {"message": "Feedback stored", "content_id": req.content_id}

@app.post("/generate-leads")
def generate_leads(req: LeadRequest, db: Session = Depends(get_db)):
    try:
        result = LeadAgent(get_ai()).run(
            req.brand, req.target_industry, req.location, req.count
        )
        
        if isinstance(result, list):
            leads = result
        else:
            leads = result.get("leads", [])

        for item in leads:
            db.add(Lead(
                name=item.get("name", ""),
                company=item.get("company", ""),
                industry=item.get("industry", ""),
                location=item.get("location", ""),
                fit_score=float(item.get("fit_score", 0)),
                source_url=item.get("source_url", ""),
                outreach=item.get("outreach", ""),
            ))
        db.commit()
        return {"leads": leads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/content")
def get_content(db: Session = Depends(get_db)):
    rows = db.query(Content).order_by(Content.created_at.desc()).limit(50).all()
    return [
        {
            "id": r.id, "brand": r.brand, "platform": r.platform,
            "topic": r.topic, "language": r.language,
            "content": r.content, "status": r.status,
            "created_at": r.created_at.isoformat(),
        } for r in rows
    ]

@app.get("/leads")
def get_leads(db: Session = Depends(get_db)):
    rows = db.query(Lead).order_by(Lead.fit_score.desc()).limit(100).all()
    return [
        {
            "id": r.id, "name": r.name, "company": r.company,
            "industry": r.industry, "location": r.location,
            "fit_score": r.fit_score, "source_url": r.source_url,
            "outreach": r.outreach,
        } for r in rows
    ]

@app.get("/feedback")
def get_feedback(db: Session = Depends(get_db)):
    rows = db.query(Feedback).order_by(Feedback.created_at.desc()).limit(100).all()
    return [
        {"id": r.id, "content_id": r.content_id, "reason": r.reason,
         "details": r.details, "created_at": r.created_at.isoformat()}
        for r in rows
    ]
