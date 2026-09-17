import pandas as pd

# Charger le dataset (latin-1 car le CSV contient des accents)
df = pd.read_csv("data/superstore.csv", encoding="latin-1")

print("=" * 60)
print("DIMENSIONS")
print("=" * 60)
print(f"Lignes   : {len(df)}")
print(f"Colonnes : {len(df.columns)}")

print()
print("=" * 60)
print("COLONNES ET TYPES")
print("=" * 60)
for col in df.columns:
    print(f"  {col:<25} {str(df[col].dtype):<10}")

print()
print("=" * 60)
print("APERÇU (3 premières lignes)")
print("=" * 60)
print(df.head(3).to_string())

print()
print("=" * 60)
print("VALEURS MANQUANTES")
print("=" * 60)
missing = df.isnull().sum()
for col, count in missing.items():
    if count > 0:
        print(f"  {col:<25} {count} valeurs manquantes")
if missing.sum() == 0:
    print("  Aucune valeur manquante.")

print()
print("=" * 60)
print("STATISTIQUES (colonnes numériques)")
print("=" * 60)
print(df[["Sales", "Quantity", "Discount", "Profit"]].describe().to_string())

print()
print("=" * 60)
print("COLONNES CATÉGORIELLES")
print("=" * 60)
for col in ["Ship Mode", "Segment", "Region", "Category", "Sub-Category"]:
    if col in df.columns:
        values = df[col].unique()
        print(f"  {col:<25} {len(values)} valeurs : {list(values)[:5]}...")

print()
print("=" * 60)
print("PÉRIODE COUVERTE")
print("=" * 60)
if "Order Date" in df.columns:
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    print(f"  Du {df['Order Date'].min()} au {df['Order Date'].max()}")