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
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = None
    if 'ready_for_pdf' not in st.session_state:
        st.session_state.ready_for_pdf = False


def upload_and_process_page():
    st.header("Upload & Process")
    
    # Initialize session state variables
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'upload_success' not in st.session_state:
        st.session_state.upload_success = False

    # File uploader widget
    uploaded_file = st.file_uploader("Upload site report PDF", type="pdf")
    
    # Handle file selection and persistence
    if uploaded_file and (uploaded_file != st.session_state.uploaded_file):
        st.session_state.upload_success = False
        st.session_state.uploaded_file = uploaded_file
        st.session_state.extracted_data = None
        st.session_state.ready_for_pdf = False
    
    # Process only when requested
    if st.session_state.uploaded_file:
        file_details = {
            "File name": st.session_state.uploaded_file.name,
            "File size": f"{len(st.session_state.uploaded_file.getvalue()) / 1024:.2f} KB"
        }
        st.json(file_details)
        
        if st.button("Process PDF", key="process_btn") and not st.session_state.upload_success:
            parser = PDFParser()
            try:
                st.info("📄 Extracting text from PDF...")
                
                raw_data = parser.extract_text_from_pdf(st.session_state.uploaded_file)
                st.text_area("📄 Extracted Text (Raw)", raw_data, height=300)

                processor = GeminiProcessor(api_key=os.getenv("GOOGLE_API_KEY", ""))
                st.info("🤖 Sending to Gemini for data extraction...")

                try:
                    processed = processor.extract_site_report_data(raw_data)
                except Exception as gemini_error:
                    st.error(f"❌ Gemini Error: {gemini_error}")
                    return

                if hasattr(processor, "last_response_text"):
                    st.text_area("🧠 Gemini Raw Response", processor.last_response_text, height=300)

                if processed:
                    st.session_state.extracted_data = processed
                    st.session_state.upload_success = True
                    st.session_state.ready_for_pdf = False
                    st.success("✅ Structured data extracted from Gemini.")
                else:
                    st.error("❌ Gemini did not return structured data. Check API key, model output, or prompt quality.")

            except Exception as e:
                st.error(f"❌ General Error: {e}")
                st.text(traceback.format_exc())
    else:
        st.info("⚠️ Please upload and process a report first.")         


