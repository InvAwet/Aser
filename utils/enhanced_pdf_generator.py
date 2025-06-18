from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
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
from .daily_diary_template import DailyDiaryTemplate

class EnhancedPDFGenerator:
    """Complete Daily Diary PDF Generator with fixed text overflow issues"""

    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 10 * mm
        self.template = DailyDiaryTemplate()  # Template with logos
        self.setup_styles()
    
    def setup_styles(self):
        """Setup all text styles for the PDF"""
        self.styles = getSampleStyleSheet()

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

    def generate(self, data: DailyDiaryData) -> bytes:
        """Main generate method that uses template logos"""
        return self.generate_daily_diary_pdf(data)

    def generate_daily_diary_pdf(self, data: DailyDiaryData) -> bytes:
        """Generate complete Daily Diary PDF with all sections"""
        try:
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)

            current_y = self.page_height - self.margin
            
            # Draw all sections in order
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

    def _draw_header_section(self, c, data, start_y):
        """Complete header section with logos"""
        section_height = 22*mm
        section_bottom = start_y - section_height

        # Main border and dividers
        c.rect(10*mm, section_bottom, 190*mm, section_height)
        c.line(85*mm, section_bottom, 85*mm, start_y)
        c.line(160*mm, section_bottom, 160*mm, start_y)

        # Nicholas O'Dwyer logo
        if self.template.logos['nod']:
            c.drawImage(self.template.logos['nod'], 12*mm, section_bottom + 10*mm, 
                      width=30*mm, height=10*mm, preserveAspectRatio=True)
        else:
            c.setFont("Helvetica-Bold", 9)
            c.drawString(12*mm, section_bottom + 15*mm, "NICHOLAS")
            c.drawString(12*mm, section_bottom + 10*mm, "O'DWYER")

        # Company details
        c.setFont("Helvetica", 7)
        c.drawString(87*mm, section_bottom + 17*mm, "Company Name")
        c.setFont("Helvetica", 6)
        c.drawString(87*mm, section_bottom + 14*mm, "Unit E4, Nutgrove Office Park,")
        c.drawString(87*mm, section_bottom + 11.5*mm, "Nutgrove Avenue, Dublin 14")
        c.drawString(87*mm, section_bottom + 9*mm, "T +353 1 296 9000")
        c.drawString(87*mm, section_bottom + 6.5*mm, "F +353 1 296 9001")
        c.drawString(87*mm, section_bottom + 4*mm, "E dublin@nodwyer.com")

        # MS Consultancy logo
        c.setFont("Helvetica", 7)
        c.drawString(162*mm, section_bottom + 17*mm, "in Jv with")
        
        if self.template.logos['ms']:
            c.drawImage(self.template.logos['ms'], 162*mm, section_bottom + 3*mm,
                      width=35*mm, height=12*mm, preserveAspectRatio=True)
        else:
            c.setFont("Helvetica-Bold", 8)
            c.drawString(162*mm, section_bottom + 10*mm, "MS Consultancy")

        return section_bottom

    def _draw_title_section(self, c, data, start_y):
        """Complete title section"""
        section_height = 10*mm
        section_bottom = start_y - section_height

        c.rect(10*mm, section_bottom, 190*mm, section_height)
        c.line(80*mm, section_bottom, 80*mm, start_y)
        c.line(135*mm, section_bottom, 135*mm, start_y)

        c.setFont("Helvetica", 8)
        c.drawString(12*mm, section_bottom + 4*mm, "Title: Daily Diary")
        c.drawString(82*mm, section_bottom + 4*mm, "Document No:")
        c.drawString(137*mm, section_bottom + 4*mm, "Page No.   of")

        return section_bottom

    def _draw_project_section(self, c, data, start_y):
        """Complete project section with text wrapping"""
        section_height = 20*mm  # Increased height
        section_bottom = start_y - section_height
        col_width = 190*mm / 4

        # Draw borders
        c.rect(10*mm, section_bottom, 190*mm, section_height)
        for i in range(1, 4):
            c.line(10*mm + (i * col_width), section_bottom, 10*mm + (i * col_width), start_y)

        # Headers
        c.setFont("Helvetica-Bold", 8)
        c.drawString(12*mm, start_y - 3*mm, "PROJECT")
        c.drawString(12*mm + col_width, start_y - 3*mm, "EMPLOYER")
        c.drawString(12*mm + (2*col_width), start_y - 3*mm, "CONSULTANT")
        c.drawString(12*mm + (3*col_width), start_y - 3*mm, "CONTRACTOR")

        # Project data with fixed text
        project_text = "Construction of Trunk Lines for Kotebe and Kitime Sub-Catchment of Eastern Sewer Line Project"
        employer_text = "AAWSA-WISIDD, THE WORLD BANK"
        consultant_text = "NICHOLAS O'DWYER LTD. In Jv. with MS CONSULTANCY"
        contractor_text = "ASER CONSTRUCTION PLC"

        # Draw text with wrapping
        self._draw_wrapped_text(c, project_text, 12*mm, start_y - 8*mm, col_width - 4*mm, 7, max_lines=2)
        self._draw_wrapped_text(c, employer_text, 12*mm + col_width, start_y - 8*mm, col_width - 4*mm, 7, max_lines=1)
        self._draw_wrapped_text(c, consultant_text, 12*mm + (2*col_width), start_y - 8*mm, col_width - 4*mm, 7, max_lines=2)
        self._draw_wrapped_text(c, contractor_text, 12*mm + (3*col_width), start_y - 8*mm, col_width - 4*mm, 7, max_lines=1)

        return section_bottom

    def _draw_date_weather_section(self, c, data, start_y):
        """Complete date and weather section"""
        section_height = 8*mm
        section_bottom = start_y - section_height

        c.rect(10*mm, section_bottom, 190*mm, section_height)
        c.line(50*mm, section_bottom, 50*mm, start_y)
        c.line(130*mm, section_bottom, 130*mm, start_y)
        c.line(160*mm, section_bottom, 160*mm, start_y)

        c.setFont("Helvetica", 7)
        c.drawString(12*mm, section_bottom + 3*mm, f"1. Date: {self._safe_text(getattr(data, 'date', ''))}")
        c.drawString(52*mm, section_bottom + 3*mm, "Weather condition: ")
        c.drawString(132*mm, section_bottom + 3*mm, "Morning")
        c.drawString(162*mm, section_bottom + 3*mm, "Afternoon")

        # Checkboxes
        morning_check = "☑" if getattr(data, 'time_morning', False) else "☐"
        afternoon_check = "☑" if getattr(data, 'time_afternoon', False) else "☐"
        c.drawString(145*mm, section_bottom + 3*mm, morning_check)
        c.drawString(180*mm, section_bottom + 3*mm, afternoon_check)

        return section_bottom

    def _draw_activities_section(self, c, data, start_y):
        """Complete activities section with improved text handling"""
        section_height = 40*mm  # Increased height
        section_bottom = start_y - section_height
        row_height = 6*mm  # Increased row height

        c.rect(10*mm, section_bottom, 190*mm, section_height)
        c.setFont("Helvetica", 7)
        c.drawString(12*mm, start_y - 3*mm, "3. Major Activities on progress, Chain age and Location")

        header_y = start_y - 6*mm
        c.line(10*mm, header_y, 200*mm, header_y)
        c.line(20*mm, section_bottom, 20*mm, header_y)

        # Headers
        c.setFont("Helvetica-Bold", 6)
        c.drawString(12*mm, header_y + 1*mm, "sn")
        c.drawString(22*mm, header_y + 1*mm, "Description/Topic - Contractor's work")

        activities = getattr(data, 'activities', []) or []
        for i in range(5):
            row_y = header_y - (i + 1) * row_height
            c.line(10*mm, row_y, 200*mm, row_y)

            if i < len(activities):
                activity = activities[i]
                c.setFont("Helvetica", 6)
                c.drawString(12*mm, row_y + 1*mm, str(activity.get('sn', i + 1)))
                self._draw_wrapped_text(c, self._safe_text(activity.get('description', '')), 
                                     22*mm, row_y + 1*mm, 175*mm, 6, max_lines=2)

        return section_bottom

    def _draw_equipment_section(self, c, data, start_y):
        """Complete equipment section"""
        section_height = 22*mm
        section_bottom = start_y - section_height

        c.rect(10*mm, section_bottom, 190*mm, section_height)
        c.setFont("Helvetica", 7)
        c.drawString(12*mm, start_y - 3*mm, "4. Contractor's Equipment (dumper truck, excavator, water pump etc.)")

        header_y = start_y - 6*mm
        c.line(10*mm, header_y, 200*mm, header_y)

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

        equipment = getattr(data, 'equipment', []) or []
        row_height = 3.2*mm

        for i in range(5):
            row_y = header_y - (i + 1) * row_height
            c.line(10*mm, row_y, 200*mm, row_y)

            c.setFont("Helvetica", 6)

            if i < len(equipment):
                eq = equipment[i]
                c.drawString(12*mm, row_y + 0.5*mm, str(eq.get('sn', i + 1)))
                self._draw_wrapped_text(c, self._safe_text(eq.get('equipment', '')), 
                                     22*mm, row_y + 0.5*mm, 45*mm, 6)
                c.drawString(72*mm, row_y + 0.5*mm, self._safe_text(eq.get('no', '')))

            right_idx = i + 5
            if right_idx < len(equipment):
                eq = equipment[right_idx]
                c.drawString(107*mm, row_y + 0.5*mm, str(eq.get('sn', right_idx + 1)))
                self._draw_wrapped_text(c, self._safe_text(eq.get('equipment', '')), 
                                     132*mm, row_y + 0.5*mm, 45*mm, 6)
                c.drawString(157*mm, row_y + 0.5*mm, self._safe_text(eq.get('no', '')))

        return section_bottom

    def _draw_personnel_section(self, c, data, start_y):
        """Complete personnel section with improved layout"""
        section_height = 70*mm  # Increased height
        section_bottom = start_y - section_height
        row_height = 4*mm  # Adjusted row height

        c.rect(10*mm, section_bottom, 190*mm, section_height)
        c.setFont("Helvetica", 7)
        c.drawString(12*mm, start_y - 3*mm, "5. Contractor's Personnel (Foreman, laborer, driver etc.)")

        header_y = start_y - 6*mm
        c.line(10*mm, header_y, 200*mm, header_y)

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

        personnel = getattr(data, 'personnel', []) or []
        for i in range(14):
            row_y = header_y - (i + 1) * row_height
            c.line(10*mm, row_y, 200*mm, row_y)

            c.setFont("Helvetica", 6)

            if i < len(personnel):
                person = personnel[i]
                c.drawString(12*mm, row_y + 0.5*mm, str(person.get('sn', i + 1)))
                self._draw_wrapped_text(c, self._safe_text(person.get('personnel', '')), 
                                     22*mm, row_y + 0.5*mm, 45*mm, 6)
                c.drawString(72*mm, row_y + 0.5*mm, self._safe_text(person.get('no', '')))

            right_idx = i + 14
            if right_idx < len(personnel):
                person = personnel[right_idx]
                c.drawString(107*mm, row_y + 0.5*mm, str(person.get('sn', right_idx + 1)))
                self._draw_wrapped_text(c, self._safe_text(person.get('personnel', '')), 
                                     132*mm, row_y + 0.5*mm, 45*mm, 6)
                c.drawString(157*mm, row_y + 0.5*mm, self._safe_text(person.get('no', '')))

        return section_bottom

    def _draw_unsafe_acts_section(self, c, data, start_y):
        """Complete unsafe acts section"""
        section_height = 18*mm
        section_bottom = start_y - section_height

        c.rect(10*mm, section_bottom, 190*mm, section_height)
        c.setFont("Helvetica", 8)
        c.drawString(12*mm, start_y - 3*mm, "6. Unsafe Acts / Conditions Observed")

        header_y = start_y - 7*mm
        c.line(10*mm, header_y, 200*mm, header_y)
        c.line(20*mm, section_bottom, 20*mm, header_y)

        c.setFont("Helvetica-Bold", 7)
        c.drawString(12*mm, header_y + 1*mm, "sn")
        c.drawString(22*mm, header_y + 1*mm, "Description of Unsafe Acts")

        unsafe_acts = getattr(data, 'unsafe_acts', []) or []
        row_height = 5.5*mm

        for i in range(2):
            row_y = header_y - (i + 1) * row_height
            c.line(10*mm, row_y, 200*mm, row_y)

            if i < len(unsafe_acts):
                act = unsafe_acts[i]
                c.setFont("Helvetica", 7)
                c.drawString(12*mm, row_y + 2*mm, str(act.get('sn', i + 1)))
                self._draw_wrapped_text(c, self._safe_text(act.get('description', '')), 
                                     22*mm, row_y + 2*mm, 175*mm, 7, max_lines=1)

        return section_bottom

    def _draw_additional_sections(self, c, data, start_y):
        """Complete additional sections (near miss, obstruction, engineer's note)"""
        # Near Miss
        near_miss_height = 12*mm
        near_miss_bottom = start_y - near_miss_height
        c.rect(10*mm, near_miss_bottom, 190*mm, near_miss_height)
        c.setFont("Helvetica", 8)
        c.drawString(12*mm, near_miss_bottom + 8*mm, "7. Near Miss/Accidents/Incidents:")
        c.setFont("Helvetica", 7)
        self._draw_wrapped_text(c, self._safe_text(getattr(data, 'near_miss', '')), 
                             12*mm, near_miss_bottom + 4*mm, 185*mm, 7)

        # Obstruction
        obstruction_height = 12*mm
        obstruction_bottom = near_miss_bottom - obstruction_height
        c.rect(10*mm, obstruction_bottom, 190*mm, obstruction_height)
        c.setFont("Helvetica", 8)
        c.drawString(12*mm, obstruction_bottom + 8*mm, "8. Obstruction/Action Plans:")
        c.setFont("Helvetica", 7)
        self._draw_wrapped_text(c, self._safe_text(getattr(data, 'obstruction', '')), 
                             12*mm, obstruction_bottom + 4*mm, 185*mm, 7)

        # Engineer's Note
        engineers_height = 20*mm
        engineers_bottom = obstruction_bottom - engineers_height
        c.rect(10*mm, engineers_bottom, 190*mm, engineers_height)
        c.setFont("Helvetica", 8)
        c.drawString(12*mm, engineers_bottom + 16*mm, "9. Engineer's Note:")
        c.setFont("Helvetica", 7)
        self._draw_wrapped_text(c, self._safe_text(getattr(data, 'engineers_note', '')), 
                             12*mm, engineers_bottom + 10*mm, 185*mm, 7)

        return engineers_bottom

    def _draw_signatures_section(self, c, data, start_y):
        """Complete signatures section"""
        section_height = 30*mm
        section_bottom = start_y - section_height

        col_width = 190*mm / 3
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

        c.drawString(12*mm, start_y - 15*mm, f"Name: {self._safe_text(getattr(data, 'prepared_by', ''))}")
        c.drawString(12*mm + col_width, start_y - 15*mm, f"Name: {self._safe_text(getattr(data, 'checked_by', ''))}")
        c.drawString(12*mm + (2*col_width), start_y - 15*mm, f"Name: {self._safe_text(getattr(data, 'approved_by', ''))}")

        c.drawString(12*mm, start_y - 20*mm, "Sign: ________________")
        c.drawString(12*mm + col_width, start_y - 20*mm, "Sign: ________________")
        c.drawString(12*mm + (2*col_width), start_y - 20*mm, "Sign: ________________")

        return section_bottom

    def _safe_text(self, text):
        """Safely convert text to string"""
        return str(text) if text is not None else ""

    def _draw_wrapped_text(self, c, text, x, y, max_width, font_size, max_lines=1):
        """Improved text wrapping with line limit and ellipsis for overflow"""
        c.setFont("Helvetica", font_size)
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if c.stringWidth(test_line, "Helvetica", font_size) <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                if len(lines) >= max_lines:
                    break
        
        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines[:max_lines]):
            c.drawString(x, y - (i * (font_size + 1)), line)
        
        # Add ellipsis if text was truncated
        if len(lines) == max_lines and len(' '.join(lines)) < len(text):
            last_line = lines[-1]
            # Find how much we can fit with ellipsis
            while last_line and c.stringWidth(last_line + "...", "Helvetica", font_size) > max_width:
                last_line = last_line[:-1]
            if last_line:
                c.drawString(x, y - ((max_lines-1) * (font_size + 1)), last_line + "...")

    def _draw_text_in_cell(self, c, text, x, y, max_width):
        """Legacy method kept for compatibility"""
        self._draw_wrapped_text(c, text, x, y, max_width, c._fontsize)
