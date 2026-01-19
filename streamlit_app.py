import streamlit as st
import requests
import io
from pypdf import PdfReader, PdfWriter

# --------------------
# Page config
# --------------------
st.set_page_config(
    page_title="Cryptext PDF Builder",
    layout="centered",
)

# --------------------
# Simple UI styling
# --------------------
st.markdown(
    """
    <style>
        .main h1 {
            font-size: 3rem;
            margin-bottom: 0.5rem;
        }
        .main p {
            font-size: 1.2rem;
        }
        input {
            font-size: 1.2rem !important;
        }
        button {
            font-size: 1.2rem !important;
            padding: 0.5rem 1.5rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------
# Header
# --------------------
st.title("Cryptext PDF")
st.write("Type a word. Get a PDF.")

# --------------------
# File mappings
# --------------------
FILE_IDS = {
    "m": "1UbRh_26i0BsjxOhIDg0wMbru_QL6yVL5",
    "y": "12mUIM66tN5U4ymH8-yK-OS-CbA18fCoi",
    "dot": "1-xQiqHwACTsAytEfKPxw_WsuFu2iPye-",
    "c": "12DqTloEq_Cu3scGN3ylqSvA4wpgtXW2v",
    "z": "17_aJEGRHeNtjqE-l5rQfWBKBGqk8ethJ",
    "e2": "1KzJsHLWarZAPQId0rdh_5aayVmgDFXPL",
    "e3": "1wbwObcpRZDRdG8qX1ECvol0NCiTkwkq5",
    "r1": "1LCdjcGNnC80WCADNJ-dBZPJzRNJzV18K",
    "r21": "1ojXyOgfGGzE2RrKxu1jJbzG-X7CY6AGH",
    "l7": "11XT-03Am8OaGYBU4EbAc8dUi9jW2R16U",
    "a": "1gHkEiKRz5vF7jH2douD4RxJ1jxyHpOsP",
    "b": "1P_8oZ5AipkJ-nnGgn1wCal9EXvtLukTx",
    "d": "1xjBZpSTokFPzycjO-NTOQ3jya9BubIi1",
    "e": "1KzJsHLWarZAPQId0rdh_5aayVmgDFXPL",
    "o": "1b0w2Yw6rZsoDvPbVv92kiUIVdPDnKYTh",
}

TOKEN_MAP = {
    "e": "e2",
    "l": "l7",
    "r": "r1",
}

# --------------------
# Input
# --------------------
user_text = st.text_input(
    label="",
    placeholder="e.g. Red.Ear",
    value="Red.Ear",
)

# --------------------
# One-step action
# --------------------
if st.button("Create PDF"):
    text = user_text.strip().lower()

    if not text:
        st.warning("Enter something first.")
    else:
        tokens = []

        for i, ch in enumerate(text):
            if ch == ".":
                tokens.append("dot")
                continue

            is_word_start = i == 0 or text[i - 1] == "."

            if ch == "e" and is_word_start:
                tokens.append("e3")
            elif ch == "r" and is_word_start:
                tokens.append("r21")
            else:
                tokens.append(ch)

        writer = PdfWriter()

        for token in reversed(tokens):
            key = TOKEN_MAP.get(token, token)
            file_id = FILE_IDS.get(key)

            if not file_id:
                continue

            data = requests.get(
                f"https://drive.google.com/uc?export=download&id={file_id}"
            ).content

            reader = PdfReader(io.BytesIO(data))
            writer.add_page(reader.pages[0])

        pdf_bytes = io.BytesIO()
        writer.write(pdf_bytes)
        pdf_bytes.seek(0)

        # Human-readable filename
        safe_name = (
            text.replace(".", "_")
            .replace(" ", "_")
        )
        filename = f"cryptext_{safe_name}.pdf"

        st.download_button(
            label="Download PDF",
            data=pdf_bytes.getvalue(),
            file_name=filename,
            mime="application/pdf",
        )
