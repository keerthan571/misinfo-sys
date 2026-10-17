import pandas as pd

DATA_PATH = (
    r"C:\Users\Keerthan\Downloads"
    r"\social-media-post-performance-forecasting"
    r"\archive\train.csv"
)

df = pd.read_csv(DATA_PATH)
df["platform"] = df["platform"].str.lower()

df = df[
    df["platform"].isin(["facebook", "instagram"])
].copy()

df["likes"] = pd.to_numeric(df["likes"], errors="coerce")
df["comments"] = pd.to_numeric(df["comments"], errors="coerce")
df["total_engagement"] = df["likes"] + df["comments"]

df = df.dropna(
    subset=["platform", "content_type", "likes", "comments"]
).copy()

df = df[
    (df["likes"] >= 0) & (df["comments"] >= 0)
].copy()

# Descriptive audit: platform-specific engagement thresholds.
df["high_engagement"] = 0

for platform in ["facebook", "instagram"]:
    mask = df["platform"] == platform
    threshold = df.loc[mask, "total_engagement"].quantile(0.75)
    df.loc[mask, "high_engagement"] = (
        df.loc[mask, "total_engagement"] >= threshold
    ).astype(int)

print("PLATFORM COUNTS")
print(df["platform"].value_counts())

print("\nCONTENT TYPES BY PLATFORM")
counts = pd.crosstab(df["content_type"], df["platform"])
print(counts.to_string())

print("\nCONTENT TYPE ENGAGEMENT AUDIT")
audit = (
    df.groupby(["platform", "content_type"], dropna=False)
    .agg(
        posts=("total_engagement", "size"),
        median_engagement=("total_engagement", "median"),
        mean_engagement=("total_engagement", "mean"),
        high_engagement_rate=("high_engagement", "mean"),
    )
    .reset_index()
)

audit["high_engagement_rate"] *= 100

print(
    audit.sort_values(["platform", "posts"], ascending=[True, False])
    .to_string(
        index=False,
        formatters={
            "median_engagement": "{:.1f}".format,
            "mean_engagement": "{:.1f}".format,
            "high_engagement_rate": "{:.1f}%".format,
        },
    )
)

print("\nAudit complete. No application files were changed.")
