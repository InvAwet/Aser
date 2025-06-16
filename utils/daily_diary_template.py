"""
Template configuration for Daily Diary PDF generation
This module contains the layout and styling configurations for the PDF template
"""

from typing import Dict, List, Any, Tuple
from reportlab.lib.units import mm, inch
from reportlab.lib import colors

class DailyDiaryTemplate:
    """Template configuration for Daily Diary PDF"""
    
    def __init__(self):
        self.setup_dimensions()
        self.setup_colors()
        self.setup_fonts()
        self.setup_sections()
    
    def setup_dimensions(self):
        """Set up page dimensions and margins"""
        self.page_width = 210 * mm  # A4 width
        self.page_height = 297 * mm  # A4 height
        self.margin = 20 * mm
        self.content_width = self.page_width - (2 * self.margin)
        self.content_height = self.page_height - (2 * self.margin)
        
        # Column widths for different sections
        self.header_col_widths = [40*mm, 60*mm, 40*mm, 40*mm]
        self.project_col_widths = [45*mm, 45*mm, 45*mm, 45*mm]
        self.activity_col_widths = [20*mm, 160*mm]
        self.equipment_col_widths = [15*mm, 60*mm, 15*mm, 15*mm, 60*mm, 15*mm]
        self.personnel_col_widths = [15*mm, 60*mm, 15*mm, 15*mm, 60*mm, 15*mm]
        self.signature_col_widths = [60*mm, 60*mm, 60*mm]
    
    def setup_colors(self):
        """Set up color scheme"""
        self.colors = {
            'black': colors.black,
            'white': colors.white,
            'light_grey': colors.lightgrey,
            'dark_grey': colors.darkgrey,
            'header_bg': colors.lightgrey,
            'border': colors.black
        }
    
    def setup_fonts(self):
        """Set up font configurations"""
        self.fonts = {
            'title': {
                'name': 'Helvetica-Bold',
                'size': 12
            },
            'header': {
                'name': 'Helvetica-Bold',
                'size': 10
            },
            'normal': {
                'name': 'Helvetica',
                'size': 9
            },
            'small': {
                'name': 'Helvetica',
                'size': 8
            },
            'company_header': {
                'name': 'Helvetica-Bold',
                'size': 11
            }
        }
    
    def setup_sections(self):
        """Set up section configurations"""
        self.sections = {
            'header': {
                'height': 50*mm,
                'show_border': True,
                'background': self.colors['white']
            },
            'project_info': {
                'height': 20*mm,
                'show_border': True,
                'header_background': self.colors['header_bg']
            },
            'date_weather': {
                'height': 15*mm,
                'show_border': True
            },
            'activities': {
                'height': 40*mm,
                'rows': 6,
                'show_border': True,
                'header_background': self.colors['header_bg']
            },
            'equipment': {
                'height': 35*mm,
                'rows': 5,
                'show_border': True,
                'header_background': self.colors['header_bg']
            },
            'personnel': {
                'height': 70*mm,
                'rows': 14,
                'show_border': True,
                'header_background': self.colors['header_bg']
            },
            'unsafe_acts': {
                'height': 30*mm,
                'rows': 2,
                'show_border': True,
                'header_background': self.colors['header_bg']
            },
            'additional_info': {
                'height': 60*mm,
                'show_border': True
            },
            'signatures': {
                'height': 40*mm,
                'show_border': True
            }
        }
    
    def get_header_data(self) -> List[List[str]]:
        """Get header section data"""
        return [
            ['NICHOLAS O\'DWYER', 'Company Name:', '', 'in Jv with'],
            ['', 'Unit E4, Nutgrove Office Park,', '', ''],
            ['', 'Nutgrove Avenue, Dublin 14', '', ''],
            ['', 'T +353 1 296 9000', '', ''],
            ['', 'F +353 1 296 9001', '', ''],
            ['', 'E dublin@nodwyer.com', '', ''],
            ['', 'W www.nodwyer.com', '', 'MS Consultancy']
        ]
    
    def get_title_data(self) -> List[List[str]]:
        """Get title section data"""
        return [
            ['Title: Daily Diary', 'Document No:', 'Page No. of']
        ]
    
    def get_project_headers(self) -> List[str]:
        """Get project section headers"""
        return ['PROJECT', 'EMPLOYER', 'CONSULTANT', 'CONTRACTOR']
    
    def get_activity_headers(self) -> List[str]:
        """Get activity section headers"""
        return ['sn', 'Description/Topic - Contractor\'s work']
    
    def get_equipment_headers(self) -> List[str]:
        """Get equipment section headers"""
        return ['sn', 'Equipment', 'NO', 'sn', 'Equipment', 'NO']
    
    def get_personnel_headers(self) -> List[str]:
        """Get personnel section headers"""
        return ['sn', 'Personnel', 'No.', 'sn', 'Personnel', 'No.']
    
    def get_unsafe_acts_headers(self) -> List[str]:
        """Get unsafe acts section headers"""
        return ['sn', 'Description of Unsafe Acts']
    
    def get_signature_headers(self) -> List[str]:
        """Get signature section headers"""
        return ['Prepared by', 'Checked by', 'Approved by']
    
    def get_signature_roles(self) -> List[str]:
        """Get signature roles"""
        return [
            'Construction Staff',
            'Consultant Supervision Staff',
            'Consultant Supervision Staff'
        ]
    
    def get_section_titles(self) -> Dict[str, str]:
        """Get section titles"""
        return {
            'activities': '3. Major Activities on progress, Chain age and Location',
            'equipment': '4. Contractor\'s Equipment (dumper truck, excavator, water pump etc.)',
            'personnel': '5. Contractor\'s Personnel (Foreman, laborer, driver etc.)',
            'unsafe_acts': '6. Unsafe Acts / Conditions Observed',
            'near_miss': '7. Near Miss/Accidents/Incidents:',
            'obstruction': '8. Obstruction/Action Plans:',
            'engineers_note': '9. Engineer\'s Note:'
        }
    
    def get_table_style_config(self, section: str) -> Dict[str, Any]:
        """Get table style configuration for a section"""
        base_style = {
            'font_name': self.fonts['normal']['name'],
            'font_size': self.fonts['normal']['size'],
            'border_width': 0.5,
            'border_color': self.colors['border'],
            'alignment': 'LEFT',
            'valignment': 'TOP'
        }
        
        section_styles = {
            'header': {
                'font_name': self.fonts['company_header']['name'],
                'font_size': self.fonts['company_header']['size']
            },
            'title': {
                'font_name': self.fonts['header']['name'],
                'font_size': self.fonts['header']['size'],
                'alignment': 'LEFT'
            },
            'project_header': {
                'font_name': self.fonts['header']['name'],
                'font_size': self.fonts['header']['size'],
                'alignment': 'CENTER',
                'background': self.colors['header_bg']
            },
            'table_header': {
                'font_name': self.fonts['header']['name'],
                'font_size': self.fonts['normal']['size'],
                'alignment': 'CENTER',
                'background': self.colors['header_bg']
            }
        }
        
        if section in section_styles:
            base_style.update(section_styles[section])
        
        return base_style
    
    def get_row_heights(self, section: str) -> List[float]:
        """Get row heights for a section"""
        row_heights = {
            'header': [8*mm] * 7,
            'title': [10*mm],
            'project': [10*mm, 10*mm],
            'date_weather': [10*mm, 10*mm],
            'activities': [8*mm] + [6*mm] * 6,
            'equipment': [8*mm] + [6*mm] * 5,
            'personnel': [8*mm] + [4*mm] * 14,
            'unsafe_acts': [8*mm] + [15*mm] * 2,
            'additional_info': [8*mm, 20*mm],
            'signatures': [8*mm, 8*mm, 12*mm, 12*mm]
        }
        
        return row_heights.get(section, [])
    
    def validate_template_config(self) -> List[str]:
        """Validate template configuration"""
        errors = []
        
        # Check dimensions
        if self.content_width <= 0:
            errors.append("Content width must be positive")
        
        if self.content_height <= 0:
            errors.append("Content height must be positive")
        
        # Check column widths sum
        total_width = sum(self.project_col_widths)
        if abs(total_width - self.content_width) > 1*mm:
            errors.append(f"Project column widths don't match content width: {total_width} vs {self.content_width}")
        
        # Check font configurations
        for font_name, config in self.fonts.items():
            if 'name' not in config or 'size' not in config:
                errors.append(f"Font {font_name} missing required configuration")
            
            if config['size'] <= 0:
                errors.append(f"Font {font_name} size must be positive")
        
        return errors

# Template instance for use in other modules
daily_diary_template = DailyDiaryTemplate()
