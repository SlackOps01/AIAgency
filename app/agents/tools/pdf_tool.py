from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import pathlib
from app.core.logging import logger
from datetime import datetime, timezone


root_path = pathlib.Path(__file__).parent.parent.parent.parent

output_path = root_path / "output"
templates_path = root_path / "templates"

# Setup Jinja2 environment
jinja_env = Environment(loader=FileSystemLoader(templates_path))


def write_pdf(title: str, content: str, filename: str):
    """
    Render a legal document PDF using the template.

    Args:
        title (str): Document title (e.g., "Non-Disclosure Agreement").
        content (str): HTML content for the document body (sections, paragraphs, etc.).
        filename (str): Name of the PDF file. Must end with .pdf.

    Returns:
        str: Absolute path to the generated PDF file.

    Raises:
        ValueError: If required fields are empty.
        ValueError: If filename does not end with .pdf.
    """
    logger.info(f"Generating PDF: {filename}")
    date = datetime.now(timezone.utc).strftime("%B %d, %Y")
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")
    
    if not content or not content.strip():
        raise ValueError("Content cannot be empty")

    if not filename.lower().endswith(".pdf"):
        raise ValueError("Filename must end with .pdf")

    # Load and render template
    template = jinja_env.get_template("legal_template.html")
    html_content = template.render(title=title, date=date, content=content)

    safe_filename = pathlib.Path(filename).name
    output_path.mkdir(parents=True, exist_ok=True)

    pdf_path = output_path / safe_filename

    HTML(string=html_content).write_pdf(pdf_path)

    logger.info(f"PDF generated: {pdf_path}")
    return str(pdf_path)