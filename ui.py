from convert import do_dataframe
import dearpygui.dearpygui as dpg
import pandas as pd


def process_file(file_path, output_file_path):
    df = pd.read_csv(file_path)
    woosb_df = df[df["Type"] == "woosb"].copy()
    woosb_df2 = woosb_df.dropna(axis=1, how="all").copy()
    new_df = do_dataframe(df, woosb_df2)

    new_df.replace({r"\n": " ", r"\r": " "}, regex=True, inplace=True)
    new_df = new_df.drop(columns=["ID"])
    new_df = new_df.drop(columns=["Categories"])

    new_df.to_csv(output_file_path, encoding="utf-8", index=False)
    print("Done. Wrote resulting mix and matches to", output_file_path)


def do_ui():
    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()

    def file_callback(sender, data):
        if len(data) > 0:
            file_path = data["file_path_name"]
            output_file_path = dpg.get_value("output_file_name")
            if output_file_path:
                process_file(file_path, output_file_path)

    with dpg.file_dialog(
        directory_selector=False,
        show=False,
        callback=file_callback,
        id="file_dialog_id",
        width=700,
        height=400,
    ):
        dpg.add_file_extension(".csv", color=(0, 255, 0, 255), custom_text="[CSV]")

    with dpg.window(label="Primary Window", tag="Primary Window"):
        dpg.add_text("Smart bundle to mix and match converter!")
        dpg.add_input_text(
            label="Output File Name",
            default_value="new_data.csv",
            tag="output_file_name",
        )
        dpg.add_button(
            label="Load File", callback=lambda: dpg.show_item("file_dialog_id")
        )

    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()
