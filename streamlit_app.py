import io
import re
import requests
import streamlit as st
from pypdf import PdfReader, PdfWriter

st.set_page_config(page_title="Cryptext PDF", layout="centered")

# --------------------
# Assets
# --------------------
FILE_IDS = {
    "m": "1UbRh_26i0BsjxOhIDg0wMbru_QL6yVL5",
    "y": "12mUIM66tN5U4ymH8-yK-OS-CbA18fCoi",
    "dot": "1-xQiqHwACTsAytEfKPxw_WsuFu2iPye-",
    "c": "12DqTloEq_Cu3scGN3ylqSvA4wpgtXW2v",
    "z": "17_aJEGRHeNtjqE-l5rQfWBKBGqk8ethJ",
    "e2": "1KzJsHLWarZAPQId0rdh_5aayVmgDFXPL",
    "e3": "1wbwObcpRZDRdG8qX1ECvol0NCiTkwkq5",
    "h": "1TjFYmuFr8nx5peV5da1i_pMMxl_aKNFW",
    "v": "1UmpSNzkXWQBlSEOdNfR4G0f_GLXnNSM4",
    "x": "1VWEQIOcnWk7DxkITjD--swvAQkjVcy6J",
    "w": "1oiKE0mWM6QtE3d26SzOFDpop7Yue6iNJ",
    "g": "1tmvojND3Uu9lR-RtWkej1DE1p2YtJRKE",
    "f": "1u7oTKGqkjSpU85rgNNU4N34ia6b7QJuQ",
    "d": "1xjBZpSTokFPzycjO-NTOQ3jya9BubIi1",
    "q": "11O59O28n-IfDzAzMRefTctJhQv0Q-FAZ",
    "l7": "11XT-03Am8OaGYBU4EbAc8dUi9jW2R16U",
    "s": "1ApxQ_Z4MKfQ6nkJKVHV6hop6CQLDuzLf",
    "j": "1CwsMsVq-QhLzVOBhHtAX2ubhL4NsmdeS",
    "l1": "1D_uS7hoPNOvGzkFLd1iopptCBzAVfYr9",
    "r1": "1LCdjcGNnC80WCADNJ-dBZPJzRNJzV18K",
    "r21": "1ojXyOgfGGzE2RrKxu1jJbzG-X7CY6AGH",
    "b": "1P_8oZ5AipkJ-nnGgn1wCal9EXvtLukTx",
    "u": "1X2xG7idLYDjEGddhgB6XpzfGTZqyCcOw",
    "n": "1X6izojDmqdBGNOQP10vJqryXACwuqisH",
    "i": "1ZVW9tLujdKUsST-Z4bY14lQGXEZ00Mag",
    "o": "1b0w2Yw6rZsoDvPbVv92kiUIVdPDnKYTh",
    "p": "1wWYD57qb6-Z5e2cl9PowS2wtPdH3MhDc",
    "a": "1gHkEiKRz5vF7jH2douD4RxJ1jxyHpOsP",
    "t": "1p4dU0y3ymbkPxXuSAVkjGAp7J_vugw_k",
    "k": "1tPgM_KI6k1OVQ65neDhoM-o_eEHgpEQL",
}
TOKEN_MAP = {"e": "e2", "l": "l7", "r": "r1"}

# --------------------
# UI styling
# --------------------
st.markdown(
    """
    <style>
        .main h1 { font-size: 3rem; margin-bottom: 0.25rem; }
        .subtle { font-size: 1.15rem; opacity: 0.85; margin-bottom: 0.75rem; }
        .examples { font-size: 1.05rem; opacity: 0.75; margin-bottom: 1.5rem; }
        input { font-size: 1.25rem !important; }
        button { font-size: 1.25rem !important; padding: 0.6rem 2rem !important; }
        .hint { font-size: 0.95rem; opacity: 0.7; margin-top: 0.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Cryptext PDF")
st.markdown("<div class='subtle'><b>Separate words with dots</b> (spaces also work)</div>", unsafe_allow_html=True)
st.markdown(
    """
    <div class='examples'>
        <div><code>red</code></div>
        <div><code>red.ear</code></div>
        <div><code>hello moto</code> <span class='hint'>(same as <code>hello.moto</code>)</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------
# Helpers
# --------------------
def normalize_input(s: str) -> str:
    s = s.strip().lower()
    # spaces become dots (friendlier)
    s = re.sub(r"\s+", ".", s)
    # keep only letters and dots
    s = re.sub(r"[^a-z.]", "", s)
    # collapse multiple dots
    s = re.sub(r"\.+", ".", s)
    # trim leading/trailing dots
    return s.strip(".")


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
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
    return tokens


def find_unsupported(tokens: list[str]) -> list[str]:
    missing = set()
    for token in tokens:
        key = TOKEN_MAP.get(token, token)
        if key not in FILE_IDS:
            # show the "human" character when possible
            if token == "dot":
                missing.add(".")
            elif token in ("e3", "e2"):
                missing.add("e")
            elif token in ("r21", "r1"):
                missing.add("r")
            elif token == "l7":
                missing.add("l")
            else:
                missing.add(str(token))
    return sorted(missing)


@st.cache_data(show_spinner=False)
def fetch_pdf_first_page_bytes(file_id: str) -> bytes:
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.content


@st.cache_data(show_spinner=True)
def build_pdf_bytes(tokens: list[str]) -> bytes:
    writer = PdfWriter()
    for token in reversed(tokens):
        key = TOKEN_MAP.get(token, token)
        file_id = FILE_IDS[key]  # safe: only call when validated
        data = fetch_pdf_first_page_bytes(file_id)
        reader = PdfReader(io.BytesIO(data))
        writer.add_page(reader.pages[0])

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


# --------------------
# Input
# --------------------
raw = st.text_input("", placeholder="Type here… (e.g. Red.Ear)", value="Red.Ear")
normalized = normalize_input(raw)

if raw.strip() and normalized != raw.strip().lower():
    st.caption(f"Using: `{normalized}`")

# Validate
tokens = tokenize(normalized) if normalized else []
unsupported = find_unsupported(tokens) if tokens else []

if unsupported:
    st.error(
        "Unsupported character(s): "
        + ", ".join(f"`{c}`" for c in unsupported)
        + "\n\nAdd their PDF IDs to `FILE_IDS` (or remove them from the input)."
    )

# Single-click experience:
# - user clicks ONE button (download button)
# - generation happens behind it (cached), then download triggers immediately
disabled = (not normalized) or bool(unsupported)
filename = f"cryptext_{normalized.replace('.', '_')}.pdf" if normalized else "cryptext.pdf"

data_bytes = b""
if not disabled:
    # Precompute so the click immediately downloads.
    # Cached, so it won't refetch endlessly once built.
    data_bytes = build_pdf_bytes(tokens)

st.download_button(
    label="Generate & Download PDF",
    data=data_bytes,
    file_name=filename,
    mime="application/pdf",
    disabled=disabled,
)
