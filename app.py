import streamlit as st
from google import genai
from PIL import Image
import io
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

# --- TIJORI (SECRETS) SE AUTOMATIC CHABI LENA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("API Key nahi mili! Kripya Streamlit ki settings mein Secrets check karein.")
    st.stop()

client = genai.Client(api_key=API_KEY)

def get_text_from_image(image):
    # STRICT COMMAND: Jo photo mein hai wahi likho, apna dimaag mat lagao
    prompt = """
    Extract the text from this exam paper image EXACTLY as it is written.
    Do NOT answer the questions. Do NOT add any extra text, titles, comments, or explanations.
    Keep the Hindi and English language exactly as it is in the image.
    Format it cleanly line by line exactly like the original paper.
    Do NOT use any HTML tags or markdown. Just pure plain text.
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, image]
    )
    return response.text

def create_docx(all_text):
    doc = Document()
    
    # Page ko 2-Column (Aadha left, Aadha right) design karna
    section = doc.sections[0]
    sectPr = section._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), '720') # Columns ke beech ka space
    
    # Har line ko properly word document mein daalna (Bina khud se kuch jode)
    for line in all_text.split('\n'):
        if line.strip():
            doc.add_paragraph(line.strip())
            
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- UI SETUP ---
st.set_page_config(page_title="Smart Question Paper Maker", page_icon="📝")
st.title("📝 Auto Question Paper Generator")
st.write("Apne phone ya computer se questions ki photos upload karein. Ye App **exactly photo ka text padhkar** aapke liye ek Editable Word File bana dega!")

uploaded_files = st.file_uploader("Upload Question Photos (Multiple allowed)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    if st.button("✨ Generate Question Paper"):
        all_extracted_text = ""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Processing image {i+1} of {len(uploaded_files)}... Kripya intezaar karein.")
                img = Image.open(file)
                extracted_text = get_text_from_image(img)
                all_extracted_text += extracted_text + "\n\n"
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.text("Photos process ho gayi! Ab Word File ban rahi hai...")
            
            docx_data = create_docx(all_extracted_text)
            
            st.success("🎉 Aapka Question Paper Taiyaar Hai! Download karke open karein.")
            
            st.download_button(
                label="📥 Download Word File (.docx)",
                data=docx_data,
                file_name="My_Question_Paper.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        except Exception as e:
            st.error(f"Kuch error aayi: {e}")
