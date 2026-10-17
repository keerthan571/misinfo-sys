
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

print("Total rows:", len(df))
print("Unique pages:", df["page_id"].nunique())
print("Missing posting dates:", df["date_posted"].isna().sum())

valid = df.dropna(subset=["date_posted"]).copy()

print("\nEarliest post:", valid["date_posted"].min())
print("Latest post:", valid["date_posted"].max())

print("\nRows per year-month:")
print(
    valid.groupby(valid["date_posted"].dt.to_period("M"))
    .size()
    .to_string()
)

print("\nPages per platform:")
print(
    df.groupby("platform")["page_id"]
    .nunique()
    .to_string()
)

print("\nRows per platform:")
print(df["platform"].value_counts().to_string())

print("\nPage overlap between earlier and later halves:")

valid = valid.sort_values("date_posted")
cutoff = valid["date_posted"].quantile(0.80)

earlier = valid[valid["date_posted"] < cutoff]
later = valid[valid["date_posted"] >= cutoff]

earlier_pages = set(earlier["page_id"])
later_pages = set(later["page_id"])

print("80th-percentile cutoff:", cutoff)
print("Earlier-period rows:", len(earlier))
print("Later-period rows:", len(later))
print("Earlier-period pages:", len(earlier_pages))
print("Later-period pages:", len(later_pages))
print("Pages appearing in both periods:", len(earlier_pages & later_pages))
print("Pages exclusive to later period:", len(later_pages - earlier_pages))
