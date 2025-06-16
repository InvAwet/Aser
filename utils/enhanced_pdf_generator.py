
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.utils import ImageReader
import io
import os
from typing import List, Dict, Optional
from utils.data_models import DailyDiaryData
from PIL import Image

class EnhancedPDFGenerator:
    """Enhanced PDF Generator that creates a Daily Diary form matching the exact reference layout"""

    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 10 * mm  # Minimal margin for maximum space utilization
        self.setup_styles()

    def setup_styles(self):
        """Setup text styles for the PDF"""
        self.styles = getSampleStyleSheet()

        # Custom styles with improved font sizes for better readability
        self.header_style = ParagraphStyle(
            'HeaderStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold'
        )

        self.normal_style = ParagraphStyle(
            'NormalStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName='Helvetica'
        )

        self.small_style = ParagraphStyle(
            'SmallStyle',
            parent=self.styles['Normal'],
            fontSize=7,
            fontName='Helvetica'
        )

    def generate_daily_diary_pdf(self, data: DailyDiaryData) -> bytes:
        """Generate Daily Diary PDF matching exact reference layout"""
        try:
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)

            # Calculate positions based on reference image proportions
            current_y = self.page_height - self.margin
            
            # Draw all sections with exact spacing from reference
            current_y = self._draw_header_section(c, data, current_y)
            current_y = self._draw_title_section(c, data, current_y)
            current_y = self._draw_project_section(c, data, current_y)
            current_y = self._draw_date_weather_section(c, data, current_y)
            current_y = self._draw_activities_section(c, data, current_y)
            current_y = self._draw_equipment_section(c, data, current_y)
            current_y = self._draw_personnel_section(c, data, current_y)
            current_y = self._draw_unsafe_acts_section(c, data, current_y)
            current_y = self._draw_additional_sections(c, data, current_y)
            current_y = self._draw_signatures_section(c, data, current_y)

            c.save()
            pdf_bytes = buffer.getvalue()
            buffer.close()
            return pdf_bytes

        except Exception as e:
            raise Exception(f"Error generating PDF: {str(e)}")

    def _find_nicholas_logo(self):
        """Find Nicholas O'Dwyer logo file"""
        possible_files = [
            "attached_assets/download_1750012790494.png",
            "attached_assets/nicholas_odwyer_logo.png",
            "attached_assets/nicholas_logo.png"
        ]
        for filepath in possible_files:
            if os.path.exists(filepath):
                return filepath
        return None

    def _find_ms_logo(self):
        """Find MS Consultancy logo file"""
        possible_files = [
            "attached_assets/MS-LOGO-with-text-cut-out_1750012778072.png",
            "attached_assets/ms_consultancy_logo.png",
            "attached_assets/ms_logo.png"
        ]
        for filepath in possible_files:
            if os.path.exists(filepath):
                return filepath
        return None

    def _draw_header_section(self, c, data, start_y):
        """Draw header section with improved spacing and logo sizes"""
        section_height = 22*mm  # Increased height for better spacing
        section_bottom = start_y - section_height

        # Main border
        c.rect(10*mm, section_bottom, 190*mm, section_height)

        # Vertical dividers - matching reference layout
        c.line(85*mm, section_bottom, 85*mm, start_y)  # Company info divider
        c.line(160*mm, section_bottom, 160*mm, start_y)  # "in Jv with" divider

        # Nicholas O'Dwyer logo and text (left section)
        nicholas_logo_path = self._find_nicholas_logo()
        if nicholas_logo_path and os.path.exists(nicholas_logo_path):
            try:
                c.drawImage(nicholas_logo_path, 12*mm, section_bottom + 10*mm, 
                           width=30*mm, height=10*mm, preserveAspectRatio=True, mask='auto')
            except:
                c.setFont("Helvetica-Bold", 9)
                c.drawString(12*mm, section_bottom + 15*mm, "NICHOLAS")
                c.drawString(12*mm, section_bottom + 10*mm, "O'DWYER")
        else:
            c.setFont("Helvetica-Bold", 9)
            c.drawString(12*mm, section_bottom + 15*mm, "NICHOLAS")
            c.drawString(12*mm, section_bottom + 10*mm, "O'DWYER")

        # Company details (center section)
        c.setFont("Helvetica", 7)
        c.drawString(87*mm, section_bottom + 17*mm, "Company Name")
        c.setFont("Helvetica", 6)
        c.drawString(87*mm, section_bottom + 14*mm, "Unit E4, Nutgrove Office Park,")
        c.drawString(87*mm, section_bottom + 11.5*mm, "Nutgrove Avenue, Dublin 14")
        c.drawString(87*mm, section_bottom + 9*mm, "T +353 1 296 9000")
        c.drawString(87*mm, section_bottom + 6.5*mm, "F +353 1 296 9001")
        c.drawString(87*mm, section_bottom + 4*mm, "E dublin@nodwyer.com")

        # "in Jv with" section (right)
        c.setFont("Helvetica", 7)
        c.drawString(162*mm, section_bottom + 17*mm, "in Jv with")

        # MS Consultancy logo
        ms_logo_path = self._find_ms_logo()
        if ms_logo_path and os.path.exists(ms_logo_path):
            try:
                c.drawImage(ms_logo_path, 162*mm, section_bottom + 3*mm, 
                           width=35*mm, height=12*mm, preserveAspectRatio=True, mask='auto')
            except:
                c.setFont("Helvetica-Bold", 8)
                c.drawString(162*mm, section_bottom + 10*mm, "MS Consultancy")
        else:
            c.setFont("Helvetica-Bold", 8)
            c.drawString(162*mm, section_bottom + 10*mm, "MS Consultancy")

        return section_bottom

    def _draw_title_section(self, c, data, start_y):
        """Draw title section with improved spacing"""
        section_height = 10*mm  # Increased height
        section_bottom = start_y - section_height

        c.rect(10*mm, section_bottom, 190*mm, section_height)

        # Vertical dividers
        c.line(80*mm, section_bottom, 80*mm, start_y)
        c.line(135*mm, section_bottom, 135*mm, start_y)

        c.setFont("Helvetica", 8)
        c.drawString(12*mm, section_bottom + 4*mm, "Title: Daily Diary")
        c.drawString(82*mm, section_bottom + 4*mm, "Document No:")
        c.drawString(137*mm, section_bottom + 4*mm, "Page No.   of")

        return section_bottom

    def _draw_project_section(self, c, data, start_y):
        """Draw project section with improved spacing"""
        section_height = 14*mm  # Increased height
        section_bottom = start_y - section_height

        c.rect(10*mm, section_bottom, 190*mm, section_height)

        # Equal column widths - 4 columns
        col_width = 190*mm / 4
        for i in range(1, 4):
            x_pos = 10*mm + (i * col_width)
            c.line(x_pos, section_bottom, x_pos, start_y)

        # Headers
        c.setFont("Helvetica-Bold", 8)
        c.drawString(12*mm, start_y - 3*mm, "PROJECT")
        c.drawString(12*mm + col_width, start_y - 3*mm, "EMPLOYER")
        c.drawString(12*mm + (2*col_width), start_y - 3*mm, "CONSULTANT")
        c.drawString(12*mm + (3*col_width), start_y - 3*mm, "CONTRACTOR")

        # Data
        c.setFont("Helvetica", 7)
        c.drawString(12*mm, section_bottom + 7*mm, self._safe_text(getattr(data, 'project', '')))
        c.drawString(12*mm + col_width, section_bottom + 7*mm, self._safe_text(getattr(data, 'employer', '')))
        c.drawString(12*mm + (2*col_width), section_bottom + 7*mm, self._safe_text(getattr(data, 'consultant', '')))
        c.drawString(12*mm + (3*col_width), section_bottom + 7*mm, self._safe_text(getattr(data, 'contractor', '')))

        return section_bottom

    def _draw_date_weather_section(self, c, data, start_y):
        """Draw date and weather section"""
        section_height = 8*mm
        section_bottom = start_y - section_height

        c.rect(10*mm, section_bottom, 190*mm, section_height)

        # Dividers
        c.line(50*mm, section_bottom, 50*mm, start_y)
        c.line(130*mm, section_bottom, 130*mm, start_y)
        c.line(160*mm, section_bottom, 160*mm, start_y)

        c.setFont("Helvetica", 7)
        c.drawString(12*mm, section_bottom + 3*mm, f"1. Date: {self._safe_text(getattr(data, 'date', ''))}")
        c.drawString(52*mm, section_bottom + 3*mm, "Weather condition: ")
        c.drawString(132*mm, section_bottom + 3*mm, "Morning")
        c.drawString(162*mm, section_bottom + 3*mm, "Afternoon")

        # Time checkboxes
        morning_check = "☑" if getattr(data, 'time_morning', False) else "☐"
        afternoon_check = "☑" if getattr(data, 'time_afternoon', False) else "☐"
        c.drawString(145*mm, section_bottom + 3*mm, morning_check)
        c.drawString(180*mm, section_bottom + 3*mm, afternoon_check)

        return section_bottom

    def _draw_activities_section(self, c, data, start_y):
        """Draw activities section matching reference"""
        section_height = 25*mm
        section_bottom = start_y - section_height

        c.rect(10*mm, section_bottom, 190*mm, section_height)

        # Title
        c.setFont("Helvetica", 7)
        c.drawString(12*mm, start_y - 3*mm, "3. Major Activities on progress, Chain age and Location")

        # Table header
        header_y = start_y - 6*mm
        c.line(10*mm, header_y, 200*mm, header_y)
        c.line(20*mm, section_bottom, 20*mm, header_y)

        c.setFont("Helvetica-Bold", 6)
        c.drawString(12*mm, header_y + 1*mm, "sn")
        c.drawString(22*mm, header_y + 1*mm, "Description/Topic - Contractor's work")

        # Activity rows
        activities = getattr(data, 'activities', []) or []
        row_height = 3.8*mm

        for i in range(5):  # 5 rows as shown in reference
            row_y = header_y - (i + 1) * row_height
            c.line(10*mm, row_y, 200*mm, row_y)

            if i < len(activities):
                activity = activities[i]
                c.setFont("Helvetica", 6)
                c.drawString(12*mm, row_y + 1*mm, str(activity.get('sn', i + 1)))
                self._draw_text_in_cell(c, self._safe_text(activity.get('description', '')), 
                                      22*mm, row_y + 1*mm, 175*mm)

        return section_bottom

    def _draw_equipment_section(self, c, data, start_y):
        """Draw equipment section with exact layout from reference"""
        section_height = 22*mm
        section_bottom = start_y - section_height

        c.rect(10*mm, section_bottom, 190*mm, section_height)

        # Title
        c.setFont("Helvetica", 7)
        c.drawString(12*mm, start_y - 3*mm, "4. Contractor's Equipment (dumper truck, excavator, water pump etc.)")

        # Headers
        header_y = start_y - 6*mm
        c.line(10*mm, header_y, 200*mm, header_y)

        # Column layout: sn(15) Equipment(55) NO(25) | sn(15) Equipment(55) NO(25)
        col_positions = [20*mm, 45*mm, 70*mm, 105*mm, 130*mm, 155*mm]
        for pos in col_positions:
            c.line(pos, section_bottom, pos, header_y)

        c.setFont("Helvetica-Bold", 6)
        c.drawString(12*mm, header_y + 1*mm, "sn")
        c.drawString(22*mm, header_y + 1*mm, "Equipment")
        c.drawString(72*mm, header_y + 1*mm, "NO")
        c.drawString(107*mm, header_y + 1*mm, "sn")
        c.drawString(132*mm, header_y + 1*mm, "Equipment")
        c.drawString(157*mm, header_y + 1*mm, "NO")

        # Equipment rows
        equipment = getattr(data, 'equipment', []) or []
        row_height = 3.2*mm

        for i in range(5):  # 5 rows as in reference
            row_y = header_y - (i + 1) * row_height
            c.line(10*mm, row_y, 200*mm, row_y)

            c.setFont("Helvetica", 6)

            # Left column (items 1-5)
            if i < len(equipment):
                eq = equipment[i]
                c.drawString(12*mm, row_y + 0.5*mm, str(eq.get('sn', i + 1)))
                self._draw_text_in_cell(c, self._safe_text(eq.get('equipment', '')), 
                                      22*mm, row_y + 0.5*mm, 45*mm)
                c.drawString(72*mm, row_y + 0.5*mm, self._safe_text(eq.get('no', '')))

            # Right column (items 6-10)
            right_idx = i + 5
            if right_idx < len(equipment):
                eq = equipment[right_idx]
                c.drawString(107*mm, row_y + 0.5*mm, str(eq.get('sn', right_idx + 1)))
                self._draw_text_in_cell(c, self._safe_text(eq.get('equipment', '')), 
                                      132*mm, row_y + 0.5*mm, 45*mm)
                c.drawString(157*mm, row_y + 0.5*mm, self._safe_text(eq.get('no', '')))

        return section_bottom

    def _draw_personnel_section(self, c, data, start_y):
        """Draw personnel section with exact layout from reference (28 rows total)"""
        section_height = 55*mm
        section_bottom = start_y - section_height

        c.rect(10*mm, section_bottom, 190*mm, section_height)

        # Title
        c.setFont("Helvetica", 7)
        c.drawString(12*mm, start_y - 3*mm, "5. Contractor's Personnel (Foreman, laborer, driver etc.)")

        # Headers
        header_y = start_y - 6*mm
        c.line(10*mm, header_y, 200*mm, header_y)

        # Same column layout as equipment
        col_positions = [20*mm, 45*mm, 70*mm, 105*mm, 130*mm, 155*mm]
        for pos in col_positions:
            c.line(pos, section_bottom, pos, header_y)

        c.setFont("Helvetica-Bold", 6)
        c.drawString(12*mm, header_y + 1*mm, "sn")
        c.drawString(22*mm, header_y + 1*mm, "Personnel")
        c.drawString(72*mm, header_y + 1*mm, "No.")
        c.drawString(107*mm, header_y + 1*mm, "sn")
        c.drawString(132*mm, header_y + 1*mm, "Personnel")
        c.drawString(157*mm, header_y + 1*mm, "No.")

        # Personnel rows - 14 rows per column (28 total)
        personnel = getattr(data, 'personnel', []) or []
        row_height = 3.5*mm

        for i in range(14):  # 14 rows as shown in reference
            row_y = header_y - (i + 1) * row_height
            c.line(10*mm, row_y, 200*mm, row_y)

            c.setFont("Helvetica", 6)

            # Left column (items 1-14)
            if i < len(personnel):
                person = personnel[i]
                c.drawString(12*mm, row_y + 0.5*mm, str(person.get('sn', i + 1)))
                self._draw_text_in_cell(c, self._safe_text(person.get('personnel', '')), 
                                      22*mm, row_y + 0.5*mm, 45*mm)
                c.drawString(72*mm, row_y + 0.5*mm, self._safe_text(person.get('no', '')))

            # Right column (items 15-28)
            right_idx = i + 14
            if right_idx < len(personnel):
                person = personnel[right_idx]
                c.drawString(107*mm, row_y + 0.5*mm, str(person.get('sn', right_idx + 1)))
                self._draw_text_in_cell(c, self._safe_text(person.get('personnel', '')), 
                                      132*mm, row_y + 0.5*mm, 45*mm)
                c.drawString(157*mm, row_y + 0.5*mm, self._safe_text(person.get('no', '')))

        return section_bottom

    def _draw_unsafe_acts_section(self, c, data, start_y):
        """Draw unsafe acts section with improved spacing"""
        section_height = 18*mm  # Increased height
        section_bottom = start_y - section_height

        c.rect(10*mm, section_bottom, 190*mm, section_height)

        # Title
        c.setFont("Helvetica", 8)
        c.drawString(12*mm, start_y - 3*mm, "6. Unsafe Acts / Conditions Observed")

        # Headers
        header_y = start_y - 7*mm
        c.line(10*mm, header_y, 200*mm, header_y)
        c.line(20*mm, section_bottom, 20*mm, header_y)

        c.setFont("Helvetica-Bold", 7)
        c.drawString(12*mm, header_y + 1*mm, "sn")
        c.drawString(22*mm, header_y + 1*mm, "Description of Unsafe Acts")

        # Unsafe acts rows
        unsafe_acts = getattr(data, 'unsafe_acts', []) or []
        row_height = 5.5*mm  # Increased row height

        for i in range(2):  # 2 rows as in reference
            row_y = header_y - (i + 1) * row_height
            c.line(10*mm, row_y, 200*mm, row_y)

            if i < len(unsafe_acts):
                act = unsafe_acts[i]
                c.setFont("Helvetica", 7)
                c.drawString(12*mm, row_y + 2*mm, str(act.get('sn', i + 1)))
                self._draw_text_in_cell(c, self._safe_text(act.get('description', '')), 
                                      22*mm, row_y + 2*mm, 175*mm)

        return section_bottom

    def _draw_additional_sections(self, c, data, start_y):
        """Draw additional sections with improved spacing and font sizes"""
        # Near Miss section
        near_miss_height = 12*mm  # Increased height
        near_miss_bottom = start_y - near_miss_height

        c.rect(10*mm, near_miss_bottom, 190*mm, near_miss_height)
        c.setFont("Helvetica", 8)
        c.drawString(12*mm, near_miss_bottom + 8*mm, "7. Near Miss/Accidents/Incidents:")
        c.setFont("Helvetica", 7)
        self._draw_text_in_cell(c, self._safe_text(getattr(data, 'near_miss', '')), 
                              12*mm, near_miss_bottom + 4*mm, 185*mm)

        # Obstruction section
        obstruction_height = 12*mm  # Increased height
        obstruction_bottom = near_miss_bottom - obstruction_height

        c.rect(10*mm, obstruction_bottom, 190*mm, obstruction_height)
        c.setFont("Helvetica", 8)
        c.drawString(12*mm, obstruction_bottom + 8*mm, "8. Obstruction/Action Plans:")
        c.setFont("Helvetica", 7)
        self._draw_text_in_cell(c, self._safe_text(getattr(data, 'obstruction', '')), 
                              12*mm, obstruction_bottom + 4*mm, 185*mm)

        # Engineer's Note section
        engineers_height = 20*mm  # Increased height for more space
        engineers_bottom = obstruction_bottom - engineers_height

        c.rect(10*mm, engineers_bottom, 190*mm, engineers_height)
        c.setFont("Helvetica", 8)
        c.drawString(12*mm, engineers_bottom + 16*mm, "9. Engineer's Note:")
        c.setFont("Helvetica", 7)
        self._draw_text_in_cell(c, self._safe_text(getattr(data, 'engineers_note', '')), 
                              12*mm, engineers_bottom + 10*mm, 185*mm)

        return engineers_bottom

    def _draw_signatures_section(self, c, data, start_y):
        """Draw signatures section with improved spacing"""
        section_height = 30*mm  # Increased height
        section_bottom = start_y - section_height

        # Three equal columns
        col_width = 190*mm / 3
        
        # Column dividers
        c.line(10*mm + col_width, section_bottom, 10*mm + col_width, start_y)
        c.line(10*mm + (2*col_width), section_bottom, 10*mm + (2*col_width), start_y)

        c.setFont("Helvetica-Bold", 8)
        c.drawString(12*mm, start_y - 5*mm, "Prepared by")
        c.drawString(12*mm + col_width, start_y - 5*mm, "Checked by")
        c.drawString(12*mm + (2*col_width), start_y - 5*mm, "Approved by")

        c.setFont("Helvetica", 7)
        c.drawString(12*mm, start_y - 9*mm, "Construction Staff")
        c.drawString(12*mm + col_width, start_y - 9*mm, "Consultant Supervision Staff")
        c.drawString(12*mm + (2*col_width), start_y - 9*mm, "Consultant Supervision Staff")

        # Name lines
        c.drawString(12*mm, start_y - 15*mm, f"Name: {self._safe_text(getattr(data, 'prepared_by', ''))}")
        c.drawString(12*mm + col_width, start_y - 15*mm, f"Name: {self._safe_text(getattr(data, 'checked_by', ''))}")
        c.drawString(12*mm + (2*col_width), start_y - 15*mm, f"Name: {self._safe_text(getattr(data, 'approved_by', ''))}")

        # Signature lines
        c.drawString(12*mm, start_y - 20*mm, "Sign: ________________")
        c.drawString(12*mm + col_width, start_y - 20*mm, "Sign: ________________")
        c.drawString(12*mm + (2*col_width), start_y - 20*mm, "Sign: ________________")

        return section_bottom

    def _draw_text_in_cell(self, c, text, x, y, max_width):
        """Draw text within a cell with smart truncation"""
        if not text:
            return

        if c.stringWidth(text, c._fontname, c._fontsize) <= max_width:
            c.drawString(x, y, text)
        else:
            # Truncate text to fit
            truncated = text
            while len(truncated) > 0 and c.stringWidth(truncated + "...", c._fontname, c._fontsize) > max_width:
                truncated = truncated[:-1]
            c.drawString(x, y, truncated + "..." if truncated else "")

    def _safe_text(self, text):
        """Safely convert text to string, handling None values"""
        if text is None:
            return ""
        return str(text)
