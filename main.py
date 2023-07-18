import json

import pandas as pd


pd.set_option("display.max_columns", 150)

from typing import Optional

from pandas import DataFrame
from pandas import Series


def get_product_by_id(df: DataFrame, product_id: int, field: Optional[str] = None):
    """
    Returns a product from the DataFrame with the specified ID.

    If a field is specified, returns just that field from the product.
    """
    product = df.loc[df["ID"] == product_id]
    if field is not None:
        product = product[field].iloc[0]
    return product


def get_product_by_sku(df: DataFrame, sku: str, field: Optional[str] = None):
    """
    Returns a product from the DataFrame with the specified SKU.

    If a field is specified, returns just that field from the product.
    """
    product = df.loc[df["SKU"] == sku]
    if field is not None:
        product = product[field].iloc[0]
    return product


def convert_woosb_sku_to_mnm(master_df: DataFrame, row: Series):
    row_copy = row.copy()
    first_woosb_ids = row["Meta: woosb_ids"]
    ids_and_default_quantities = first_woosb_ids.split(",")
    product_ids = []

    # Split each item in the list into a product ID and default quantity, and add them to the respective lists
    for item in ids_and_default_quantities:
        product_id, _ = item.split("/")
        # Product ID can be one of two types: ID, which is int, or SKU, which is str
        if product_id.startswith("sku-"):
            _, sku = product_id.split("-")
            try:
                product_id = get_product_by_sku(master_df, sku, "ID")
                product_ids.append(int(product_id))
            except IndexError:
                print(
                    f"SKU {sku} not found in master_df. Skipping. (Product is {row['Name']}, sku {row['SKU']})"
                )
                return row_copy
        else:
            product_ids.append(int(product_id))

    skus = {}
    for product_id in product_ids:
        sku = get_product_by_id(master_df, product_id, "SKU")
        skus[str(product_id)] = {"product_id": sku}

    row_copy["MnM Contents (JSON-encoded)"] = json.dumps(skus)
    return row_copy


def convert_woosb_minmax_to_mnm(row: Series):
    row_copy = row.copy()
    woosb_min = row["Meta: woosb_limit_whole_min"]
    woosb_max = row["Meta: woosb_limit_whole_max"]
    row_copy["MnM Minimum Container Size"] = woosb_min
    row_copy["MnM Maximum Container Size"] = woosb_max
    return row_copy


def convert_woosb_discount_to_mnm(row: Series):
    row_copy = row.copy()
    woosb_discount = row["Meta: woosb_discount"]
    row_copy["MnM Per-Item Discount"] = woosb_discount
    return row_copy


def add_defaults(row: Series):
    row_copy = row.copy()
    row_copy["MnM Per-Item Pricing"] = 1.0
    row_copy["MnM Per-Item Shipping"] = 0.0
    row_copy["MnM Add to Cart Form Location"] = "default"
    row_copy["MnM Layout"] = "grid"
    row_copy["Type"] = "mix-and-match"

    return row_copy


def do_row(df, woosb_row):
    row = convert_woosb_minmax_to_mnm(woosb_row)
    row = convert_woosb_sku_to_mnm(df, row)
    row = convert_woosb_discount_to_mnm(row)
    row = add_defaults(row)
    return row


def do_dataframe(df, woosb_df):
    rows_list = []
    for index, row in woosb_df.iterrows():
        transformed_row = do_row(df, row)
        rows_list.append(transformed_row)
    new_df = pd.concat(rows_list, axis=1).transpose()

    # Drop rows where 'MnM Contents (JSON-encoded)' is NaN
    new_df = new_df.dropna(subset=["MnM Contents (JSON-encoded)"])

    return new_df


if __name__ == "__main__":
    WOO_EXPORTED_FILE_PATH = "SOMETHING.csv"
    file_path = WOO_EXPORTED_FILE_PATH  # replace with your preferred file path
    df = pd.read_csv(file_path)
    woosb_df = df[df["Type"] == "woosb"].copy()
    woosb_df2 = woosb_df.dropna(axis=1, how="all").copy()
    new_df = do_dataframe(df, woosb_df2)

    new_csv_path = "new_data.csv"  # replace with your preferred file path
    new_df.replace({r"\n": " ", r"\r": " "}, regex=True, inplace=True)
    new_df = new_df.drop(columns=["ID"])
    new_df = new_df.drop(columns=["Categories"])

    new_df.to_csv(new_csv_path, encoding="utf-8", index=False)
    print("Done. Wrote result to", new_csv_path)
