from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
import os
from typing import List, Dict, Optional
from utils.data_models import DailyDiaryData
from utils.daily_diary_template import daily_diary_template as template
from PIL import Image

class EnhancedPDFGenerator:
    """Complete Daily Diary PDF Generator with template-integrated logos"""
    
    def __init__(self):
        """Initialize with template configuration"""
        self.page_width, self.page_height = A4
        self.margin = 10 * mm
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
        """
        Generate complete Daily Diary PDF
        
        Args:
            data: DailyDiaryData object containing all report data
            
        Returns:
            bytes: Generated PDF as bytes
        """
        try:
            # Validate template configuration first
            if errors := template.validate_template_config():
                print(f"Template configuration issues: {errors}")
            
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
        """Header section with integrated logos"""
        section_height = 22*mm
        section_bottom = start_y - section_height

        # Main border and dividers
        c.rect(10*mm, section_bottom, 190*mm, section_height)
        c.line(85*mm, section_bottom, 85*mm, start_y)
        c.line(160*mm, section_bottom, 160*mm, start_y)

        # Draw NOD logo (if available)
        if template.logos['nod']:
            c.drawImage(template.logos['nod'], 
                      12*mm, section_bottom + 10*mm, 
                      width=30*mm, height=10*mm, 
                      preserveAspectRatio=True)
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

        # Draw MS logo (if available)
        c.setFont("Helvetica", 7)
        c.drawString(162*mm, section_bottom + 17*mm, "in Jv with")
        
        if template.logos['ms']:
            c.drawImage(template.logos['ms'],
                      162*mm, section_bottom + 3*mm,
                      width=35*mm, height=12*mm,
                      preserveAspectRatio=True)
        else:
            c.setFont("Helvetica-Bold", 8)
            c.drawString(162*mm, section_bottom + 10*mm, "MS Consultancy")

        return section_bottom

    def _draw_title_section(self, c, data, start_y):
        """Title section"""
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
        """Project information section"""
        section_height = 20*mm
        section_bottom = start_y - section_height
        col_width = 190*mm / 4

        # Draw borders
        c.rect(10*mm, section_bottom, 190*mm, section_height)
        for i in range(1, 4):
            c.line(10*mm + (i * col_width), section_bottom, 10*mm + (i * col_width), start_y)

        # Headers
        c.setFont("Helvetica-Bold", 8)
        headers = template.get_project_headers()
        for i, header in enumerate(headers):
            c.drawString(12*mm + (i * col_width), start_y - 3*mm, header)

        # Project data
        project_data = template.get_project_data(data.__dict__)
        c.setFont("Helvetica", 7)
        for i, text in enumerate(project_data):
            self._draw_wrapped_text(
                c, text, 
                12*mm + (i * col_width), start_y - 8*mm,
                col_width - 4*mm, 7, 
                max_lines=2
            )

        return section_bottom

    def _draw_date_weather_section(self, c, data, start_y):
        """Date and weather section"""
        section_height = 8*mm
        section_bottom = start_y - section_height

        c.rect(10*mm, section_bottom, 190*mm, section_height)
        c.line(50*mm, section_bottom, 50*mm, start_y)
        c.line(130*mm, section_bottom, 130*mm, start_y)
        c.line(160*mm, section_bottom, 160*mm, start_y)

        c.setFont("Helvetica", 7)
        c.drawString(12*mm, section_bottom + 3*mm, f"1. Date: {data.date}")
        c.drawString(52*mm, section_bottom + 3*mm, f"Weather condition: {data.weather}")
        c.drawString(132*mm, section_bottom + 3*mm, "Morning")
        c.drawString(162*mm, section_bottom + 3*mm, "Afternoon")

        # Checkboxes
        morning_check = "☑" if data.time_morning else "☐"
        afternoon_check = "☑" if data.time_afternoon else "☐"
        c.drawString(145*mm, section_bottom + 3*mm, morning_check)
        c.drawString(180*mm, section_bottom + 3*mm, afternoon_check)

        return section_bottom

    def _draw_activities_section(self, c, data, start_y):
        """Activities section with dynamic data"""
        section_height = 40*mm
        section_bottom = start_y - section_height
        row_height = 6*mm

        c.rect(10*mm, section_bottom, 190*mm, section_height)
        c.setFont("Helvetica", 7)
        c.drawString(12*mm, start_y - 3*mm, template.get_section_titles()['activities'])

        header_y = start_y - 6*mm
        c.line(10*mm, header_y, 200*mm, header_y)
        c.line(20*mm, section_bottom, 20*mm, header_y)

        # Headers
        headers = template.get_activity_headers()
        c.setFont("Helvetica-Bold", 6)
        c.drawString(12*mm, header_y + 1*mm, headers[0])
        c.drawString(22*mm, header_y + 1*mm, headers[1])

        # Activity rows
        for i, activity in enumerate(data.activities[:6]):  # Limit to 6 rows
            row_y = header_y - (i + 1) * row_height
            c.line(10*mm, row_y, 200*mm, row_y)

            c.setFont("Helvetica", 6)
            c.drawString(12*mm, row_y + 1*mm, str(i + 1))
            
            desc = f"{activity.get('description', '')}"
            if 'location' in activity:
                desc += f"\nLocation: {activity['location']}"
            if 'quantity' in activity:
                desc += f"\nQty: {activity['quantity']} {activity.get('unit', '')}"
            
            self._draw_wrapped_text(
                c, desc,
                22*mm, row_y + 1*mm,
                175*mm, 6,
                max_lines=2
            )

        return section_bottom

    def _draw_equipment_section(self, c, data, start_y):
        """Equipment section with two-column layout"""
        section_height = 22*mm
        section_bottom = start_y - section_height

        c.rect(10*mm, section_bottom, 190*mm, section_height)
        c.setFont("Helvetica", 7)
        c.drawString(12*mm, start_y - 3*mm, template.get_section_titles()['equipment'])

        header_y = start_y - 6*mm
        c.line(10*mm, header_y, 200*mm, header_y)

        col_positions = [20*mm, 45*mm, 70*mm, 105*mm, 130*mm, 155*mm]
        for pos in col_positions:
            c.line(pos, section_bottom, pos, header_y)

        # Headers
        headers = template.get_equipment_headers()
        c.setFont("Helvetica-Bold", 6)
        for i, header in enumerate(headers):
            c.drawString(col_positions[i] - 15*mm, header_y + 1*mm, header)

        # Equipment rows
        row_height = 3.2*mm
        equipment = data.equipment[:10]  # Limit to 10 items (5 per column)

        for i in range(5):
            row_y = header_y - (i + 1) * row_height
            c.line(10*mm, row_y, 200*mm, row_y)

            c.setFont("Helvetica", 6)

            # Left column
            if i < len(equipment[:5]):
                eq = equipment[i]
                c.drawString(12*mm, row_y + 0.5*mm, str(i + 1))
                self._draw_wrapped_text(
                    c, eq.get('equipment', ''),
                    22*mm, row_y + 0.5*mm,
                    45*mm, 6
                )
                c.drawString(72*mm, row_y + 0.5*mm, eq.get('no', ''))

            # Right column
            if i < len(equipment[5:]):
                eq = equipment[i + 5]
                c.drawString(107*mm, row_y + 0.5*mm, str(i + 6))
                self._draw_wrapped_text(
                    c, eq.get('equipment', ''),
                    132*mm, row_y + 0.5*mm,
                    45*mm, 6
                )
                c.drawString(157*mm, row_y + 0.5*mm, eq.get('no', ''))

        return section_bottom

    def _draw_personnel_section(self, c, data, start_y):
        """Personnel section with two-column layout"""
        section_height = 70*mm
        section_bottom = start_y - section_height
        row_height = 4*mm

        c.rect(10*mm, section_bottom, 190*mm, section_height)
        c.setFont("Helvetica", 7)
        c.drawString(12*mm, start_y - 3*mm, template.get_section_titles()['personnel'])

        header_y = start_y - 6*mm
        c.line(10*mm, header_y, 200*mm, header_y)

        col_positions = [20*mm, 45*mm, 70*mm, 105*mm, 130*mm, 155*mm]
        for pos in col_positions:
            c.line(pos, section_bottom, pos, header_y)

        # Headers
        headers = template.get_personnel_headers()
        c.setFont("Helvetica-Bold", 6)
        for i, header in enumerate(headers):
            c.drawString(col_positions[i] - 15*mm, header_y + 1*mm, header)

        # Personnel rows
        personnel = data.personnel[:28]  # Limit to 28 items (14 per column)

        for i in range(14):
            row_y = header_y - (i + 1) * row_height
            c.line(10*mm, row_y, 200*mm, row_y)

            c.setFont("Helvetica", 6)

            # Left column
            if i < len(personnel[:14]):
                person = personnel[i]
                c.drawString(12*mm, row_y + 0.5*mm, str(i + 1))
                self._draw_wrapped_text(
                    c, person.get('personnel', ''),
                    22*mm, row_y + 0.5*mm,
                    45*mm, 6
                )
                c.drawString(72*mm, row_y + 0.5*mm, person.get('no', ''))

            # Right column
            if i < len(personnel[14:]):
                person = personnel[i + 14]
                c.drawString(107*mm, row_y + 0.5*mm, str(i + 15))
                self._draw_wrapped_text(
                    c, person.get('personnel', ''),
                    132*mm, row_y + 0.5*mm,
                    45*mm, 6
                )
                c.drawString(157*mm, row_y + 0.5*mm, person.get('no', ''))

        return section_bottom

    def _draw_unsafe_acts_section(self, c, data, start_y):
        """Unsafe acts section"""
        section_height = 18*mm
        section_bottom = start_y - section_height

        c.rect(10*mm, section_bottom, 190*mm, section_height)
        c.setFont("Helvetica", 8)
        c.drawString(12*mm, start_y - 3*mm, template.get_section_titles()['unsafe_acts'])

        header_y = start_y - 7*mm
        c.line(10*mm, header_y, 200*mm, header_y)
        c.line(20*mm, section_bottom, 20*mm, header_y)

        # Headers
        headers = template.get_unsafe_acts_headers()
        c.setFont("Helvetica-Bold", 7)
        c.drawString(12*mm, header_y + 1*mm, headers[0])
        c.drawString(22*mm, header_y + 1*mm, headers[1])

        # Unsafe acts rows
        row_height = 5.5*mm
        unsafe_acts = data.unsafe_acts[:2]  # Limit to 2 rows

        for i, act in enumerate(unsafe_acts):
            row_y = header_y - (i + 1) * row_height
            c.line(10*mm, row_y, 200*mm, row_y)

            c.setFont("Helvetica", 7)
            c.drawString(12*mm, row_y + 2*mm, str(i + 1))
            self._draw_wrapped_text(
                c, act.get('description', ''),
                22*mm, row_y + 2*mm,
                175*mm, 7,
                max_lines=1
            )

        return section_bottom

    def _draw_additional_sections(self, c, data, start_y):
        """Additional information sections"""
        # Near Miss
        near_miss_height = 12*mm
        near_miss_bottom = start_y - near_miss_height
        c.rect(10*mm, near_miss_bottom, 190*mm, near_miss_height)
        c.setFont("Helvetica", 8)
        c.drawString(12*mm, near_miss_bottom + 8*mm, template.get_section_titles()['near_miss'])
        c.setFont("Helvetica", 7)
        self._draw_wrapped_text(
            c, data.near_miss,
            12*mm, near_miss_bottom + 4*mm,
            185*mm, 7
        )

        # Obstruction
        obstruction_height = 12*mm
        obstruction_bottom = near_miss_bottom - obstruction_height
        c.rect(10*mm, obstruction_bottom, 190*mm, obstruction_height)
        c.setFont("Helvetica", 8)
        c.drawString(12*mm, obstruction_bottom + 8*mm, template.get_section_titles()['obstruction'])
        c.setFont("Helvetica", 7)
        self._draw_wrapped_text(
            c, data.obstruction,
            12*mm, obstruction_bottom + 4*mm,
            185*mm, 7
        )

        # Engineer's Note
        engineers_height = 20*mm
        engineers_bottom = obstruction_bottom - engineers_height
        c.rect(10*mm, engineers_bottom, 190*mm, engineers_height)
        c.setFont("Helvetica", 8)
        c.drawString(12*mm, engineers_bottom + 16*mm, template.get_section_titles()['engineers_note'])
        c.setFont("Helvetica", 7)
        self._draw_wrapped_text(
            c, data.engineers_note,
            12*mm, engineers_bottom + 10*mm,
            185*mm, 7
        )

        return engineers_bottom

    def _draw_signatures_section(self, c, data, start_y):
        """Signatures section"""
        section_height = 30*mm
        section_bottom = start_y - section_height
        col_width = 190*mm / 3

        c.line(10*mm + col_width, section_bottom, 10*mm + col_width, start_y)
        c.line(10*mm + (2*col_width), section_bottom, 10*mm + (2*col_width), start_y)

        # Headers
        headers = template.get_signature_headers()
        c.setFont("Helvetica-Bold", 8)
        for i, header in enumerate(headers):
            c.drawString(12*mm + (i * col_width), start_y - 5*mm, header)

        # Roles
        roles = template.get_signature_roles()
        c.setFont("Helvetica", 7)
        for i, role in enumerate(roles):
            c.drawString(12*mm + (i * col_width), start_y - 9*mm, role)

        # Names
        c.drawString(12*mm, start_y - 15*mm, f"Name: {data.prepared_by}")
        c.drawString(12*mm + col_width, start_y - 15*mm, f"Name: {data.checked_by}")
        c.drawString(12*mm + (2*col_width), start_y - 15*mm, f"Name: {data.approved_by}")

        # Signature lines
        c.drawString(12*mm, start_y - 20*mm, "Sign: ________________")
        c.drawString(12*mm + col_width, start_y - 20*mm, "Sign: ________________")
        c.drawString(12*mm + (2*col_width), start_y - 20*mm, "Sign: ________________")

        return section_bottom

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
            while last_line and c.stringWidth(last_line + "...", "Helvetica", font_size) > max_width:
                last_line = last_line[:-1]
            if last_line:
                c.drawString(x, y - ((max_lines-1) * (font_size + 1)), last_line + "...")
