import streamlit as st
import google.generativeai as genai
from PIL import Image
from weasyprint import HTML

# --- API KEY SETUP (Yahan apni key dalein) ---
API_KEY = "Aapki_Gemini_API_Key_Yahan_Dalein" 
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

def get_text_from_image(image):
    prompt = """
    Extract all the questions and multiple-choice options from this exam paper image.
    Format the output strictly as clean HTML. 
    Wrap each question and its options inside a <div class='question'> tag.
    Use <p> tags for the question text and options.
    Keep the Hindi and English language exactly as it is.
    Do NOT add any markdown formatting like ```html. Just give the raw HTML code.
    Make sure the serial numbers are correct.
    """
    response = model.generate_content([prompt, image])
    clean_html = response.text.replace("```html", "").replace("```", "")
    return clean_html

def create_pdf(all_html_content):
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 0.75in;
            }}
            body {{
                font-family: Arial, sans-serif;
                font-size: 14px;
            }}
            .header {{
                text-align: center;
                font-weight: bold;
                font-size: 18px;
                margin-bottom: 20px;
                border-bottom: 2px solid black;
                padding-bottom: 10px;
            }}
            /* 2 Column Design */
            .paper-content {{
                column-count: 2;
                column-gap: 40px;
            }}
            .question {{
                margin-bottom: 20px;
                break-inside: avoid; /* Question ko aadha katne se rokega */
                page-break-inside: avoid;
            }}
            p {{
                margin: 2px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            Geography Test Examination (Auto Generated)
        </div>
        <div class="paper-content">
            {all_html_content}
        </div>
    </body>
    </html>
    """
    
    # HTML ko WeasyPrint ke zariye PDF mein badalna
    pdf_bytes = HTML(string=full_html).write_pdf()
    return pdf_bytes

# --- UI SETUP ---
st.set_page_config(page_title="Smart Question Paper Maker", page_icon="📝")
st.title("📝 Auto Question Paper Generator")
st.write("Apne phone ya computer se questions ki photos upload karein. Ye App automatically padhkar aapke liye ek Print-Ready A4 PDF bana dega!")

uploaded_files = st.file_uploader("Upload Question Photos (Multiple allowed)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    if st.button("✨ Generate Question Paper PDF"):
        all_extracted_html = ""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Processing image {i+1} of {len(uploaded_files)}... Kripya intezaar karein.")
                img = Image.open(file)
                extracted_html = get_text_from_image(img)
                all_extracted_html += extracted_html
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.text("Photos process ho gayi! Ab PDF ban rahi hai...")
            
            pdf_data = create_pdf(all_extracted_html)
            
            st.success("🎉 Aapka Question Paper Taiyaar Hai!")
            
            st.download_button(
                label="📥 Download PDF Paper",
                data=pdf_data,
                file_name="My_Question_Paper.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"Kuch error aayi: {e}")
