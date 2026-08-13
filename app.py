
import streamlit as st
from google import genai

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    .main {
        background-color: #f8fafc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .hero {
        padding: 28px;
        border-radius: 18px;
        background: linear-gradient(135deg, #172554, #1e3a8a);
        color: white;
        margin-bottom: 25px;
    }

    .hero h1 {
        font-size: 38px;
        margin-bottom: 8px;
    }

    .hero p {
        font-size: 17px;
        opacity: 0.9;
    }

    .feature-card {
        padding: 18px;
        border-radius: 14px;
        background-color: white;
        border: 1px solid #e5e7eb;
        margin-bottom: 10px;
    }

    .study-tip {
        padding: 16px;
        border-left: 4px solid #2563eb;
        background-color: #eff6ff;
        border-radius: 8px;
        margin-top: 15px;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

</style>
""", unsafe_allow_html=True)

# ============================================================
# GEMINI CONFIGURATION
# ============================================================

api_key = None

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not api_key:
    st.error(
        "Gemini API key is not configured. "
        "Add GEMINI_API_KEY in Streamlit Secrets."
    )
    st.stop()

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-2.5-flash"

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
        Your interactive AI-powered study assistant for
        understanding concepts, creating notes, practicing questions,
        and preparing for exams.
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
            "C++ Programming",
            "Artificial Intelligence",
            "Advanced DBMS",
            "Python Programming",
            "Web Development",
            "Mathematics",
            "Statistics",
            "Other"
        ]
    )

    study_level = st.selectbox(
        "Study Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )

    response_style = st.selectbox(
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

    st.subheader("⚡ Quick Actions")

    if st.button("📝 Create Notes", use_container_width=True):
        st.session_state.quick_action = "notes"

    if st.button("❓ Practice Questions", use_container_width=True):
        st.session_state.quick_action = "questions"

    if st.button("🧠 Generate Quiz", use_container_width=True):
        st.session_state.quick_action = "quiz"

    if st.button("📖 Explain Simply", use_container_width=True):
        st.session_state.quick_action = "simple"

    st.divider()

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div class="study-tip">
        <b>💡 Study Tip</b><br><br>
        Ask specific questions and include the topic,
        chapter, or concept you are currently studying.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# MAIN TABS
# ============================================================

tab1, tab2, tab3 = st.tabs([
    "💬 Study Assistant",
    "📝 Notes Generator",
    "🧠 Quiz Generator"
])

# ============================================================
# COMMON AI FUNCTION
# ============================================================

def generate_response(prompt):

    system_instruction = f"""
You are StudyMate AI, a professional educational study assistant.

Your ONLY purpose is education and academic learning.

Current subject:
{subject}

Student level:
{study_level}

Preferred explanation style:
{response_style}

STRICT RULES:

1. Answer only study, education, academic, learning,
   programming, mathematics, science, technology,
   exam-preparation, or career-learning questions.

2. Do NOT engage in unrelated conversations.

3. If the user asks something unrelated to education,
   politely say:
   "I'm designed specifically for study and academic
   learning. Please ask me a study-related question."

4. Explain concepts accurately and clearly.

5. Use examples whenever useful.

6. For programming questions:
   - Explain the logic.
   - Provide clean code when requested.
   - Explain the important parts of the code.

7. For mathematical questions:
   - Show the steps.
   - Explain formulas.
   - Provide the final answer clearly.

8. For exam preparation:
   - Highlight important points.
   - Mention definitions.
   - Give likely practice questions when appropriate.

9. Never intentionally help a student cheat in a live examination.
   Instead, provide concept explanations and practice guidance.

10. Do not pretend to know information that you are uncertain about.

11. Keep responses structured using headings,
    bullet points, numbered steps, tables,
    and examples where appropriate.

User request:
{prompt}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=system_instruction
    )

    return response.text


# ============================================================
# TAB 1 - CHAT ASSISTANT
# ============================================================

with tab1:

    st.subheader("💬 Ask Your Study Assistant")

    st.caption(
        "Ask questions, clarify concepts, solve academic problems, "
        "or prepare for exams."
    )

    # Display conversation
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input(
        "Ask a study-related question..."
    )

    if user_input:

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):

            with st.spinner("📚 Studying your question..."):

                try:

                    context = ""

                    # Include recent conversation
                    recent_messages = st.session_state.messages[-8:]

                    for msg in recent_messages:
                        context += (
                            f"{msg['role'].upper()}: "
                            f"{msg['content']}\n\n"
                        )

                    prompt = f"""
Continue this educational conversation.

Conversation:
{context}

Answer the latest student question.
"""

                    answer = generate_response(prompt)

                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:

                    st.error(
                        "Unable to generate a response. "
                        "Please check your Gemini API configuration."
                    )

# ============================================================
# TAB 2 - NOTES GENERATOR
# ============================================================

with tab2:

    st.subheader("📝 Smart Notes Generator")

    st.write(
        "Enter a topic and generate structured study notes."
    )

    notes_topic = st.text_input(
        "Topic",
        placeholder="Example: Normalization in DBMS"
    )

    notes_length = st.selectbox(
        "Notes Length",
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

        if not notes_topic.strip():

            st.warning("Please enter a topic.")

        else:

            prompt = f"""
Create professional study notes on:

Topic: {notes_topic}

Notes type: {notes_length}

Structure the notes using:

1. Definition
2. Key concepts
3. Important points
4. Examples
5. Advantages / disadvantages where relevant
6. Important formulas or syntax if applicable
7. Exam-focused points
8. Quick revision summary

The notes must be educational, accurate,
clear, and easy for a student to revise.
"""

            with st.spinner("📝 Creating your notes..."):

                try:

                    result = generate_response(prompt)

                    st.session_state.notes = result

                except Exception:

                    st.error(
                        "Unable to generate notes. "
                        "Please check your API configuration."
                    )

    if st.session_state.notes:

        st.markdown("---")

        st.markdown(st.session_state.notes)

# ============================================================
# TAB 3 - QUIZ GENERATOR
# ============================================================

with tab3:

    st.subheader("🧠 Interactive Quiz Generator")

    quiz_topic = st.text_input(
        "Quiz Topic",
        placeholder="Example: C++ Control Statements"
    )

    col1, col2 = st.columns(2)

    with col1:

        number_questions = st.slider(
            "Number of Questions",
            min_value=3,
            max_value=15,
            value=5
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

            st.warning("Please enter a quiz topic.")

        else:

            prompt = f"""
Create a study quiz.

Topic:
{quiz_topic}

Number of questions:
{number_questions}

Difficulty:
{difficulty}

Create multiple-choice questions.

For every question provide:

Question
A. Option
B. Option
C. Option
D. Option

Do NOT immediately reveal the answers.

After all questions, provide:

ANSWER KEY

with the correct option for each question.

Then provide a short explanation
for each correct answer.

This is strictly for academic practice.
"""

            with st.spinner("🧠 Preparing your quiz..."):

                try:

                    result = generate_response(prompt)

                    st.session_state.quiz = result

                except Exception:

                    st.error(
                        "Unable to generate quiz. "
                        "Please check your API configuration."
                    )

    if st.session_state.quiz:

        st.markdown("---")

        st.markdown(st.session_state.quiz)

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "📚 StudyMate AI • Powered by Gemini • "
    "Designed for educational and academic purposes"
)
