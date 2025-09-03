import streamlit as st
import PyPDF2
import google.generativeai as genai
import io

# --- Configuration ---
# Set your Google API Key here.
# For production apps, use st.secrets to manage your API key securely.
# Example: GOOGLE_API_KEY = st.secrets["google_api_key"]
# To run locally, you can set it as an environment variable or directly here.
# IMPORTANT: Do not hardcode your API key in a public repository.
try:
    # Attempt to get the API key from Streamlit secrets
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except (KeyError, AttributeError):
    # Fallback for local development if secrets aren't set
    # You should set this as an environment variable in a real scenario
    GOOGLE_API_KEY = "" # Add your key here for local testing if needed

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    # This block will be executed if the API key is not found
    st.warning("Google API Key not found. Please configure it in your Streamlit secrets to use the AI features.", icon="⚠️")


# --- Gemini API Call Function ---
def analyze_pdf_with_gemini(pdf_text):
    """
    Sends the extracted PDF text to the Gemini API for analysis.

    Args:
        pdf_text (str): The text content extracted from the PDF.

    Returns:
        str: The generated text from the model, or an error message.
    """
    if not GOOGLE_API_KEY:
        # Simulate a response if the API key is not available
        return """
        **Executive Summary:**
        This is a simulated executive summary. The content of the PDF would be concisely summarized here, highlighting the key findings, main arguments, and overall purpose of the document. This section is designed for quick consumption by busy stakeholders.

        ---

        **In-depth Analysis:**
        This is a simulated in-depth analysis. In a real scenario, this section would provide a detailed breakdown of the document's content. It would explore the primary topics, methodologies, and conclusions presented in the PDF. Key points would be elaborated upon, and a critical perspective might be offered on the document's strengths, weaknesses, and implications. For example, it could include:
        - **Main Arguments:** A bulleted list or detailed paragraphs on the core arguments.
        - **Evidence and Data:** Analysis of the data or evidence used to support the claims.
        - **Potential Biases:** Identification of any potential biases or limitations.
        - **Conclusion and Recommendations:** A deeper look at the document's conclusions and any actionable recommendations.
        """

    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
        prompt = f"""
        Based on the following text extracted from a PDF document, please provide a comprehensive analysis. Structure your response into two distinct sections:

        1.  **Executive Summary:** A concise, high-level overview of the document's key points, purpose, and conclusions. This should be easy to understand for someone who has not read the document.

        2.  **In-depth Analysis:** A detailed breakdown of the document. This should include:
            * Identification of the main arguments or topics.
            * An evaluation of the evidence or data presented.
            * A discussion of the document's implications, strengths, and potential weaknesses.
            * Any other critical insights you can derive from the text.

        Here is the document text:
        ---
        {pdf_text}
        ---
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while calling the Gemini API: {e}"

# --- PDF Processing Function ---
def extract_text_from_pdf(uploaded_file):
    """
    Extracts text from an uploaded PDF file.

    Args:
        uploaded_file: The file-like object from Streamlit's file uploader.

    Returns:
        str: The extracted text content of the PDF.
    """
    text = ""
    try:
        # Create a file-like object in memory
        pdf_file_obj = io.BytesIO(uploaded_file.read())
        pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
        for page in pdf_reader.pages:
            text += page.extract_text()
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
    return text


# --- Streamlit App UI ---
st.set_page_config(page_title="PDF Analyzer with Gemini", layout="wide", page_icon="📄")

# Custom CSS for a better look and feel
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
    }
    .st-emotion-cache-16txtl3 {
        padding: 2rem 2rem 2rem;
    }
    .st-emotion-cache-1y4p8pa {
        padding: 2rem;
        background-color: white;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .st-emotion-cache-1v0mbdj > img {
        border-radius: 0.5rem;
    }
    h1, h2, h3 {
        color: #1e3a8a; /* A nice dark blue */
    }
</style>
""", unsafe_allow_html=True)


st.title("📄 PDF Document Analyzer powered by Gemini 2.5 Pro")
st.markdown("Upload one or more PDF files below. The application will extract the text and use Google's Gemini model to generate a summary and a detailed analysis.")

uploaded_files = st.file_uploader(
    "Choose your PDF files",
    type="pdf",
    accept_multiple_files=True,
    help="You can upload multiple PDFs at once. Each will be analyzed separately."
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.write("---")
        st.subheader(f"Analysis for: `{uploaded_file.name}`")

        with st.spinner(f"Reading and analyzing `{uploaded_file.name}`... This may take a moment."):
            # Step 1: Extract text from the PDF
            pdf_text = extract_text_from_pdf(uploaded_file)

            if pdf_text.strip():
                # Step 2: Get analysis from Gemini
                analysis = analyze_pdf_with_gemini(pdf_text)

                # Step 3: Display the results
                st.markdown(analysis)
            else:
                st.warning(f"Could not extract text from `{uploaded_file.name}`. The file might be empty, image-based, or corrupted.")
elif not GOOGLE_API_KEY:
     st.info("Please add your Google API Key to the Streamlit secrets to begin.")
