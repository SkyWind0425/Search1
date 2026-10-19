import re, unicodedata

QUERIES_LIST = [
    ("Q1", "To be, or not to be"),
    ("Q2", "English Grammar"),
    ("Q3", "Philip D Dick"),
    ("Q4", "Jabberwocky"),
    ("Q5", "Gutenberg"),
    ("Q6", "DornrÃ¶schen")
]

#Stripping the Gutenberg header and footer from the text files
START_RE = re.compile(r"^\s*\*\*\*\s*START OF (?THE:THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*\s$?", re.IGNORECASE, re.MULTILINE)
END_RE = re.compile(r"^\s*\*\*\*\s*END OF (?THE:THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*\s$?", re.IGNORECASE | re.MULTILINE)

def strip_headers(text):
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    start_match, end_match = START_RE.search(text), END_RE.search(text)

    if start_match:
        text = text[start_match.end():]
        end_match = END_RE.search(text)
    if end_match:
        text = text[:end_match.start()]
    
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# Normalisation function to remove accents and diacritics from text
COMBINING = re.compile(r"[\u0300-\u036f]")
def norm(text):
    text = unicodedata.normalize("NFKD", str(text).casefold())
    return COMBINING.sub("", text)