from flask import Flask, send_file, request, jsonify
from fpdf import FPDF
from datetime import datetime

app = Flask(__name__)

class CustomPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", size=8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def header(self):
        self.set_font("DejaVu", style="B", size=10)
        self.cell(0, 10, "Chat History", align="R", ln=True)

def generate_pdf(history, subject, unit_number, faculty_name):
    pdf = CustomPDF()

    # Assign dynamic properties for header and footer
    pdf.subject = subject
    pdf.unit_number = unit_number
    pdf.faculty_name = faculty_name

    # Add Unicode-compatible font (DejaVu)
    pdf.add_font("DejaVu", "", "models\\DejaVuSans.ttf", uni=True)  # Regular
    pdf.add_page()
    pdf.set_font("DejaVu", size=12)

    # Add Chat History
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)

    for idx, message in enumerate(history, start=1):
        if "question" in message:  # Example key for User's Question
            pdf.set_font("DejaVu", style="B", size=12)
            pdf.set_text_color(0, 0, 255)  # Blue for question
            pdf.multi_cell(0, 10, f"Q{idx}: {message['question']}")
            pdf.ln(2)
        if "answer" in message:  # Example key for AI's Answer
            pdf.set_font("DejaVu", size=12)
            pdf.set_text_color(0, 0, 0)  # Black for answer
            pdf.multi_cell(0, 10, f"Ans: {message['answer']}", border=1)
            pdf.ln(5)

    pdf_output_path = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(pdf_output_path)

    return pdf_output_path


@app.route('/download', methods=['POST'])
def download_pdf():
    # Sample history data from a POST request
    data = request.json
    history = data.get("history", [])
    subject = data.get("subject", "Unknown Subject")
    unit_number = data.get("unit_number", "1")
    faculty_name = data.get("faculty_name", "Unknown Faculty")

    # Generate PDF
    pdf_path = generate_pdf(history, subject, unit_number, faculty_name)

    # Send the PDF as a downloadable file
    return send_file(pdf_path, as_attachment=True, download_name="ChatHistory.pdf")


if __name__ == '__main__':
    app.run(debug=True)







# js code


# fetch('/download', {
#     method: 'POST',
#     headers: {
#         'Content-Type': 'application/json',
#     },
#     body: JSON.stringify({
#         history: [
#             { question: "What is AI?", answer: "AI stands for Artificial Intelligence." },
#             { question: "What is ML?", answer: "ML stands for Machine Learning." }
#         ],
#         subject: "Artificial Intelligence",
#         unit_number: 3,
#         faculty_name: "Dr. John Doe"
#     })
# })
# .then(response => response.blob())
# .then(blob => {
#     const url = window.URL.createObjectURL(blob);
#     const a = document.createElement('a');
#     a.style.display = 'none';
#     a.href = url;
#     a.download = 'ChatHistory.pdf';  // Default file name
#     document.body.appendChild(a);
#     a.click();
#     window.URL.revokeObjectURL(url);
# })
# .catch(err => console.error('Error generating PDF:', err));
