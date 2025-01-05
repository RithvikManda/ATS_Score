import os
import json
import streamlit as st
from groq import Groq
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import re
client = Groq()

working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))

GROQ_API_KEY = config_data["GROQ_API_KEY"]
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

def interview_page():
    st.title("Interview")

def resume_screening():

    def input_pdf_text(uploaded_file):
        """Extract text from uploaded PDF."""
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in range(len(reader.pages)):
            page = reader.pages[page]
            text += str(page.extract_text())
        return text

    def clean_json_response(response):
        """Extract and clean the JSON portion of the LLM's response."""
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        else:
            return None
    
    def clean_json_response(response):
        """Extract and clean the JSON portion of the LLM's response."""
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        else:
            return None

        
    def get_llm_response(prompt):
        chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": "Using the prompt provide me the ATS score for the uploaded resume",
            }
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        )
        return chat_completion.choices[0].message.content



    st.title("Smart ATS")
    st.text("Improve Your Resume ATS")

    jd = st.text_area("Paste the Job Description")
    uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF")

    submit = st.button("Submit")
    if submit:
        if uploaded_file is not None and jd.strip():
            # Extract resume text from uploaded PDF
            resume_text = input_pdf_text(uploaded_file)


            input_prompt = f"""
                Act as a skilled ATS with expertise in technology, software engineering, and data analysis.
                Evaluate the resume against the provided job description (JD).
                Provide:
                1. A percentage match for how well the resume fits the JD.
                2. A list of missing keywords.
            
                Your response should be in this strict json format:
                {{
                    "JD Match": "85%",
                    "MissingKeywords": ["keyword1", "keyword2"],
                    "Profile Summary": "Brief summary of the evaluation"
                }}
            
                Resume: {resume_text}
                JD: {jd}
                """

            response = get_llm_response(input_prompt)
            cleaned_response = clean_json_response(response)
            if cleaned_response:
                try:
                    parsed_response = json.loads(cleaned_response)
                    jd_match = float(parsed_response.get("JD Match", "0").replace("%", "").strip())
                except json.JSONDecodeError:
                    st.error("The cleaned response is not valid JSON.")
            st.write(jd_match)
            if jd_match>70:
                # url = "https://www.youtube.com/watch?v=jR1ZQQ5W07M&t=18s"
                # st.write("check out this [link](%s)" % url)
                # st.markdown("check out this [link](%s)" % url)
                st.write("Get ready for the interview --> [link](https://share.streamlit.io/mesmith027/streamlit_webapps/main/MC_pi/streamlit_app.py)")


resume_screening()


