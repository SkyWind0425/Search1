import os, os.path, argparse
import pandas as pd
from whoosh import scoring, index
from whoosh.fields import ID, TEXT, Schema
from whoosh.analysis import RegexTokenizer, LowercaseFilter, CharsetFilter
from whoosh.support.charset import accent_map
from queries import norm

#Creating tha analyzer and the schema for the index
analysis = RegexTokenizer(r"\w+") | LowercaseFilter() | CharsetFilter(accent_map)

schema = Schema(
    gutenberg_id=ID(stored=True, unique=True),
    title=TEXT(stored=True, analyzer=analysis),
    author=TEXT(stored=True, analyzer=analysis),
    language=TEXT(stored=True),
    body=TEXT(analyzer=analysis)
)

def main():
    # This part is just mainly for testing smaller subsets to see if the code works.
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="books_10k.csv")
    ap.add_argument("--books", default="books")
    ap.add_argument("--index", default="indexdir")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--procs", type=int, default=1)
    ap.add_argument("-limitmb", type=int, default=256)
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    if args.limit:
        df = df.head(args.limit)
    if not os.path.exists(args.index):
        os.mkdir(args.index)  

    ix = index.create_in(args.index, schema)
    writer = ix.writer(limitmb=args.limitmb, procs=args.procs, multisegment=args.procs > 1)

    missing, bad_encoding, no_markers = [], [], []
    for n, row in enumerate(df.itertuples(index=False), 1):
        try:
            with open(os.path.join(args.books, row.filename), encoding="utf-8", errors="replace") as f:
                raw_text = f.read()
            except FileNotFoundError:
                missing.append(row.filename)
                continue
            if "\ufffd" in raw_text:
                bad_encoding.append(row.filename)
            body, ok = strip_headers(raw_text)
            if not ok:
                no_markers.append(row.filename)
            
            writer.add_document(
                gutenberg_id=str(row.gutenberg_id),
                title=row.title if pd.notna(row.title) else "",
                author=row.author if pd.notna(row.author) else "",
                language=row.language if pd.notna(row.language) else "",
                body=norm(body),
            )

            if n % 500 == 0:
                print(f"Indexed {n} books...") # Just to show progress, since indexing can take a while. Will be commented out
            
            writer.commit()
            print(f"Indexed: {ix.doc_count()} documents. Missing Files: {len(missing)}")
            for label, names in (("Missing", missing), ("Bad Encoding", bad_encoding), ("No Markers", no_markers)):
                if names:
                    print(f"First few {label}: {names[:5]}")

if __name__ == "__main__":
    main()