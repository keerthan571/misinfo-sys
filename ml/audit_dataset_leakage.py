
import pandas as pd

DATA_PATH = (
    r"C:\Users\Keerthan\Downloads"
    r"\social-media-post-performance-forecasting"
    r"\archive\train.csv"
)

df = pd.read_csv(DATA_PATH)

df["platform"] = df["platform"].str.lower()
df = df[df["platform"].isin(["facebook", "instagram"])].copy()

df["date_posted"] = pd.to_datetime(
    df["date_posted"], errors="coerce", utc=True
)

df["caption"] = df["caption"].fillna("").astype(str)
df["likes"] = pd.to_numeric(df["likes"], errors="coerce")
df["comments"] = pd.to_numeric(df["comments"], errors="coerce")

print("=" * 65)
print("DATASET DUPLICATE AND LEAKAGE AUDIT")
print("=" * 65)

print("\n1. BASIC COUNTS")
print("Rows:", len(df))
print("Unique page IDs:", df["page_id"].nunique())
print("Exact duplicate rows:", int(df.duplicated().sum()))

# --------------------------------------------------
# 2. DUPLICATE CAPTIONS
# --------------------------------------------------

print("\n2. CAPTION DUPLICATES")

caption_counts = (
    df[df["caption"].str.strip().ne("")]
    .groupby(["platform", "caption"], dropna=False)
    .size()
)

repeated_captions = caption_counts[caption_counts > 1]

print("Repeated platform-caption groups:", len(repeated_captions))
print(
    "Rows belonging to repeated groups:",
    int(repeated_captions.sum())
)

print("\nTop 10 repeated captions:")
print(
    repeated_captions.sort_values(ascending=False)
    .head(10)
    .to_string()
)

# --------------------------------------------------
# 3. DUPLICATE POST SIGNATURES
# --------------------------------------------------

print("\n3. POST SIGNATURE DUPLICATES")

# This is a candidate signature, not a guaranteed post ID.
signature_columns = [
    "platform", "page_id", "date_posted", "caption"
]

valid_signature_rows = df.dropna(
    subset=["page_id", "date_posted"]
).copy()

signature_counts = (
    valid_signature_rows
    .groupby(signature_columns, dropna=False)
    .size()
)

repeated_signatures = signature_counts[signature_counts > 1]

print("Repeated post-signature groups:", len(repeated_signatures))
print(
    "Rows belonging to repeated signature groups:",
    int(repeated_signatures.sum())
)

# --------------------------------------------------
# 4. SAME PAGE AND CAPTION AT DIFFERENT TIMES
# --------------------------------------------------

print("\n4. SAME PAGE + CAPTION AT DIFFERENT TIMES")

page_caption = (
    df[df["caption"].str.strip().ne("")]
    .groupby(["platform", "page_id", "caption"], dropna=False)
    .agg(
        rows=("caption", "size"),
        distinct_dates=("date_posted", "nunique"),
        first_date=("date_posted", "min"),
        last_date=("date_posted", "max"),
    )
)

reused_page_captions = page_caption[
    (page_caption["rows"] > 1)
    & (page_caption["distinct_dates"] > 1)
]

print("Repeated page-caption groups:", len(reused_page_captions))
print(
    "Rows in these groups:",
    int(reused_page_captions["rows"].sum())
)

print("\nTop 10 repeated page-caption groups:")
print(
    reused_page_captions.sort_values(
        "rows", ascending=False
    ).head(10).to_string()
)

# --------------------------------------------------
# 5. IDENTICAL CAPTIONS ACROSS DIFFERENT PAGES
# --------------------------------------------------

print("\n5. IDENTICAL CAPTIONS ACROSS DIFFERENT PAGES")

caption_pages = (
    df[df["caption"].str.strip().ne("")]
    .groupby(["platform", "caption"])["page_id"]
    .nunique()
)

captions_across_pages = caption_pages[caption_pages > 1]

print(
    "Caption groups appearing on multiple pages:",
    len(captions_across_pages)
)

print("\nTop 10 captions across pages:")
print(
    captions_across_pages.sort_values(ascending=False)
    .head(10)
    .to_string()
)

# --------------------------------------------------
# 6. PAGE AND DATE CONCENTRATION
# --------------------------------------------------

print("\n6. PAGE CONCENTRATION")

rows_per_page = df.groupby(
    ["platform", "page_id"], dropna=False
).size()

print("Largest page row counts:")
print(rows_per_page.sort_values(ascending=False).head(15).to_string())

print("\nRows by month:")
valid_dates = df.dropna(subset=["date_posted"]).copy()
valid_dates["year_month"] = (
    valid_dates["date_posted"].dt.strftime("%Y-%m")
)

print(
    valid_dates.groupby(["platform", "year_month"])
    .size()
    .sort_values(ascending=False)
    .head(20)
    .to_string()
)

print("\nAudit complete. No dataset or application files were modified.")
