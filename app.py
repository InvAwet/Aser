import streamlit as st
import pandas as pd
from datetime import datetime
import os, traceback, base64
from io import BytesIO

from utils.pdf_parser import PDFParser
from utils.gemini_processor import GeminiProcessor
from utils.enhanced_pdf_generator import EnhancedPDFGenerator
from utils.data_models import DailyDiaryData, SiteReportData


def initialize_session_state():
    """Initialize all required session state variables"""
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = None
    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.getenv("GOOGLE_API_KEY", "")


def upload_and_process_page():
    """Page for uploading and processing PDF reports"""
    st.header("Upload & Process")
    
    # API key input
    st.session_state.api_key = st.text_input(
        "Google Gemini API Key",
        value=st.session_state.api_key,
        type="password"
    )
    
    uploaded_file = st.file_uploader("Upload site report PDF", type="pdf")

    if uploaded_file:
        parser = PDFParser()
        try:
            with st.spinner("📄 Extracting text from PDF..."):
                raw_data = parser.extract_text_from_pdf(uploaded_file)
            
            st.text_area("📄 Extracted Text (Raw)", raw_data, height=300)

            processor = GeminiProcessor(api_key=st.session_state.api_key)
            
            with st.spinner("🤖 Processing with Gemini AI..."):
                try:
                    processed = processor.extract_site_report_data(raw_data)
                except Exception as gemini_error:
                    st.error(f"❌ Gemini Error: {str(gemini_error)}")
                    st.text(traceback.format_exc())
                    return

            if hasattr(processor, "last_response_text"):
                st.text_area("🧠 Gemini Raw Response", processor.last_response_text, height=300)

            if processed:
                st.session_state.extracted_data = processed
                st.success("✅ Structured data extracted successfully!")
                
                # Show extraction summary
                with st.expander("Extracted Data Preview"):
                    st.json(processed.to_dict())
            else:
                st.error("❌ Failed to extract structured data")

        except Exception as e:
            st.error(f"❌ Processing Error: {str(e)}")
            st.text(traceback.format_exc())


def review_and_edit_page():
    """Page for reviewing and editing extracted data"""
    st.header("Review & Edit")
    data = st.session_state.extracted_data
    
    if not data:
        st.info("⚠️ Please upload and process a report first.")
        return

    with st.form("diary_form"):
        # Project Information
        st.subheader("Project Information")
        col1, col2 = st.columns(2)
        data.project = col1.text_input("Project Name", data.project)
        data.location = col2.text_input("Location", data.location)
        
        col3, col4 = st.columns(2)
        data.employer = col3.text_input("Employer", data.employer)
        data.contractor = col4.text_input("Contractor", data.contractor)
        
        # Date and Time
        st.subheader("Date & Time")
        date_col, weather_col = st.columns(2)
        data.date = date_col.text_input("Date (DD-MM-YYYY)", data.date)
        data.weather = weather_col.selectbox(
            "Weather Condition",
            ["Sunny/Dry", "Cloudy", "Rainy", "Stormy"],
            index=["Sunny/Dry", "Cloudy", "Rainy", "Stormy"].index(data.weather) if data.weather in ["Sunny/Dry", "Cloudy", "Rainy", "Stormy"] else 0
        )
        
        time_col1, time_col2 = st.columns(2)
        data.time_morning = time_col1.checkbox("Morning Shift", value=data.time_morning)
        data.time_afternoon = time_col2.checkbox("Afternoon Shift", value=data.time_afternoon)
        
        # Activities Editor
        st.subheader("Activities")
        activities_df = pd.DataFrame([a.__dict__ for a in data.activities])
        edited_activities = st.data_editor(
            activities_df,
            num_rows="dynamic",
            column_config={
                "sn": st.column_config.NumberColumn("No.", disabled=True),
                "description": "Activity Description",
                "location": "Location",
                "quantity": "Quantity",
                "unit": "Unit"
            }
        )
        data.activities = [ActivityData(**row) for _, row in edited_activities.iterrows()]
        
        # Equipment Editor
        st.subheader("Equipment")
        equipment_df = pd.DataFrame([e.__dict__ for e in data.equipment])
        edited_equipment = st.data_editor(
            equipment_df,
            num_rows="dynamic",
            column_config={
                "sn": st.column_config.NumberColumn("No.", disabled=True),
                "equipment": "Equipment Type",
                "no": "ID/Number",
                "operating_hours": "Hours Operated",
                "status": "Status"
            }
        )
        data.equipment = [EquipmentData(**row) for _, row in edited_equipment.iterrows()]
        
        # Safety Information
        st.subheader("Safety Observations")
        data.near_miss = st.text_area("Near Miss/Accidents", data.near_miss)
        data.unsafe_acts = st.text_area("Unsafe Acts/Conditions", "\n".join([ua.description for ua in data.unsafe_acts]))
        
        # Form Submission
        if st.form_submit_button("💾 Save All Changes"):
            if errors := data.validate():
                for error in errors:
                    st.error(error)
            else:
                st.session_state.extracted_data = data
                st.success("✅ All changes saved successfully!")


def generate_pdf_page():
    """Page for generating the final PDF"""
    st.header("Generate PDF")
    data = st.session_state.extracted_data

    if not data:
        st.info("⚠️ Please upload and process a report first.")
        return

    # Validation summary
    if errors := data.validate():
        st.warning("⚠️ Data validation issues found:")
        for error in errors:
            st.error(error)
    else:
        st.success("✅ Data validation passed")

    if st.button("🖨️ Generate PDF"):
        try:
            with st.spinner("Generating PDF..."):
                gen = EnhancedPDFGenerator()
                pdf_bytes = gen.generate(data)
            
            # Create download link
            st.success("✅ PDF generated successfully!")
            st.balloons()
            
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="daily_diary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf">📥 Download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
            
            # Show preview (first page only)
            with st.expander("PDF Preview"):
                try:
                    from pdf2image import convert_from_bytes
                    images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)
                    st.image(images[0], use_column_width=True)
                except Exception as e:
                    st.warning(f"Could not generate preview: {str(e)}")
            
        except Exception as e:
            st.error(f"❌ PDF generation failed: {str(e)}")
            st.text(traceback.format_exc())


def history_page():
    """Placeholder for history functionality"""
    st.header("History")
    st.info("🕓 History feature coming soon!")
    if st.session_state.get('extracted_data'):
        st.json(st.session_state.extracted_data.to_dict())


def main():
    """Main application entry point"""
    initialize_session_state()
    st.set_page_config(
        page_title="Aser Diary Converter",
        page_icon="📋",
        layout="centered"
    )
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Upload & Process", "Review & Edit", "Generate PDF", "History"],
        index=0
    )
    
    # Display selected page
    if page == "Upload & Process":
        upload_and_process_page()
    elif page == "Review & Edit":
        review_and_edit_page()
    elif page == "Generate PDF":
        generate_pdf_page()
    elif page == "History":
        history_page()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<div style='text-align: center'>v1.0.0<br>Last Updated: {datetime.now().strftime('%Y-%m-%d')}</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
