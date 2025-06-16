import pdfplumber
import io
import pytesseract
import cv2
import numpy as np
from PIL import Image
from typing import Optional, Dict, List
import streamlit as st
import fitz  # PyMuPDF
import re

class PDFParser:
    """Enhanced PDF Parser with high-accuracy OCR and multilingual support"""
    
    def __init__(self):
        """Initialize PDF parser with OCR configuration"""
        self.setup_ocr()
    
    def setup_ocr(self):
        """Setup OCR with enhanced configuration for maximum accuracy"""
        # Configure Tesseract for high accuracy
        self.ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?@#$%^&*()_+-=[]{}|;:\'\"<>/?`~àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮįİıĲĳĴĵĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŒœŔŕŖŗŘřŚśŜŝŞşŠšŢţŤťŦŧŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽž'
        
        # Language configuration for multilingual support
        self.languages = 'eng+fra+deu+spa+ita+por+ara+chi_sim+chi_tra+jpn+kor'
    
    def extract_text_from_pdf(self, uploaded_file) -> str:
        """
        Extract text from PDF using multiple methods for maximum accuracy
        
        Args:
            uploaded_file: Uploaded PDF file
            
        Returns:
            str: Extracted text with preserved formatting
        """
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Method 1: Try pdfplumber first (best for text-based PDFs)
            text_content = self._extract_with_pdfplumber(uploaded_file)
            
            # If pdfplumber fails or returns minimal text, try OCR
            if not text_content.strip() or len(text_content.strip()) < 50:
                uploaded_file.seek(0)
                text_content = self._extract_with_ocr(uploaded_file)
            
            # Clean and preserve formatting
            cleaned_text = self._clean_and_preserve_text(text_content)
            
            return cleaned_text
            
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def _extract_with_pdfplumber(self, uploaded_file) -> str:
        """Extract text using pdfplumber for text-based PDFs"""
        try:
            text_content = ""
            
            with pdfplumber.open(uploaded_file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f"\n--- Page {page_num + 1} ---\n"
                            text_content += page_text + "\n"
                        
                        # Also try to extract tables
                        tables = page.extract_tables()
                        for table_num, table in enumerate(tables):
                            if table:
                                text_content += f"\n--- Table {table_num + 1} on Page {page_num + 1} ---\n"
                                for row in table:
                                    if row:
                                        row_text = " | ".join([str(cell) if cell else "" for cell in row])
                                        text_content += row_text + "\n"
                    
                    except Exception as e:
                        st.warning(f"Error extracting from page {page_num + 1}: {str(e)}")
                        continue
            
            return text_content
            
        except Exception as e:
            st.warning(f"PDFPlumber extraction failed: {str(e)}")
            return ""
    
    def _extract_with_ocr(self, uploaded_file) -> str:
        """Extract text using OCR for image-based or scanned PDFs"""
        try:
            text_content = ""
            
            # Convert PDF to images using PyMuPDF
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            
            for page_num in range(len(pdf_document)):
                try:
                    page = pdf_document.load_page(page_num)
                    
                    # Convert to image with high DPI for better OCR
                    mat = fitz.Matrix(3.0, 3.0)  # High resolution matrix
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    
                    # Convert to PIL Image
                    pil_image = Image.open(io.BytesIO(img_data))
                    
                    # Enhance image for better OCR
                    enhanced_image = self._enhance_image_for_ocr(pil_image)
                    
                    # Perform OCR with multiple methods
                    page_text = self._perform_enhanced_ocr(enhanced_image)
                    
                    if page_text.strip():
                        text_content += f"\n--- Page {page_num + 1} (OCR) ---\n"
                        text_content += page_text + "\n"
                
                except Exception as e:
                    st.warning(f"OCR failed for page {page_num + 1}: {str(e)}")
                    continue
            
            pdf_document.close()
            return text_content
            
        except Exception as e:
            st.warning(f"OCR extraction failed: {str(e)}")
            return ""
    
    def _enhance_image_for_ocr(self, pil_image):
        """Enhance image quality for better OCR accuracy"""
        try:
            # Convert PIL to OpenCV
            cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (1, 1), 0)
            
            # Apply adaptive threshold for better text separation
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to PIL Image
            enhanced_image = Image.fromarray(cleaned)
            
            return enhanced_image
            
        except Exception as e:
            # Return original if enhancement fails
            return pil_image
    
    def _perform_enhanced_ocr(self, image):
        """Perform OCR with multiple configurations for maximum accuracy"""
        try:
            # Primary OCR with high accuracy settings
            text = pytesseract.image_to_string(
                image, 
                config=self.ocr_config,
                lang=self.languages
            )
            
            # If primary OCR yields little text, try alternative configurations
            if len(text.strip()) < 20:
                # Try with different PSM modes
                alt_configs = [
                    r'--oem 3 --psm 4',  # Single column text
                    r'--oem 3 --psm 7',  # Single text line
                    r'--oem 3 --psm 8',  # Single word
                    r'--oem 3 --psm 12'  # Sparse text
                ]
                
                for config in alt_configs:
                    alt_text = pytesseract.image_to_string(image, config=config)
                    if len(alt_text.strip()) > len(text.strip()):
                        text = alt_text
                        break
            
            return text
            
        except Exception as e:
            st.warning(f"OCR processing failed: {str(e)}")
            return ""
    
    def _clean_and_preserve_text(self, text: str) -> str:
        """Clean text while preserving formatting and multilingual content"""
        if not text:
            return ""
        
        # Remove excessive whitespace while preserving structure
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Preserve lines that contain meaningful content
            cleaned_line = ' '.join(line.split())
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
            elif cleaned_lines and cleaned_lines[-1]:  # Preserve paragraph breaks
                cleaned_lines.append('')
        
        # Join lines back together
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Apply common OCR error corrections
        cleaned_text = self._fix_common_ocr_errors(cleaned_text)
        
        return cleaned_text
    
    def _fix_common_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors while preserving multilingual content"""
        
        # Common OCR character substitutions
        corrections = {
            'rn': 'm',
            'vv': 'w',
            '|': 'l',
            '0': 'O',  # Context-dependent
            '1': 'I',  # Context-dependent
            '5': 'S',  # Context-dependent
        }
        
        # Apply corrections selectively (only for clearly misrecognized patterns)
        corrected_text = text
        
        # Fix spacing issues while preserving natural word boundaries
        corrected_text = re.sub(r'\s+', ' ', corrected_text)
        
        # Add spaces between concatenated words (common OCR issue)
        # Detect lowercase followed by uppercase (camelCase or merged words)
        corrected_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', corrected_text)
        
        # Add spaces between letters and numbers when appropriate
        corrected_text = re.sub(r'([a-zA-Z])([0-9])', r'\1 \2', corrected_text)
        corrected_text = re.sub(r'([0-9])([a-zA-Z])', r'\1 \2', corrected_text)
        
        # Fix common merged word patterns
        # Example: "loadingmaterial" -> "loading material"
        common_word_patterns = [
            (r'loading([a-z])', r'loading \1'),
            (r'material([a-z])', r'material \1'),
            (r'concrete([a-z])', r'concrete \1'),
            (r'excavation([a-z])', r'excavation \1'),
            (r'construction([a-z])', r'construction \1'),
            (r'equipment([a-z])', r'equipment \1'),
            (r'([a-z])work', r'\1 work'),
            (r'([a-z])site', r'\1 site'),
            (r'([a-z])area', r'\1 area'),
            (r'([a-z])operation', r'\1 operation'),
        ]
        
        for pattern, replacement in common_word_patterns:
            corrected_text = re.sub(pattern, replacement, corrected_text, flags=re.IGNORECASE)
        
        return corrected_text
    
    def extract_metadata(self, uploaded_file) -> Dict:
        """Extract metadata from PDF"""
        try:
            uploaded_file.seek(0)
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            
            metadata = {
                'title': pdf_document.metadata.get('title', ''),
                'author': pdf_document.metadata.get('author', ''),
                'subject': pdf_document.metadata.get('subject', ''),
                'creator': pdf_document.metadata.get('creator', ''),
                'producer': pdf_document.metadata.get('producer', ''),
                'creation_date': pdf_document.metadata.get('creationDate', ''),
                'modification_date': pdf_document.metadata.get('modDate', ''),
                'page_count': len(pdf_document),
                'encrypted': pdf_document.is_encrypted
            }
            
            pdf_document.close()
            return metadata
            
        except Exception as e:
            st.warning(f"Could not extract metadata: {str(e)}")
            return {}