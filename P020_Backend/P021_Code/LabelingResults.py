import pandas as pd
import os
from tkinter import messagebox


class ResultsDataFrame:
    """
    A class that is used to save and process the data in the results dataframe

    ...

    Attributes
    ----------
    results_path : str
        The storage path where the result data is saved/The memory path where result data is located
    df : pd.DataFrame
        The DataFrame which is used to store and process the result data

    Methods
    -------
    append_result(filename, label, zero_offsets)
        Appends a new result or changes an existing entry
    to_csv()
        Saves the results to the results path
    get_label(filename)
        Returns the entered labels of a specific entry
    """

    def __init__(self, cutout_path, kernel_size):
        """
        Parameter
        ---------
        cutout_path : Any
            The path of the dataset
        kernel_size : str
            The size of the cutout matrix

        """
        columns = ["filename", "use_case", "arrowlo", "arrowo", "arrowro", "arrowl", "arrowr", "arrowlu", "arrowu",
                   "arrowru", "offset_lu", "offset_l", "offset_lo",	"offset_u",	"offset_o",	"offset_ru", "offset_r",
                   "offset_ro",	"center"]
        results_file = f"Cutout_{kernel_size}_Results_Labeled.csv"
        self.results_path = os.path.join(cutout_path, results_file)
        if results_file in os.listdir(cutout_path):
            self.df = pd.read_csv(self.results_path, delimiter=";")
        else:
            self.df = pd.DataFrame(columns=columns)

    def append_result(self, filename, label, zero_offsets):
        """
        Appends a new result or changes an existing entry

        Parameter
        ---------
        filename : Any
            The filename for which a new entry is to be set
        label : Any
            The labeling results
        zero_offsets : Any
            The zero offset values

        """
        if filename in self.df["filename"].values:
            self.df.loc[self.df["filename"] == filename, label.keys()] = label.values()
        else:
            use_case = "train"
            if len(self.df.index) % 5 == 0:
                use_case = "test"
            new_entry = {"filename": filename, "use_case": use_case} | label | zero_offsets
            new_entry = {key: [value] for key, value in new_entry.items()}
            new_df = pd.DataFrame.from_dict(new_entry)
            self.df = pd.concat([self.df, new_df], ignore_index=True)

    def to_csv(self):
        """
        Saves the results to the results path

        """
        self.df.to_csv(self.results_path, sep=";", index=False)

    def get_label(self, filename):
        """
        Returns the entered labels of a specific entry

        Parameter
        --------
        filename : Any
            The filename of which the label should be returned

        """
        if filename in self.df["filename"].values:
            label = self.df.loc[self.df["filename"] == filename]
            label = label.values.tolist()[0][2:10]
            return label
        else:
            messagebox.showerror("Label nicht gefunden", "Der Punktwolkenausschnitt ist nicht in der Label Datei. ")
            return None
