from convert import do_dataframe
import fire
import pandas as pd
import rich


def process_file(file_path, out="OUTPUT-mix-and-match.csv"):
    """
    Convert a CSV file from the Smart Bundle format to the Mix and Match format.

    file_path: Path to the CSV file to convert. The should be a FULL export of your WooCommerce products (not just the Smart Bundles).
    output_file_path: Path to the file to write the resulting Mix and Match CSV to.
    """
    df = pd.read_csv(file_path)
    woosb_df = df[df["Type"] == "woosb"].copy()
    woosb_df2 = woosb_df.dropna(axis=1, how="all").copy()
    new_df = do_dataframe(df, woosb_df2)

    new_df.replace({r"\n": " ", r"\r": " "}, regex=True, inplace=True)
    new_df = new_df.drop(columns=["ID"])
    new_df = new_df.drop(columns=["Categories"])

    new_df.to_csv(out, encoding="utf-8", index=False)
    print("")
    rich.print(
        f" 🚀 Done. Wrote resulting mix and matches to [bold green]{out}[/bold green]"
    )


if __name__ == "__main__":
    fire.Fire(process_file)
