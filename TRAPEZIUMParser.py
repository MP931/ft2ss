import os
import socket

import numpy as np
import pandas as pd

file_list = [  # (fn_forcestroke, fn_dimension)

]

gkdir = r"C:\Git\UltimateGraph"
boxdir = r"D:\Box Sync\Personal"
 
def trapezium_parser(file_list):
    arg_list = []
    # loop over the trapezium files
    for fn in file_list:
        # read the force-time data from the TRAPEZIUM X
        fn_ft = os.path.join(boxdir, fn[0])
        df_ft = pd.read_csv(fn_ft, header=0, skiprows=range(1, 3))

        # read the specimen dimension
        fn_dim = os.path.join(boxdir, fn[1])
        df_dim = pd.read_csv(
            fn_dim, header=0, index_col=0, dtype={"Name": str, "Color": str, "Line": str}
        )

        # prepare the list of specimen names (one specimen uses 3 columns, TIME, FORCE, STROKE)
        specs = np.array([])
        for col in df_ft.columns:
            if not "Unnamed" in col:
                specs = np.append(specs, col)

        # loop over the specimens
        for i, spec in enumerate(specs):
            # extract the columns for each specimen
            currentcols = df_ft.iloc[:, i * 3 : i * 3 + 3]
            # remove NaN from dataframe
            currentcols = currentcols.dropna()
            # reorder the columns as STROKE, FORCE
            ft = currentcols.iloc[:, [2, 1]].to_numpy()
            # save the data
            fn_out = os.path.splitext(fn_ft)[0] + "_" + spec + ".csv"
            np.savetxt(fn_out, ft, delimiter=",", header="Stroke(mm),Force(N)")

            current_arg = {
                "fn_forcestroke": fn_out.split("" + "\\")[1],
                "label": spec,
                "height": df_dim.loc[spec, "Height(mm)"],
                "area": df_dim.loc[spec, "Area(mm2)"],
                "color": df_dim.loc[spec, "Color"],
                "linestyle": df_dim.loc[spec, "Line"],
                "slope_delta": 0.001,
                "truecurve": False,
            }
            arg_list.append(current_arg)
    print(arg_list)
    return arg_list


if __name__ == "__main__":
    trapezium_parser(file_list)
