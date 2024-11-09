import streamlit as st
import os
from langchain_community.llms import Ollama
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import re

llm = Ollama(model="llama3")

load_dotenv()  # Load all environment variables

def input_pdf_text(uploaded_file):
    """Extract text from uploaded PDF."""
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

def get_llm_response(prompt):
    """Send a prompt to the LLM and return the raw response."""
    response = llm(prompt)
    return response

def clean_json_response(response):
    """Extract and clean the JSON portion of the LLM's response."""
    json_match = re.search(r"\{.*\}", response, re.DOTALL)
    if json_match:
        return json_match.group(0)
    else:
        return None

# Streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS")

jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None and jd.strip():
        # Extract resume text from uploaded PDF
        resume_text = input_pdf_text(uploaded_file)

        # Define the prompt for the LLM
        input_prompt = f"""
        Act as a skilled ATS with expertise in technology, software engineering, and data analysis.
        Evaluate the resume against the provided job description (JD).
        Provide:
        1. A percentage match for how well the resume fits the JD.
        2. A list of missing keywords.
        
        Your response should be in this strict JSON format:
        {{
            "JD Match": "85%",
            "MissingKeywords": ["keyword1", "keyword2"],
            "Profile Summary": "Brief summary of the evaluation"
        }}
        
        Resume: {resume_text}
        JD: {jd}
        """

        # Get LLM response
        response = get_llm_response(input_prompt)
        cleaned_response = clean_json_response(response)

        if cleaned_response:
            try:
                parsed_response = json.loads(cleaned_response)
                jd_match = float(parsed_response.get("JD Match", "0").replace("%", "").strip())

                # Check if the match is above 70%
                if jd_match > 70:
                    st.subheader("Selected")
                else:
                    st.subheader("Not Selected")

                # Display detailed feedback
                st.write(parsed_response)

            except json.JSONDecodeError:
                st.error("The cleaned response is not valid JSON.")
        else:
            st.error("Unable to parse the LLM's response. Please try again.")
    else:
        st.warning("Please provide both a job description and a resume.")
