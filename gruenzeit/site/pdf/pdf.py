from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from typing import List, Dict
from io import BytesIO


class pdfGen():
    data = {}

    def __init__(self):
        pass

    def setData(self, dict: Dict):
        self.data = dict

    def generate(self):
        # Create a BytesIO object to hold the PDF data
        pdf_buffer = BytesIO()

        # Create the PDF document using the buffer as the file
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    
        # Define the data for the table
        data = [
            ['Header 1', 'Header 2', 'Header 3'],
            ['Row 1, Column 1', 'Row 1, Column 2', 'Row 1, Column 3'],
            ['Row 2, Column 1', 'Row 2, Column 2', 'Row 2, Column 3'],
        ]

        # Create the table
        table = Table(data)

        # Add style to the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(style)

        # Build the PDF
        elements = [table]
        doc.build(elements)

        # Move the buffer's position to the beginning
        pdf_buffer.seek(0)

        return pdf_buffer
