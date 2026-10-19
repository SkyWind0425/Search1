import os, argparse
import pandas as pd
from whoosh import scoring, index
from whoosh.query import Or, Phrase, Term
from queries import strip_headers, QUERIES_LIST, norm

FIELD_WEIGHTS = {
    "title": 2.8,
    "author": 2.5,
    "body": 1.0
}
PHRASE_BOOST = {
    "title": 5.0,
    "author": 5.0
}
PRF_DOCS, PRF_TERMS = 5, 30