def review_and_edit_page():
    st.header("Review & Edit")
    data = st.session_state.extracted_data
    
    if not data:
        st.info("⚠️ Please upload and process a report first.")
        return

    # Set default metadata if empty
    if not data.project:
        data.project = "Construction of Trunk Lines for Kotebe and Kitime Sub-Catchment of Eastern Sewer Line Project"
    if not data.employer:
        data.employer = "AAWSA-WISIDD, THE WORLD BANK"
    if not data.consultant:
        data.consultant = "NICHOLAS O'DWYER LTD. In Jv. with MS CONSULTANCY"
    if not data.contractor:
        data.contractor = "ASER CONSTRUCTION PLC"

    with st.form("diary_form"):
        st.subheader("Project Information")
        col1, col2 = st.columns(2)
        data.project = col1.text_input("Project Name", value=data.project)
        data.contractor = col2.text_input("Contractor", value=data.contractor)
        data.employer = col1.text_input("Employer", value=data.employer)
        data.consultant = col2.text_input("Consultant", value=data.consultant)
        
        st.divider()
        st.subheader("Date & Time")
        date_col, weather_col, time_col = st.columns([2, 2, 1])
        data.date = date_col.text_input("Date (DD-MM-YYYY)", value=data.date)
        data.weather = weather_col.selectbox("Weather", 
                                           ["Sunny/Dry", "Cloudy", "Rainy", "Stormy"],
                                           index=0 if not data.weather else 
                                           ["Sunny/Dry", "Cloudy", "Rainy", "Stormy"].index(data.weather))
        st.write("Work Period:")
        time_col1, time_col2 = st.columns(2)
        data.time_morning = time_col1.checkbox("Morning", value=data.time_morning)
        data.time_afternoon = time_col2.checkbox("Afternoon", value=data.time_afternoon)
        data.location = st.text_input("Location", value=data.location)
        
        st.divider()
        st.subheader("Activities")
        st.info("Add, edit, or remove activities below")
        activities = pd.DataFrame(data.activities if data.activities else [])
        if not activities.empty:
            activities_edited = st.data_editor(
                activities,
                num_rows="dynamic",
                column_config={
                    "sn": st.column_config.NumberColumn("No.", width="small"),
                    "description": "Description",
                    "location": "Location",
                    "quantity": "Quantity",
                    "unit": "Unit"
                },
                use_container_width=True
            )
            data.activities = activities_edited.to_dict(orient='records')
        else:
            st.warning("No activities extracted. Add new ones below:")
            if st.button("Add Activity"):
                data.activities = [{"sn": 1, "description": "", "location": "", "quantity": "", "unit": ""}]
        
        st.divider()
        st.subheader("Equipment")
        st.info("Review equipment used on site")
        equipment = pd.DataFrame(data.equipment if data.equipment else [])
        if not equipment.empty:
            equipment_edited = st.data_editor(
                equipment,
                num_rows="dynamic",
                column_config={
                    "sn": st.column_config.NumberColumn("No.", width="small"),
                    "equipment": "Equipment Type",
                    "no": "ID/Number",
                    "operating_hours": "Op. Hours",
                    "idle_hours": "Idle Hours",
                    "status": "Status",
                    "remarks": "Remarks"
                },
                use_container_width=True
            )
            data.equipment = equipment_edited.to_dict(orient='records')
        else:
            st.warning("No equipment information extracted")
        
        st.divider()
        st.subheader("Personnel")
        st.info("Edit personnel information")
        personnel = pd.DataFrame(data.personnel if data.personnel else [])
        if not personnel.empty:
            personnel_edited = st.data_editor(
                personnel,
                num_rows="dynamic",
                column_config={
                    "sn": st.column_config.NumberColumn("No.", width="small"),
                    "personnel": "Role/Type",
                    "no": "Count",
                    "hours": "Hours",
                    "role": "Specific Role"
                },
                use_container_width=True
            )
            data.personnel = personnel_edited.to_dict(orient='records')
        else:
            st.warning("No personnel information extracted")
        
        st.divider()
        st.subheader("Safety Information")
        unsafe_acts = pd.DataFrame(data.unsafe_acts if data.unsafe_acts else [])
        if not unsafe_acts.empty:
            st.write("Unsafe Acts/Conditions:")
            unsafe_edited = st.data_editor(
                unsafe_acts,
                num_rows="dynamic",
                column_config={
                    "sn": st.column_config.NumberColumn("No.", width="small"),
                    "description": "Description",
                    "severity": "Severity",
                    "action_taken": "Action Taken"
                }
            )
            data.unsafe_acts = unsafe_edited.to_dict(orient='records')
        else:
            st.info("No unsafe acts reported")
        
        data.near_miss = st.text_area("Near Miss/Accidents/Incidents", value=data.near_miss or "", height=100)
        data.obstruction = st.text_area("Obstructions/Action Plans", value=data.obstruction or "", height=100)
        data.engineers_note = st.text_area("Engineer's Notes", value=data.engineers_note or "", height=150)
        
        st.divider()
        st.subheader("Signatures")
        sig_col1, sig_col2, sig_col3 = st.columns(3)
        data.prepared_by = sig_col1.text_input("Prepared By", value=data.prepared_by or "")
        data.checked_by = sig_col2.text_input("Checked By", value=data.checked_by or "")
        data.approved_by = sig_col3.text_input("Approved By", value=data.approved_by or "")
        
        st.divider()
        st.subheader("Document Details")
        doc_col1, doc_col2, doc_col3 = st.columns(3)
        data.document_number = doc_col1.text_input("Document Number", value=data.document_number or "")
        data.page_number = doc_col2.text_input("Page Number", value=data.page_number or "")
        data.revision = doc_col3.text_input("Revision", value=data.revision or "")
        
        submitted = st.form_submit_button("Save All Changes")
        if submitted:
            validation_errors = data.validate()
            if validation_errors:
                st.error("Validation errors found:")
                for error in validation_errors:
                    st.error(f"- {error}")
            else:
                st.session_state.extracted_data = data
                st.session_state.ready_for_pdf = True
                st.success("✅ All changes saved successfully!")
                st.rerun()


def generate_pdf_page():
    st.header("Generate PDF")
    
    if not st.session_state.get('ready_for_pdf', False):
        st.warning("⚠️ Please complete and save the review/edit section first")
        return
    
    data = st.session_state.extracted_data

    if st.button("Generate PDF"):
        try:
            gen = EnhancedPDFGenerator()
            output = gen.generate(data)
            
            st.session_state.generated_pdf = output
            st.success("✅ PDF generated successfully!")
            
            b64 = base64.b64encode(output).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="diary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf">📥 Download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

        except Exception as e:
            st.error("❌ PDF generation failed:")
            st.text(traceback.format_exc())


def history_page():
    st.header("History")
    st.info("🕓 History feature not implemented yet.")


def main():
    initialize_session_state()
    st.set_page_config(page_title="Aser Diary Converter", layout="centered")
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
