"""
Backend Module: Refrigerator Catalog Management & Vector Store
Handles PDF creation, data processing, and vector store initialization
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# ====================
# REFRIGERATOR DATA
# ====================

REFRIGERATOR_DATA = [
    {
        "name": "FrostFree Compact 150",
        "model": "FF-150-2024",
        "category": "Compact",
        "price": "$279",
        "capacity": "150L",
        "features": "Energy Star rated, reversible door, adjustable shelves, crisper drawer",
        "dimensions": "54cm W x 60cm D x 85cm H",
        "warranty": "1 year comprehensive",
        "color_options": "White, Silver",
        "stock": "In Stock",
        "ideal_for": "Students, small apartments, dorm rooms"
    },
    {
        "name": "ChillMaster 250L Single Door",
        "model": "CM-250-SD",
        "category": "Single Door",
        "price": "$399",
        "capacity": "250L",
        "features": "Direct cool, toughened glass shelves, large vegetable box, stabilizer-free operation",
        "dimensions": "60cm W x 65cm D x 120cm H",
        "warranty": "2 years on product, 5 years on compressor",
        "color_options": "Red, Blue, Silver, Black",
        "stock": "In Stock",
        "ideal_for": "Small families (2-3 members), bachelor pads"
    },
    {
        "name": "CoolPro 340L Double Door",
        "model": "CP-340-DD",
        "category": "Double Door",
        "price": "$649",
        "capacity": "340L (240L fridge + 100L freezer)",
        "features": "Frost-free, inverter compressor, anti-bacterial gasket, LED interior lighting",
        "dimensions": "65cm W x 70cm D x 165cm H",
        "warranty": "3 years comprehensive, 10 years on compressor",
        "color_options": "Stainless Steel, Black, White Pearl",
        "stock": "In Stock",
        "ideal_for": "Medium families (3-4 members)"
    },
    {
        "name": "IceCool 450L French Door",
        "model": "IC-450-FD",
        "category": "French Door",
        "price": "$999",
        "capacity": "450L (320L fridge + 130L freezer)",
        "features": "Multi-airflow cooling, humidity-controlled crispers, ice maker, touch control panel",
        "dimensions": "80cm W x 75cm D x 175cm H",
        "warranty": "5 years comprehensive warranty",
        "color_options": "Platinum Silver, Charcoal Black",
        "stock": "In Stock",
        "ideal_for": "Large families (4-6 members), food enthusiasts"
    },
    {
        "name": "Arctic 550L Side-by-Side",
        "model": "AR-550-SBS",
        "category": "Side-by-Side",
        "price": "$1,299",
        "capacity": "550L (350L fridge + 200L freezer)",
        "features": "Water & ice dispenser, smart diagnostics, door alarm, express freeze function",
        "dimensions": "90cm W x 75cm D x 180cm H",
        "warranty": "5 years comprehensive, 10 years on linear compressor",
        "color_options": "Stainless Steel, Black Stainless",
        "stock": "In Stock",
        "ideal_for": "Large families (5+ members), entertaining frequently"
    },
    {
        "name": "SmartChill 600L IoT Enabled",
        "model": "SC-600-IOT",
        "category": "Smart Refrigerator",
        "price": "$1,599",
        "capacity": "600L (420L fridge + 180L freezer)",
        "features": "WiFi connectivity, internal camera, voice control, auto-reorder, energy monitoring app",
        "dimensions": "92cm W x 78cm D x 185cm H",
        "warranty": "7 years comprehensive warranty",
        "color_options": "Mirror Finish, Matte Black",
        "stock": "In Stock",
        "ideal_for": "Tech-savvy families, smart home integration"
    },
    {
        "name": "EcoFreeze 400L Energy Saver",
        "model": "EF-400-ES",
        "category": "Energy Efficient",
        "price": "$849",
        "capacity": "400L (280L fridge + 120L freezer)",
        "features": "5-star energy rating, solar-compatible inverter, eco mode, low noise operation (38dB)",
        "dimensions": "70cm W x 72cm D x 170cm H",
        "warranty": "4 years comprehensive",
        "color_options": "Nature Green, Ocean Blue, Cloud White",
        "stock": "In Stock",
        "ideal_for": "Eco-conscious families, energy bill savers"
    },
    {
        "name": "MiniChill 90L Bar Refrigerator",
        "model": "MC-90-BR",
        "category": "Mini/Bar",
        "price": "$199",
        "capacity": "90L",
        "features": "Compact design, glass door option, adjustable thermostat, reversible door",
        "dimensions": "48cm W x 52cm D x 75cm H",
        "warranty": "1 year",
        "color_options": "Black, Stainless Steel",
        "stock": "In Stock",
        "ideal_for": "Home bars, offices, guest rooms, beverages"
    },
    {
        "name": "CommercialPro 800L",
        "model": "CP-800-COM",
        "category": "Commercial",
        "price": "$2,299",
        "capacity": "800L",
        "features": "Heavy-duty compressor, stainless steel interior, lockable doors, temperature display",
        "dimensions": "120cm W x 80cm D x 200cm H",
        "warranty": "3 years commercial warranty",
        "color_options": "Stainless Steel",
        "stock": "Made to Order (2-3 weeks)",
        "ideal_for": "Restaurants, cafes, commercial kitchens"
    },
    {
        "name": "UltraFreeze 700L Premium",
        "model": "UF-700-PRM",
        "category": "Premium",
        "price": "$1,899",
        "capacity": "700L (480L fridge + 220L freezer)",
        "features": "Dual cooling system, convertible freezer, wine rack, sabbath mode, child lock",
        "dimensions": "95cm W x 80cm D x 190cm H",
        "warranty": "10 years comprehensive warranty",
        "color_options": "Champagne Gold, Graphite Grey",
        "stock": "Limited Stock",
        "ideal_for": "Luxury homes, large families, premium lifestyle"
    }
]


# ====================
# PDF CREATION
# ====================

def create_refrigerator_catalog(filename="refrigerator_catalog.pdf"):
    """Create a comprehensive refrigerator product catalog PDF"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph("<b>Premium Refrigerator Collection 2024</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Introduction
    intro = Paragraph(
        "Welcome to our comprehensive refrigerator lineup. "
        "Find the perfect cooling solution for your home with our range of "
        "energy-efficient, feature-rich refrigerators.",
        styles['Normal']
    )
    story.append(intro)
    story.append(Spacer(1, 30))
    
    # Add each refrigerator
    for idx, ref in enumerate(REFRIGERATOR_DATA, 1):
        product_title = Paragraph(f"<b>{idx}. {ref['name']}</b>", styles['Heading2'])
        story.append(product_title)
        
        model_info = Paragraph(
            f"<i>Model: {ref['model']} | Category: {ref['category']}</i>",
            styles['Normal']
        )
        story.append(model_info)
        story.append(Spacer(1, 10))
        
        details = [
            ["Price:", ref['price']],
            ["Capacity:", ref['capacity']],
            ["Key Features:", ref['features']],
            ["Dimensions:", ref['dimensions']],
            ["Warranty:", ref['warranty']],
            ["Available Colors:", ref['color_options']],
            ["Availability:", ref['stock']],
            ["Ideal For:", ref['ideal_for']]
        ]
        
        t = Table(details, colWidths=[120, 380])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(t)
        story.append(Spacer(1, 25))
    
    # Footer
    story.append(Spacer(1, 20))
    footer = Paragraph(
        "<b>Contact Us:</b> For any queries, reach us at sales@cooltech.com | "
        "Customer Support: 1-800-COOL-123 | Visit: www.cooltech.com",
        styles['Normal']
    )
    story.append(footer)
    
    doc.build(story)
    print(f"✓ Refrigerator catalog created: {filename}")
    return True


# ====================
# PDF PROCESSING
# ====================

def load_pdf_content(pdf_path):
    """Extract text from PDF"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def create_vector_store(pdf_path):
    """Create FAISS vector store from PDF content"""
    text = load_pdf_content(pdf_path)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    vector_store = FAISS.from_texts(chunks, embeddings)
    return vector_store


# ====================
# UTILITY FUNCTIONS
# ====================

def ensure_catalog_exists(pdf_path="refrigerator_catalog.pdf"):
    """Ensure the catalog PDF exists, create it if not"""
    if not os.path.exists(pdf_path):
        print(f"📄 Creating refrigerator catalog: {pdf_path}")
        create_refrigerator_catalog(pdf_path)
    return pdf_path


def get_catalog_stats():
    """Return statistics about the refrigerator catalog"""
    return {
        "total_products": len(REFRIGERATOR_DATA),
        "categories": list(set(ref["category"] for ref in REFRIGERATOR_DATA)),
        "price_range": {
            "min": "$199",
            "max": "$2,299"
        },
        "capacity_range": {
            "min": "90L",
            "max": "800L"
        }
    }