import streamlit as st
import requests
import io
from pypdf import PdfReader, PdfWriter

st.set_page_config(page_title="Cryptext PDF Builder", layout="centered")

st.title("Cryptext PDF Builder")
st.write("Enter word(s) and receive a generated Cryptext PDF.")

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

TOKEN_MAP = {"e": "e2", "l": "l7", "r": "r1"}

force_word = st.text_input("Enter your word(s)", value="Red.Ear")

if st.button("Generate PDF"):
    text = force_word.lower()
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

        data = requests.get(
            f"https://drive.google.com/uc?export=download&id={file_id}"
        ).content

        reader = PdfReader(io.BytesIO(data))
        writer.add_page(reader.pages[0])

    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    st.download_button(
        "Download PDF",
        pdf_bytes.getvalue(),
        file_name=f"combined_{''.join(tokens)}.pdf",
        mime="application/pdf",
    )
