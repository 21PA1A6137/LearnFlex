from langchain.schema import HumanMessage, AIMessage
from fpdf import FPDF
from datetime import datetime
import streamlit as st
import re
import time
import os

class CustomPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", size=8)
        self.cell(0, 10, f"Page {self.page_no()} - Faculty: {self.faculty_name}", align="C")

    def header(self):
        self.set_font("DejaVu", style="B", size=10)
        self.cell(0, 10, f"Unit {self.unit_number}: {self.subject}", align="R", ln=True)

    def watermark(self):
        self.set_font("DejaVu", style="I", size=50)
        self.set_text_color(200, 200, 200)
        self.rotate(45, x=self.w / 2, y=self.h / 2)
        self.text(x=self.w / 2 - 50, y=self.h / 2, txt="LearnFlex Chat History")
        self.rotate(0)

    def add_toc(self, toc):
        """Add Table of Contents (TOC) page."""
        self.add_page()
        self.set_font("DejaVu", style="B", size=14)
        self.cell(0, 10, "Table of Contents", ln=True, align="C")
        self.ln(5)

        self.set_font("DejaVu", size=12)
        for idx, question in enumerate(toc, start=1):
            self.cell(0, 10, f"{idx}. {question}", ln=True)
        self.ln(10)


def render_styled_text(pdf, content):
    """Render text with support for **bold** and *italic* markers."""
    bold_pattern = r"\*\*(.*?)\*\*"
    italic_pattern = r"\*(.*?)\*"
    pos = 0

    while pos < len(content):
        # Find matches for bold and italic markers
        bold_match = re.search(bold_pattern, content[pos:])
        italic_match = re.search(italic_pattern, content[pos:])

        # Determine the first match (if any)
        next_match = None
        if bold_match and italic_match:
            next_match = bold_match if bold_match.start() < italic_match.start() else italic_match
        elif bold_match:
            next_match = bold_match
        elif italic_match:
            next_match = italic_match

        if next_match:
            start = pos + next_match.start()
            end = pos + next_match.end()

            # Add text before the match
            pdf.set_font("DejaVu", size=12)
            pdf.multi_cell(0, 10, content[pos:start],border=1, fill=True)

            # Add styled text (bold or italic)
            style = "B" if next_match.re.pattern == bold_pattern else "I"
            pdf.set_font("DejaVu", style=style, size=12)
            pdf.multi_cell(0, 10, next_match.group(1),border=1, fill=True)

            # Move position past the match
            pos = end
        else:
            # No more matches; add the remaining text
            pdf.set_font("DejaVu", size=12)
            pdf.multi_cell(0, 10, content[pos:])
            break


def generate_pdf(history, subject, unit_number, faculty_name, pdf_name, summary):
    """Generate a styled PDF from chat history."""
    pdf = CustomPDF()

    # Assign dynamic properties for header and footer
    pdf.subject = subject or "General Subject"
    pdf.unit_number = unit_number or "1"
    pdf.faculty_name = faculty_name or "Unknown Faculty"

    font_path = os.path.join(os.path.dirname(__file__), 'dejavu-fonts-ttf-2.37', 'ttf', 'DejaVuSans.ttf')
    font_path_bold = os.path.join(os.path.dirname(__file__), 'dejavu-fonts-ttf-2.37', 'ttf', 'DejaVuSans-Bold.ttf')
    font_path_italic = os.path.join(os.path.dirname(__file__), 'dejavu-fonts-ttf-2.37', 'ttf', 'DejaVuSans-Oblique.ttf')
    # Add fonts
    pdf.add_font("DejaVu", "", font_path, uni=True)  # Regular
    pdf.add_font("DejaVu", "B", font_path_bold, uni=True)  # Bold
    pdf.add_font("DejaVu", "I",font_path_italic, uni=True)

    # Add Table of Contents
    toc = [message.content[:50] + "..." for message in history if isinstance(message, HumanMessage)]
    pdf.add_toc(toc)

    # Add Chat History
    pdf.add_page()
    pdf.set_font("DejaVu", size=12)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)

    # Process Chat History
    progress_bar = st.sidebar.progress(0)
    for idx, message in enumerate(history, start=1):
        progress_bar.progress(int((idx / len(history)) * 100))

        if isinstance(message, HumanMessage):  # User's Question
            pdf.set_font("DejaVu", style="B", size=12)
            pdf.set_text_color(0, 0, 255)  # Blue color for the question
            pdf.multi_cell(0, 10, f"Q{idx}: {message.content}", border=1)
            pdf.ln(2)
        elif isinstance(message, AIMessage):  # AI's Answer
            pdf.set_font("DejaVu", size=12)
            pdf.set_text_color(0, 0, 0)  # Black color for the answer
            render_styled_text(pdf, f"Ans: {message.content}")
            pdf.ln(5)

        time.sleep(0.1)

    # Add Watermark to All Pages
    for page in range(1, pdf.page_no() + 1):
        pdf.page = page
        pdf.watermark()

    # Save PDF
    pdf_output_path = f"{pdf_name}.pdf" if pdf_name else f"{summary}.pdf"
    pdf.output(pdf_output_path)

    return pdf_output_path
