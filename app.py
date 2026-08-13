import streamlit as st
from google import genai
from google.genai import types

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #0e1117;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}

.hero {
    padding: 30px;
    border-radius: 20px;
    background: linear-gradient(135deg, #172554, #1e40af);
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 40px;
    margin-bottom: 8px;
}

.hero p {
    font-size: 17px;
    opacity: 0.9;
}

.study-card {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #30363d;
    background: #161b22;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# GEMINI API
# ============================================================

try:

    API_KEY = st.secrets["GEMINI_API_KEY"]

except Exception:

    st.error("""
    🔐 Gemini API key is missing.

    Go to:

    Streamlit → Manage app → Settings → Secrets

    and add:

    GEMINI_API_KEY = "YOUR_API_KEY"
    """)

    st.stop()


try:

    client = genai.Client(api_key=API_KEY)

except Exception as e:

    st.error("❌ Gemini client could not be initialized.")

    st.code(str(e))

    st.stop()


MODEL = "gemini-3.1-flash-lite"

# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "notes" not in st.session_state:
    st.session_state.notes = ""

if "quiz" not in st.session_state:
    st.session_state.quiz = ""

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">

<h1>📚 StudyMate AI</h1>

<p>
Your intelligent study companion for understanding concepts,
creating notes, practicing questions, and preparing for exams.
</p>

</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🎓 Study Settings")

    subject = st.selectbox(
        "Select Subject",
        [
            "General",
            "Artificial Intelligence",
            "Advanced DBMS",
            "C++ Programming",
            "Python Programming",
            "Web Development",
            "Mathematics",
            "Statistics",
            "Other"
        ]
    )

    level = st.selectbox(
        "Study Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )

    style = st.selectbox(
        "Explanation Style",
        [
            "Simple & Easy",
            "Detailed",
            "Exam-Oriented",
            "Step-by-Step",
            "With Examples"
        ]
    )

    st.divider()

    st.markdown("### ⚡ Quick Actions")

    create_notes = st.button(
        "📝 Create Notes",
        use_container_width=True
    )

    practice_questions = st.button(
        "❓ Practice Questions",
        use_container_width=True
    )

    generate_quiz = st.button(
        "🧠 Generate Quiz",
        use_container_width=True
    )

    explain_simple = st.button(
        "📖 Explain Simply",
        use_container_width=True
    )

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.rerun()

# ============================================================
# AI FUNCTION
# ============================================================

def ask_gemini(user_prompt):

    system_instruction = f"""
You are StudyMate AI, a professional AI study assistant.

Your purpose is ONLY academic learning and education.

Student subject:
{subject}

Student level:
{level}

Preferred explanation style:
{style}

STRICT EDUCATIONAL RULES:

1. Only answer study-related and academic questions.

2. You may help with:
   - Concepts
   - Programming
   - Mathematics
   - Science
   - Artificial Intelligence
   - Databases
   - Exam preparation
   - Assignments
   - Revision
   - Practice questions
   - Notes
   - Examples
   - Problem solving

3. If the question is unrelated to education,
   respond:

   "I'm StudyMate AI, designed specifically for
   academic learning. Please ask me a study-related
   question."

4. Explain concepts clearly.

5. Use examples when useful.

6. For programming:
   Explain the logic and provide clean code when needed.

7. For mathematics:
   Show the solution step-by-step.

8. For exam preparation:
   Highlight important points.

9. Do not help students cheat during a live examination.

10. Do not invent facts.

11. Keep answers structured and easy to revise.

Student request:

{user_prompt}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            max_output_tokens=1500
        )
    )

    return response.text


# ============================================================
# TABS
# ============================================================

tab_chat, tab_notes, tab_quiz = st.tabs([
    "💬 Study Assistant",
    "📝 Notes Generator",
    "🧠 Quiz Generator"
])

# ============================================================
# STUDY ASSISTANT
# ============================================================

with tab_chat:

    st.subheader("💬 Ask StudyMate")

    st.caption(
        "Ask questions and get clear, structured explanations."
    )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    question = st.chat_input(
        "Ask a study-related question..."
    )

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner("📚 Thinking..."):

                try:

                    conversation = ""

                    for message in st.session_state.messages[-10:]:

                        conversation += (
                            message["role"].upper()
                            + ": "
                            + message["content"]
                            + "\n\n"
                        )

                    answer = ask_gemini(
                        f"""
Conversation history:

{conversation}

Answer the latest student question.
"""
                    )

                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:

                    st.error(
                        "❌ Gemini request failed."
                    )

                    st.warning(
                        "The exact error is shown below. "
                        "This will tell us whether the problem "
                        "is the API key, model, quota, or permissions."
                    )

                    st.code(str(e))


# ============================================================
# NOTES GENERATOR
# ============================================================

with tab_notes:

    st.subheader("📝 Smart Notes Generator")

    topic = st.text_input(
        "Enter Topic",
        placeholder="Example: Normalization in DBMS"
    )

    notes_type = st.selectbox(
        "Notes Type",
        [
            "Short Revision Notes",
            "Detailed Notes",
            "Exam Preparation Notes"
        ]
    )

    if st.button(
        "✨ Generate Notes",
        use_container_width=True
    ):

        if not topic.strip():

            st.warning(
                "Please enter a topic first."
            )

        else:

            prompt = f"""
Create professional study notes.

Subject:
{subject}

Topic:
{topic}

Notes type:
{notes_type}

Student level:
{level}

Include:

• Definition
• Key concepts
• Important points
• Examples
• Applications where relevant
• Advantages and disadvantages where relevant
• Important formulas or syntax
• Exam-focused points
• Quick revision summary

Make the notes clear, accurate,
well-structured and easy to study.
"""

            with st.spinner(
                "📝 Creating study notes..."
            ):

                try:

                    result = ask_gemini(prompt)

                    st.session_state.notes = result

                except Exception as e:

                    st.error(
                        "❌ Gemini request failed."
                    )

                    st.code(str(e))

    if st.session_state.notes:

        st.divider()

        st.markdown(
            st.session_state.notes
        )


# ============================================================
# QUIZ GENERATOR
# ============================================================

with tab_quiz:

    st.subheader("🧠 Practice Quiz")

    quiz_topic = st.text_input(
        "Quiz Topic",
        placeholder="Example: C++ Control Statements"
    )

    col1, col2 = st.columns(2)

    with col1:

        question_count = st.slider(
            "Number of Questions",
            3,
            15,
            5
        )

    with col2:

        difficulty = st.selectbox(
            "Difficulty",
            [
                "Easy",
                "Medium",
                "Hard",
                "Mixed"
            ]
        )

    if st.button(
        "🎯 Generate Quiz",
        use_container_width=True
    ):

        if not quiz_topic.strip():

            st.warning(
                "Please enter a quiz topic."
            )

        else:

            prompt = f"""
Create an academic practice quiz.

Subject:
{subject}

Topic:
{quiz_topic}

Difficulty:
{difficulty}

Number of questions:
{question_count}

Create multiple-choice questions.

Format:

Question 1

A. Option
B. Option
C. Option
D. Option

Continue for all questions.

After all questions provide:

ANSWER KEY

Then provide short explanations
for each correct answer.

This quiz is strictly for academic practice.
"""

            with st.spinner(
                "🧠 Creating your quiz..."
            ):

                try:

                    result = ask_gemini(prompt)

                    st.session_state.quiz = result

                except Exception as e:

                    st.error(
                        "❌ Gemini request failed."
                    )

                    st.code(str(e))

    if st.session_state.quiz:

        st.divider()

        st.markdown(
            st.session_state.quiz
        )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "📚 StudyMate AI • Powered by Gemini • "
    "For educational purposes"
)
