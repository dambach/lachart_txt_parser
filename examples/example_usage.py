"""Example usage of the LabChart parser API.

This script demonstrates how to load a LabChart export, access its
metadata, channels, blocks and comments, and how to plot a single
channel from a specific block. The file path used here assumes the
exported text file is located in ``examples/data/labchart_file.example.txt``
relative to the project root.
"""

from labchart_parser import LabChartFile
import matplotlib.pyplot as plt
import pandas as pd

def main():
    # Load the exported file
    lc = LabChartFile.from_file("examples/data/labchart_file.example.txt")

    # Display metadata and column preview
    print("Metadata:", lc.metadata)
    print("Channels:", lc.channels)
    print("Number of blocks:", len(lc.blocks))
    print("Comments:")
    print(lc.comments.head())

    # Get df from block 1
    df_bloc1 = lc.get_block_df(1)
    # Plot pressure (channel "Pressure") for block 1
    plt.figure(figsize=(5, 2))
    plt.grid(True)
    plt.plot(df_bloc1["Time"], df_bloc1["Flow"])

    # ------------------------------------------
    # Cycle by cycle calculation: pressure difference between INSP and EXP
    # ------------------------------------------

    # Filter comments from block 1
    comments_b1 = lc.comments[lc.comments["block"] == 1].copy()
    comments_b1["Comment"] = comments_b1["Comment"].str.strip()

    # Time of INSP and EXP (in time_abs to be block-independent)
    t_inspi = comments_b1[comments_b1["Comment"].str.upper() == "INSPI"]["time_abs"].values
    t_expi  = comments_b1[comments_b1["Comment"].str.upper() == "EXPI"]["time_abs"].values

    paired_cycles = []
    for insp in t_inspi:
        # find the first EXP after this INSP
        exps_after = t_expi[t_expi > insp]
        if len(exps_after) == 0:
            continue
        expi = exps_after[0]

        # find the closest index in df_bloc1 for each time
        idx_inspi = (df_bloc1["time_abs"] - insp).abs().idxmin()
        idx_expi  = (df_bloc1["time_abs"] - expi).abs().idxmin()
        
        # compute difference between value at idx_inspi and max value between idx_inspi and idx_expi
        max_between = df_bloc1.loc[idx_inspi:idx_expi, "Pressure"].max()
        diff = abs(df_bloc1.loc[idx_inspi, "Pressure"] - max_between)

        paired_cycles.append(
            {
                "insp_time": insp,
                "expi_time": expi,
                "insp_pressure": df_bloc1.loc[idx_inspi, "Pressure"],
                "expi_pressure": df_bloc1.loc[idx_expi, "Pressure"],
                "pressure_diff": diff,
            }
        )

    # Convert to DataFrame for further analysis
    cycles_df = pd.DataFrame(paired_cycles)
    print(cycles_df.head())
    print("Number of detected cycles:", len(cycles_df))


    # Get pressure (channel "Pressure") for block 1
    pressure_df = lc.get_channel(1, "Pressure")
    plt.figure(figsize=(5, 2))
    plt.plot(pressure_df["Time"], pressure_df["value"])
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    
if __name__ == "__main__":
    main()
