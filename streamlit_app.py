import streamlit as st
import requests
import io
import tempfile
from pypdf import PdfReader, PdfWriter

st.set_page_config(
    page_title="Cryptext PDF Builder",
    layout="centered"
)

st.title("Cryptext PDF Builder")
st.write("Enter word(s) and receive a generated Cryptext PDF.")

# ===============================
# Cryptext CDN
# ===============================
FILE_IDS = {
    "m": "1UbRh_26i0BsjxOhIDg0wMbru_QL6yVL5",
    "y": "12mUIM66tN5U4ymH8-yK-OS-CbA18fCoi",
    "dot": "1-xQiqHwACTsAytEfKPxw_WsuFu2iPye-",
    "c": "12DqTloEq_Cu3scGN3ylqSvA4wpgtXW2v",
    "z": "17_aJEGRHeNtjqE-l5rQfWBKBGqk8ethJ",
    "e2": "1KzJsHLWarZAPQId0rdh_5aayVmgDFXPL",
    "h": "1TjFYmuFr8nx5peV5da1i_pMMxl_aKNFW",
    "v": "1UmpSNzkXWQBlSEOdNfR4G0f_GLXnNSM4",
    "x": "1VWEQIOcnWk7DxkITjD--swvAQkjVcy6J",
    "w": "1oiKE0mWM6QtE3d26SzOFDpop7Yue6iNJ",
    "g": "1tmvojND3Uu9lR-RtWkej1DE1p2YtJRKE",
    "f": "1u7oTKGqkjSpU85rgNNU4N34ia6b7QJuQ",
    "e3": "1wbwObcpRZDRdG8qX1ECvol0NCiTkwkq5",
    "d": "1xjBZpSTokFPzycjO-NTOQ3jya9BubIi1",
    "q": "11O59O28n-IfDzAzMRefTctJhQv0Q-FAZ",
    "l7": "11XT-03Am8OaGYBU4EbAc8dUi9jW2R16U",
    "s": "1ApxQ_Z4MKfQ6nkJKVHV6hop6CQLDuzLf",
    "j": "1CwsMsVq-QhLzVOBhHtAX2ubhL4NsmdeS",
    "l1": "1D_uS7hoPNOvGzkFLd1iopptCBzAVfYr9",
    "r1": "1LCdjcGNnC80WCADNJ-dBZPJzRNJzV18K",
    "b": "1P_8oZ5AipkJ-nnGgn1wCal9EXvtLukTx",
    "u": "1X2xG7idLYDjEGddhgB6XpzfGTZqyCcOw",
    "n": "1X6izojDmqdBGNOQP10vJqryXACwuqisH",
    "i": "1ZVW9tLujdKUsST-Z4bY14lQGXEZ00Mag",
    "o": "1b0w2Yw6rZsoDvPbVv92kiUIVdPDnKYTh",
    "p": "1bRFJWuJaUAXCuFTZrv-oX3pFJYfIWk1l",
    "a": "1gHkEiKRz5vF7jH2douD4RxJ1jxyHpOsP",
    "r21": "1ojXyOgfGGzE2RrKxu1jJbzG-X7CY6AGH",
    "t": "1p4dU0y3ymbkPxXuSAVkjGAp7J_vugw_k",
    "k": "1tPgM_KI6k1OVQ65neDhoM-o_eEHgpEQL",
}

TOKEN_MAP = {
    "e": "e2",
    "l": "l7",
    "r": "r1",
}

# ===============================
# UI
# ===============================
force_word = st.text_input(
    "Enter your word(s)",
    value="several.example.words"
)

if st.button("Generate PDF"):
    if not force_word.strip():
        st.error("Please enter a word.")
        st.stop()

    with st.spinner("Building PDF..."):
        text = force_word.lower()
        tokens = []

        # Context-aware tokenization
        for i, ch in enumerate(text):
            if ch == ".":
                tokens.append("dot")
                continue

            is_word_start = (i == 0) or (text[i - 1] == ".")

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
                st.error(f"No file mapped for token: {token}")
                st.stop()

            url = f"https://drive.google.com/uc?export=download&id={file_id}"
            response = requests.get(url)
            response.raise_for_status()

            reader = PdfReader(io.BytesIO(response.content))
            writer.add_page(reader.pages[0])

        pdf_bytes = io.BytesIO()
        writer.write(pdf_bytes)
        pdf_bytes.seek(0)

        # Write to temp file for reliable preview
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes.getvalue())
            tmp_path = tmp.name

        st.markdown("### Preview")
        st.components.v1.iframe(
            src=tmp_path,
            width=700,
            height=900
        )

        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=f"combined_{''.join(tokens)}.pdf",
            mime="application/pdf"
        )
