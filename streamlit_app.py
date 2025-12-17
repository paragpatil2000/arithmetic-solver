import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/solve"   # FastAPI URL

st.set_page_config(page_title="AI Arithmetic Solver")

st.title("🧠 AI Arithmetic Solver (Groq + Streamlit)")

st.write("Enter any arithmetic problem in normal language, and the AI will solve it.")

# User input
question = st.text_input("Enter your question:")

# When user clicks button
if st.button("Solve"):
    if question.strip() == "":
        st.warning("Please enter a question.")
    else:
        try:
            # Call FastAPI backend
            response = requests.post(API_URL, json={"text": question})
            result = response.json()

            st.subheader("Result")

            # FIXED: safe checking
            if result.get("answer") is not None:
                st.success(f"**Answer:** {result['answer']}")
            else:
                st.error("AI could not find a final numeric answer. Please check the full AI output below.")

            st.markdown("### Full AI Output")
            st.info(result.get("raw", "No raw content received."))

            st.markdown(f"**Solved By:** `{result.get('method', 'Unknown')}` engine")

        except Exception as e:
            st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption("Built using Streamlit + FastAPI + Groq LLaMA-3")
