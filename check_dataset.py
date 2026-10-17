import pandas as pd

df = pd.read_csv(r"C:\Users\Keerthan\Downloads\social-media-post-performance-forecasting\archive\train.csv")

print("\n=== SHAPE ===")
print(df.shape)

print("\n=== COLUMNS ===")
print(df.columns.tolist())

print("\n=== PLATFORM DISTRIBUTION ===")
print(df["platform"].value_counts())

print("\n=== CONTENT TYPES ===")
print(df["content_type"].value_counts())

print("\n=== MISSING VALUES ===")
print(df.isnull().sum())

print("\n=== DUPLICATE ROWS ===")
print(df.duplicated().sum())

print("\n=== TARGET SUMMARY ===")
print(df[["likes", "comments"]].describe())

print("\n=== ZERO TARGETS ===")
print("Likes = 0:", (df["likes"] == 0).sum())
print("Comments = 0:", (df["comments"] == 0).sum())

# Convert timestamps
df["date_posted"] = pd.to_datetime(df["date_posted"], errors="coerce")
df["recorded_at"] = pd.to_datetime(df["recorded_at"], errors="coerce")

# Observation window
df["observation_hours"] = (
    df["recorded_at"] - df["date_posted"]
).dt.total_seconds() / 3600

print("\n=== OBSERVATION WINDOW ===")
print(df["observation_hours"].describe())

print("\n=== NEGATIVE OBSERVATION WINDOWS ===")
print((df["observation_hours"] < 0).sum())

print("\n=== OBSERVATION WINDOW BY PLATFORM ===")
print(
    df.groupby("platform")["observation_hours"]
      .describe()
)

print("\n=== LIKES BY PLATFORM ===")
print(
    df.groupby("platform")["likes"]
      .agg(["count", "mean", "median", "min", "max"])
)

print("\n=== COMMENTS BY PLATFORM ===")
print(
    df.groupby("platform")["comments"]
      .agg(["count", "mean", "median", "min", "max"])
)

print("\n=== UNIQUE IDS ===")
print("Total rows:", len(df))
print("Unique IDs:", df["id"].nunique())

print("\n=== DUPLICATE IDS ===")
print(
    df["id"].value_counts()
    .loc[lambda x: x > 1]
    .head(20)
)

print("\n=== UNIQUE PAGE IDs ===")
print(df["page_id"].nunique())

print("\n=== DATE RANGE ===")
print("Posted:", df["date_posted"].min(), "to", df["date_posted"].max())
print("Recorded:", df["recorded_at"].min(), "to", df["recorded_at"].max())

df["observation_days"] = (
    df["recorded_at"] - df["date_posted"]
).dt.total_seconds() / 86400

df["total_engagement"] = (
    df["likes"] + df["comments"]
)

df["engagement_per_day"] = (
    df["total_engagement"] /
    df["observation_days"].clip(lower=1 / 24)
)

print("\n=== OBSERVATION DAYS ===")
print(df["observation_days"].describe())

print("\n=== ENGAGEMENT PER DAY ===")
print(df["engagement_per_day"].describe())

print("\n=== CORRELATION WITH OBSERVATION TIME ===")
print(
    df[
        ["observation_days", "likes", "comments", "total_engagement"]
    ].corr()
)

print("\n=== RECENT POSTS ===")
print(
    df.sort_values("date_posted", ascending=False)[
        [
            "platform",
            "date_posted",
            "recorded_at",
            "content_type",
            "likes",
            "comments"
        ]
    ].head(10)
)