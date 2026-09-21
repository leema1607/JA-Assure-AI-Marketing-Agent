import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

if "BACKEND_URL" is st.secrets:
    BACKEND = st.secrets.BACKEND_URL
else:
    BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="JA Assure AI Marketing Agent",
    page_icon="🛡️",
    layout="wide"
)


# ---------------------------------------------------------
# WORKFLOW FUNCTION
# ---------------------------------------------------------

def run_workflow():
    try:
        with st.spinner(
            f"Generating content in {st.session_state.language}..."
        ):
            r = requests.post(
                f"{BACKEND}/workflow",
                json={
                    "brand": st.session_state.brand,
                    "platform": st.session_state.platform,
                    "objective": st.session_state.objective,
                    "topic": st.session_state.topic,
                    "language": st.session_state.language,
                },
                timeout=180,
            )

            r.raise_for_status()

            st.session_state.result = r.json()

    except Exception as e:
        st.session_state.workflow_error = str(e)


# ---------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------

st.title("🛡️ JA ASSURE AI MARKETING AGENT")

st.caption(
    "Research → Content → Compliance → Human Review → Feedback Learning"
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "result" not in st.session_state:
    st.session_state.result = None

if "workflow_error" not in st.session_state:
    st.session_state.workflow_error = None


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.header("Campaign")

    brand = st.selectbox(
        "Brand",
        ["DoctorShield", "Jade", "Jaguar Transit"],
        key="brand"
    )

    platform = st.selectbox(
        "Platform",
        ["LinkedIn", "Instagram", "X", "Blog", "Reel"],
        key="platform"
    )

    objective = st.selectbox(
        "Objective",
        [
            "Create Content",
            "Awareness",
            "Lead Generation",
            "Product Education",
            "Engagement"
        ],
        key="objective"
    )

    language = st.selectbox(
        "🌍 Language",
        [
            "English",
            "Malay",
            "Bahasa Indonesia",
            "Thai",
            "Chinese"
        ],
        key="language",
        on_change=run_workflow
    )

    topic = st.text_area(
        "Topic / Request",
        "Preventive health and employee wellbeing.",
        key="topic"
    )


# ---------------------------------------------------------
# MANUAL RUN BUTTON
# ---------------------------------------------------------

if st.button(
    "🚀 Run AI Workflow",
    type="primary"
):

    run_workflow()


# ---------------------------------------------------------
# ERROR
# ---------------------------------------------------------

if st.session_state.workflow_error:

    st.error(
        f"Workflow error: {st.session_state.workflow_error}"
    )

    st.session_state.workflow_error = None


# ---------------------------------------------------------
# DISPLAY RESULT
# ---------------------------------------------------------

result = st.session_state.result


if result:

    content_id = result["content_id"]

    st.success(
        f"Content generated in: {result.get('language', language)}"
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🔎 Research",
            "✍️ Content",
            "🛡️ Compliance",
            "👩‍💼 Human Review"
        ]
    )


    # -----------------------------------------------------
    # RESEARCH
    # -----------------------------------------------------

    with tab1:

        st.subheader("Research Agent Output")

        st.write(
            result["research"]
        )


    # -----------------------------------------------------
    # CONTENT
    # -----------------------------------------------------

    with tab2:

        st.subheader("AI Generated Content")

        st.text_area(
            "Content",
            result["content"],
            height=350,
            key=f"generated_content_{content_id}"
        )


    # -----------------------------------------------------
    # COMPLIANCE
    # -----------------------------------------------------

    with tab3:

        status = result["compliance_status"]

        if status == "PASS":

            st.success(
                "Compliance check passed — human approval is still required."
            )

        else:

            st.error(
                "Compliance check failed / needs attention."
            )

        if result["compliance_issues"]:

            for issue in result["compliance_issues"]:

                st.warning(issue)


    # -----------------------------------------------------
    # HUMAN REVIEW
    # -----------------------------------------------------

    with tab4:

        st.subheader(
            f"Review Content #{content_id}"
        )

        decision = st.radio(
            "Decision",
            ["approve", "edit", "reject"],
            horizontal=True
        )

        comments = st.text_area(
            "Comment / rejection reason"
        )

        edited = ""

        if decision == "edit":

            edited = st.text_area(
                "Edited content",
                value=result["content"],
                height=300
            )


        if st.button("Save Review"):

            try:

                r = requests.post(
                    f"{BACKEND}/review",
                    json={
                        "content_id": content_id,
                        "decision": decision,
                        "comments": comments,
                        "edited_content": edited,
                    },
                    timeout=60,
                )

                r.raise_for_status()

                st.success(
                    r.json()["status"]
                )

                if decision in ["reject", "edit"]:

                    st.info(
                        "Store the specific lesson below so future generations can use it."
                    )

            except Exception as e:

                st.error(
                    f"Review error: {e}"
                )


        st.divider()

        st.subheader("Feedback Memory")

        reason = st.selectbox(
            "Feedback reason",
            [
                "Too salesy",
                "Incorrect information",
                "Wrong brand tone",
                "Wrong CTA",
                "Compliance concern",
                "Other"
            ]
        )

        details = st.text_area(
            "Lesson learned"
        )


        if st.button("🧠 Save Feedback"):

            try:

                r = requests.post(
                    f"{BACKEND}/feedback",
                    json={
                        "content_id": content_id,
                        "reason": reason,
                        "details": details,
                    },
                    timeout=60,
                )

                r.raise_for_status()

                st.success(
                    "Feedback stored in SQLite memory."
                )

            except Exception as e:

                st.error(
                    f"Feedback error: {e}"
                )


# ---------------------------------------------------------
# LEAD GENERATION
# ---------------------------------------------------------

st.divider()

col1, col2 = st.columns(2)


with col1:

    st.subheader("🎯 Lead Generation")

    lead_industry = st.selectbox(
        "Target industry",
        [
            "Doctors / Clinics",
            "Jewellers",
            "SMEs",
            "Couriers / Logistics"
        ]
    )

    lead_location = st.text_input(
        "Location",
        "Malaysia"
    )

    lead_count = st.slider(
        "Number of leads",
        1,
        10,
        5
    )


    if st.button("Find Prospects"):

        with st.spinner(
            "Searching public sources..."
        ):

            try:

                r = requests.post(
                    f"{BACKEND}/generate-leads",
                    json={
                        "brand": brand,
                        "target_industry": lead_industry,
                        "location": lead_location,
                        "count": lead_count,
                    },
                    timeout=180,
                )

                r.raise_for_status()

                data = r.json()

                for lead in data.get("leads", []):

                    with st.expander(
                        f"{lead.get('company', 'Unknown')} — Fit {lead.get('fit_score', 0)}"
                    ):

                        st.write(
                            lead.get("why_fit", "")
                        )

                        st.write(
                            lead.get("outreach", "")
                        )

                        st.caption(
                            lead.get("source_url", "")
                        )

            except Exception as e:

                st.error(
                    f"Lead generation error: {e}"
                )


# ---------------------------------------------------------
# STORED DATA
# ---------------------------------------------------------

with col2:

    st.subheader("📚 Stored Data")


    if st.button("Refresh Content History"):

        try:

            r = requests.get(
                f"{BACKEND}/content",
                timeout=30
            )

            r.raise_for_status()

            st.dataframe(
                r.json(),
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"Could not load history: {e}"
            )


    if st.button("Refresh Feedback Memory"):

        try:

            r = requests.get(
                f"{BACKEND}/feedback",
                timeout=30
            )

            r.raise_for_status()

            st.dataframe(
                r.json(),
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"Could not load feedback: {e}"
            )