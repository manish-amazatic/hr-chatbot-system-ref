"""
Generate Comprehensive HR Policy PDFs

Generates PDFs from both original and comprehensive HR policy documents.
Creates a complete, professional HR policy document suite.

Usage:
    python scripts/generate_all_comprehensive_pdfs.py
"""

import sys
from pathlib import Path
import re
import logging
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_pdf_styles():
    """Create custom paragraph styles for PDF"""
    styles = getSampleStyleSheet()

    # Custom title style
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        textColor='#2C3E50',
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    # Custom heading style
    styles.add(ParagraphStyle(
        name='CustomHeading',
        parent=styles['Heading1'],
        fontSize=14,
        textColor='#34495E',
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    ))

    # Custom subheading style
    styles.add(ParagraphStyle(
        name='CustomSubHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor='#34495E',
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    ))

    # Custom body style
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        textColor='#2C3E50',
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    ))

    # Custom metadata style
    styles.add(ParagraphStyle(
        name='CustomMetadata',
        parent=styles['Normal'],
        fontSize=9,
        textColor='gray',
        spaceAfter=10,
        fontName='Helvetica-Oblique',
        alignment=TA_CENTER
    ))

    return styles


def text_to_pdf_elements(content: str, styles):
    """
    Convert markdown-style text to PDF flowable elements

    Args:
        content: Text content with markdown-style formatting
        styles: ReportLab StyleSheet

    Returns:
        List of Paragraph and Spacer elements
    """
    elements = []
    lines = content.strip().split('\n')

    for line in lines:
        line = line.strip()

        if not line:
            elements.append(Spacer(1, 0.1 * inch))
            continue

        # Main title (starts with #)
        if line.startswith('# '):
            title_text = line[2:].strip()
            elements.append(Paragraph(title_text, styles['CustomTitle']))
            elements.append(Spacer(1, 0.2 * inch))

        # Heading (starts with ##)
        elif line.startswith('## '):
            heading_text = line[3:].strip()
            elements.append(Paragraph(heading_text, styles['CustomHeading']))

        # Subheading (starts with ###)
        elif line.startswith('### '):
            subheading_text = line[4:].strip()
            elements.append(Paragraph(subheading_text, styles['CustomSubHeading']))

        # Metadata (starts with ** and ends with **)
        elif line.startswith('**') and line.endswith('**'):
            metadata_text = line[2:-2].strip()
            elements.append(Paragraph(metadata_text, styles['CustomMetadata']))

        # Separator line (---)
        elif line.startswith('---'):
            elements.append(Spacer(1, 0.2 * inch))

        # List item (starts with -)
        elif line.startswith('- '):
            bullet_text = '• ' + line[2:]
            # Handle bold in bullet text
            bullet_text = re.sub(r'\*\*([^\*]+)\*\*', r'<b>\1</b>', bullet_text)
            elements.append(Paragraph(bullet_text, styles['CustomBody']))

        # Regular text
        else:
            # Handle bold (**text**)
            formatted_line = re.sub(r'\*\*([^\*]+)\*\*', r'<b>\1</b>', line)
            elements.append(Paragraph(formatted_line, styles['CustomBody']))

    return elements


def generate_pdf(filename: str, content: str, output_dir: Path) -> Path:
    """
    Generate a single PDF from text content

    Args:
        filename: Original text filename
        content: Policy content
        output_dir: Output directory for PDF

    Returns:
        Path to generated PDF
    """
    try:
        pdf_filename = filename.replace('.txt', '.pdf')
        filepath = output_dir / pdf_filename

        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        # Get styles
        styles = create_pdf_styles()

        # Convert text to elements
        elements = text_to_pdf_elements(content, styles)

        # Build PDF
        doc.build(elements)

        return filepath

    except Exception as e:
        logger.error(f"Error generating PDF for {filename}: {e}")
        raise


def load_policy_file(filepath: Path) -> str:
    """Load policy content from text file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return ""


def generate_all_pdfs():
    """Generate PDFs from all policy documents"""

    # Get script directory
    script_dir = Path(__file__).parent.parent

    # Source directories
    source_dir = script_dir / "docs" / "hr_policies"

    # Output directory
    output_dir = script_dir / "docs" / "hr_policies_pdf"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("Comprehensive HR Policy PDF Generation")
    print("=" * 70)
    print()

    total_size = 0
    pdf_count = 0

    # Process original policies
    if source_dir.exists():
        print(f"Processing original policies from: {source_dir}")
        print()

        for txt_file in sorted(source_dir.glob("*.txt")):
            logger.info(f"Processing: {txt_file.name}")

            content = load_policy_file(txt_file)
            if not content:
                continue

            pdf_path = generate_pdf(txt_file.name, content, output_dir)
            pdf_size = pdf_path.stat().st_size
            total_size += pdf_size
            pdf_count += 1

            print(f"✓ {txt_file.name} → {pdf_path.name}")
            print(f"  Size: {pdf_size / 1024:.1f} KB")
            print()

    print("=" * 70)
    print("✓ PDF Generation Complete!")
    print("=" * 70)
    print(f"\nTotal: {pdf_count} PDF files, {total_size / 1024:.1f} KB")
    print(f"Output directory: {output_dir.absolute()}")
    print()
    print("Next step:")
    print("  python scripts/ingest_all_comprehensive_pdfs.py --drop-existing")
    print()


if __name__ == "__main__":
    try:
        generate_all_pdfs()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
