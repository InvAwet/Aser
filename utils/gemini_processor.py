import google.generativeai as genai
import json
import re
from typing import Optional, Dict, List
from utils.data_models import DailyDiaryData
import streamlit as st

class GeminiProcessor:
    """Class for processing site reports using Gemini AI"""
    
    def __init__(self, api_key: str):
        """
        Initialize Gemini processor
        
        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key
        self.model = None
        self.setup_gemini()
    
    def setup_gemini(self):
        """Configure Gemini AI"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            st.error(f"Failed to initialize Gemini AI: {str(e)}")
            raise e
    
    def extract_site_report_data(self, raw_text: str) -> Optional[DailyDiaryData]:
        """
        Extract structured data from site report text using Gemini AI
        
        Args:
            raw_text: Raw text extracted from site report
            
        Returns:
            DailyDiaryData: Structured data object
        """
        try:
            # Create extraction prompt
            prompt = self.create_extraction_prompt(raw_text)
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            self.last_response_text = response.text if response and response.text else "❌ No text in Gemini response"
            
            if response and response.text:
                # Parse the response
                structured_data = self.parse_gemini_response(response.text)
                
                if structured_data:
                    # Convert to DailyDiaryData object
                    return self.convert_to_daily_diary_data(structured_data)
            
            return None
            
        except Exception as e:
            st.error(f"Error processing with Gemini AI: {str(e)}")
            return None
    
    def create_extraction_prompt(self, raw_text: str) -> str:
        """
        Create a detailed prompt for Gemini AI to extract site report data
        
        Args:
            raw_text: Raw text from site report
            
        Returns:
            str: Formatted prompt
        """
        
        prompt = f"""
You are an expert data extraction specialist for construction site reports. Extract structured information from the following site report text and return it as a JSON object.

SITE REPORT TEXT:
{raw_text}

Extract the following information and return it as a valid JSON object with these exact keys:

{{
    "project": "project name or description",
    "employer": "employer/client name",
    "consultant": "consultant company name", 
    "contractor": "contractor company name",
    "date": "date in DD-MM-YYYY format",
    "time_morning": true/false,
    "time_afternoon": true/false,
    "location": "work location or site location",
    "weather": "weather condition (e.g., Sunny/Dry, Rainy, Cloudy)",
    "activities": [
        {{
            "sn": 1,
            "description": "activity description",
            "location": "specific location if mentioned",
            "quantity": "quantity if mentioned",
            "unit": "unit if mentioned"
        }}
    ],
    "equipment": [
        {{
            "sn": 1,
            "equipment": "equipment name/type",
            "no": "equipment number/ID",
            "operating_hours": "hours if mentioned",
            "idle_hours": "idle hours if mentioned",
            "status": "working status",
            "remarks": "any remarks"
        }}
    ],
    "personnel": [
        {{
            "sn": 1,
            "personnel": "personnel type/role",
            "no": "number of personnel",
            "hours": "working hours if mentioned",
            "role": "specific role description"
        }}
    ],
    "materials": [
        {{
            "type": "material type",
            "unit": "unit of measurement",
            "quantity": "quantity used",
            "location": "where used"
        }}
    ],
    "unsafe_acts": [
        {{
            "sn": 1,
            "description": "description of unsafe act or condition",
            "severity": "severity level if mentioned",
            "action_taken": "corrective action if mentioned"
        }}
    ],
    "near_miss": "near miss incidents description",
    "obstruction": "any obstructions or delays",
    "engineers_note": "engineer's notes or remarks",
    "prepared_by": "person who prepared the report",
    "checked_by": "person who checked the report",
    "approved_by": "person who approved the report",
    "document_number": "document number if available",
    "page_number": "page number if available",
    "revision": "revision number if available"
}}

EXTRACTION RULES:
1. Extract information accurately from the provided text
2. If information is not available, use empty string "" for text fields, empty array [] for lists, and false for boolean fields
3. For dates, convert to DD-MM-YYYY format
4. For activities, equipment, personnel - extract as many items as mentioned in the text
5. Assign sequential serial numbers (sn) starting from 1
6. For time_morning/time_afternoon, determine from context (morning/afternoon shifts, AM/PM times)
7. Preserve original language and terminology from the source text
8. IMPORTANT: Ensure proper word spacing in descriptions (e.g., "loading material" not "loadingmaterial", "concrete work" not "concretework")
9. When extracting activities and descriptions, maintain natural word boundaries and spacing
10. Return only valid JSON without any additional text or explanation

RESPOND WITH JSON ONLY:
"""
        
        return prompt
    
    def parse_gemini_response(self, response_text: str) -> Optional[Dict]:
        """
        Parse Gemini AI response and extract structured data
        
        Args:
            response_text: Raw response from Gemini AI
            
        Returns:
            Dict: Parsed structured data or None if parsing failed
        """
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                
                # Parse JSON
                structured_data = json.loads(json_text)
                return structured_data
            
            # If no JSON found, try to parse the entire response
            try:
                structured_data = json.loads(cleaned_text)
                return structured_data
            except json.JSONDecodeError:
                # Last resort: extract key-value pairs manually
                return self.extract_key_value_from_text(cleaned_text)
                
        except Exception as e:
            st.warning(f"Failed to parse Gemini response: {str(e)}")
            return None
    
    def extract_key_value_from_text(self, text: str) -> Dict:
        """
        Extract key-value pairs from text when JSON parsing fails
        
        Args:
            text: Text to parse
            
        Returns:
            Dict: Extracted key-value pairs
        """
        extracted_data = {
            "project": "",
            "employer": "",
            "consultant": "",
            "contractor": "",
            "date": "",
            "time_morning": False,
            "time_afternoon": False,
            "location": "",
            "weather": "Sunny/Dry",
            "activities": [],
            "equipment": [],
            "personnel": [],
            "materials": [],
            "unsafe_acts": [],
            "near_miss": "",
            "obstruction": "",
            "engineers_note": "",
            "prepared_by": "",
            "checked_by": "",
            "approved_by": "",
            "document_number": "",
            "page_number": "",
            "revision": ""
        }
        
        # Extract basic information using regex patterns
        patterns = {
            'project': r'project[:\s]*([^\n]+)',
            'employer': r'employer[:\s]*([^\n]+)',
            'consultant': r'consultant[:\s]*([^\n]+)',
            'contractor': r'contractor[:\s]*([^\n]+)',
            'date': r'date[:\s]*([^\n]+)',
            'location': r'location[:\s]*([^\n]+)',
            'weather': r'weather[:\s]*([^\n]+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_data[key] = match.group(1).strip()
        
        return extracted_data
    
    def convert_to_daily_diary_data(self, structured_data: Dict) -> DailyDiaryData:
        """
        Convert structured data dictionary to DailyDiaryData object with enhanced validation
        
        Args:
            structured_data: Dictionary with extracted data
            
        Returns:
            DailyDiaryData: Structured data object
        """
        try:
            # Clean and validate the data
            cleaned_data = {}
            
            # Basic text fields
            text_fields = ['project', 'employer', 'consultant', 'contractor', 'location', 
                          'weather', 'near_miss', 'obstruction', 'engineers_note', 
                          'prepared_by', 'checked_by', 'approved_by', 'document_number', 
                          'page_number', 'revision']
            
            for field in text_fields:
                value = structured_data.get(field, '')
                cleaned_data[field] = self._clean_text(str(value)) if value else ''
            
            # Date validation and formatting
            date_str = structured_data.get('date', '')
            cleaned_data['date'] = self._validate_date(date_str)
            
            # Boolean fields
            cleaned_data['time_morning'] = bool(structured_data.get('time_morning', False))
            cleaned_data['time_afternoon'] = bool(structured_data.get('time_afternoon', False))
            
            # List fields with validation
            list_fields = {
                'activities': ['sn', 'description', 'location', 'quantity', 'unit'],
                'equipment': ['sn', 'equipment', 'no', 'operating_hours', 'idle_hours', 'status', 'remarks'],
                'personnel': ['sn', 'personnel', 'no', 'hours', 'role'],
                'materials': ['type', 'unit', 'quantity', 'location'],
                'unsafe_acts': ['sn', 'description', 'severity', 'action_taken']
            }
            
            for list_field, required_fields in list_fields.items():
                raw_list = structured_data.get(list_field, [])
                if isinstance(raw_list, list):
                    cleaned_data[list_field] = self._validate_and_clean_list(raw_list, required_fields)
                else:
                    cleaned_data[list_field] = []
            
            # Create DailyDiaryData object
            return DailyDiaryData.from_dict(cleaned_data)
            
        except Exception as e:
            st.warning(f"Error converting data: {str(e)}")
            # Return minimal valid object
            return DailyDiaryData()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text data while preserving proper word spacing"""
        if not text or text == 'null':
            return ''
        
        # Convert to string and normalize whitespace
        cleaned = ' '.join(str(text).split())
        
        # Remove common artifacts
        cleaned = re.sub(r'^["\'\s]+|["\'\s]+$', '', cleaned)
        
        # Fix common word spacing issues that may come from OCR or AI extraction
        # Add spaces between lowercase and uppercase letters (merged words)
        cleaned = re.sub(r'([a-z])([A-Z])', r'\1 \2', cleaned)
        
        # Fix common construction-related merged words
        word_patterns = [
            (r'loading([a-z])', r'loading \1'),
            (r'material([a-z])', r'material \1'),
            (r'concrete([a-z])', r'concrete \1'),
            (r'steel([a-z])', r'steel \1'),
            (r'excavation([a-z])', r'excavation \1'),
            (r'construction([a-z])', r'construction \1'),
            (r'equipment([a-z])', r'equipment \1'),
            (r'([a-z])work\b', r'\1 work'),
            (r'([a-z])site\b', r'\1 site'),
            (r'([a-z])area\b', r'\1 area'),
            (r'([a-z])pipe\b', r'\1 pipe'),
            (r'([a-z])road\b', r'\1 road'),
            (r'([a-z])bridge\b', r'\1 bridge'),
        ]
        
        for pattern, replacement in word_patterns:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        # Clean up any double spaces created
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _validate_date(self, date_str: str) -> str:
        """Validate and format date string"""
        if not date_str or date_str == 'null':
            return ''
        
        # Try to extract date from various formats
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
            r'(\d{1,2})\s+(\w+)\s+(\d{4})',        # DD Month YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, str(date_str))
            if match:
                try:
                    if len(match.groups()) == 3:
                        # Assume first pattern found is DD-MM-YYYY
                        day, month, year = match.groups()
                        return f"{day.zfill(2)}-{month.zfill(2)}-{year}"
                except:
                    continue
        
        return str(date_str).strip()
    
    def _validate_and_clean_list(self, data_list: List[Dict], required_fields: List[str]) -> List[Dict]:
        """Validate and clean list data with duplicate detection for equipment"""
        cleaned_list = []
        seen_equipment = set()  # Track equipment plate numbers
        
        for i, item in enumerate(data_list):
            if not isinstance(item, dict):
                continue
            
            cleaned_item = {}
            
            # Ensure serial number
            cleaned_item['sn'] = item.get('sn', i + 1)
            
            # Clean other fields
            for field in required_fields:
                if field != 'sn':
                    value = item.get(field, '')
                    cleaned_item[field] = self._clean_text(str(value)) if value else ''
            
            # Special handling for equipment to prevent duplicates
            if 'equipment' in required_fields and 'no' in required_fields:
                equipment_no = cleaned_item.get('no', '').strip()
                if equipment_no:
                    # Normalize equipment number (remove spaces, convert to uppercase)
                    normalized_no = re.sub(r'\s+', '', equipment_no.upper())
                    if normalized_no in seen_equipment:
                        # Skip this duplicate equipment
                        continue
                    seen_equipment.add(normalized_no)
            
            # Only add if has meaningful content
            has_content = any(cleaned_item.get(field, '') for field in required_fields if field != 'sn')
            if has_content:
                cleaned_list.append(cleaned_item)
        
        # Renumber serial numbers after removing duplicates
        for i, item in enumerate(cleaned_list):
            item['sn'] = i + 1
        
        return cleaned_list
