from fpdf import FPDF

def create_pdf(content: str, output_filename: str = "output.pdf"):
    """
    Creates a PDF file based on a string passed as a parameter.
    
    Args:
        content (str): The text content to be added to the PDF.
        output_filename (str): The name of the output PDF file (default is 'output.pdf').
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add content to the PDF
    pdf.multi_cell(0, 10, content)

    # Save the PDF to a file
    pdf.output(output_filename)
    print(f"PDF created successfully and saved as '{output_filename}'.")