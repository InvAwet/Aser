import streamlit as st
import pandas as pd
from datetime import datetime
import os, traceback, io, base64

from utils.pdf_parser import PDFParser
from utils.gemini_processor import GeminiProcessor
from utils.enhanced_pdf_generator import EnhancedPDFGenerator
from utils.data_models import DailyDiaryData, SiteReportData
from io import BytesIO

def initialize_session_state():
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = None

def upload_and_process_page():
    st.header("Upload & Process")
    uploaded_file = st.file_uploader("Upload site report PDF", type="pdf")

    if uploaded_file:
        parser = PDFParser()
        try:
            st.info("📄 Extracting text from PDF...")
            raw_data = parser.extract_text_from_pdf(uploaded_file)
            st.text_area("📄 Extracted Text (Raw)", raw_data, height=300)

            processor = GeminiProcessor(api_key=os.getenv("GOOGLE_API_KEY", ""))
            st.info("🤖 Sending to Gemini for data extraction...")

            try:
                processed = processor.extract_site_report_data(raw_data)
            except Exception as gemini_error:
                st.error(f"❌ Gemini Error: {gemini_error}")
                return

            # ✅ Show Gemini raw response
            if hasattr(processor, "last_response_text"):
                st.text_area("🧠 Gemini Raw Response", processor.last_response_text, height=300)

            if processed:
                st.session_state.extracted_data = processed
                st.success("✅ Structured data extracted from Gemini.")
            else:
                st.error("❌ Gemini did not return structured data. Check API key, model output, or prompt quality.")

        except Exception as e:
            st.error(f"❌ General Error: {e}")
            st.text(traceback.format_exc())

def review_and_edit_page():
    st.header("Review & Edit")
    data = st.session_state.extracted_data
    if data:
        df = pd.DataFrame([data.__dict__])
        edited = st.data_editor(df)
        if st.button("Save Changes"):
            st.session_state.extracted_data = DailyDiaryData(**edited.to_dict(orient="records")[0])
            st.success("Changes saved.")
    else:
        st.info("Upload and process a report first.")

def generate_pdf_page():
    st.header("Generate PDF")
    data = st.session_state.extracted_data
    if data:
        logo1 = st.file_uploader("Upload Nicholas O'Dwyer logo", type=["png", "jpg", "jpeg"], key="logo1")
        logo2 = st.file_uploader("Upload MS Consultancy logo", type=["png", "jpg", "jpeg"], key="logo2")

        if st.button("Generate PDF"):
            if not logo1 or not logo2:
                st.error("⚠️ Please upload both logos before generating the PDF.")
                return

            try:
                gen = EnhancedPDFGenerator()
                logo1_bytes = BytesIO(logo1.read())
                logo2_bytes = BytesIO(logo2.read())

                output = gen.generate(data, logo1_bytes, logo2_bytes)
                b64 = base64.b64encode(output).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="diary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf">📥 Download PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("✅ PDF generated successfully.")
            except Exception as e:
                st.error(f"❌ PDF generation failed: {e}")
                st.text(traceback.format_exc())
    else:
        st.info("Upload and process a report first.")

def history_page():
    st.header("History")
    st.info("History feature not implemented yet.")

def main():
    initialize_session_state()
    st.set_page_config(page_title="Aser Diary Converter")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Upload & Process", "Review & Edit", "Generate PDF", "History"])
    if page == "Upload & Process":
        upload_and_process_page()
    elif page == "Review & Edit":
        review_and_edit_page()
    elif page == "Generate PDF":
        generate_pdf_page()
    elif page == "History":
        history_page()

if __name__ == "__main__":
    main()
