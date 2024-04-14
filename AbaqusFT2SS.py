import os
import socket
import sys

import matplotlib.pyplot as plt
import numpy as np

import ss_manipulation as ssmanip

gkdir = r"C:\Users\Git\UltimateGraph"
boxdir = r"D:\Box Sync\Personal"

sys.path.insert(1, gkdir)
import GraphKernel

output = "SS"  # dir is same as the last input file
func_param = {
    "ft2ss": [
        True,
    ],
}
arg_list = [
    {
        "fn_forcestroke": os.path.abspath(
            r"C:\AbaqusWD\Force-Displacement.csv"
        ),
        "label": "Initial (L25SE2)",
        "height": 25.0,
        "area": 25.0 * 25.0,
        "color": "navy",
        "linestyle": "-",
        "slope_delta": 0.001,
        "truecurve": False,
    },
]


def ft2ss(args_list, output):
    fig, ax = GraphKernel.format_general(
        xtitle="Engineering strain, $e$ (%)",
        ytitle="Engineering stress, $\sigma$ / MPa",
        w=None,
        h=None,
        r=None,
        xt_space=None,
        yt_space=None,
    )
    fig_true, ax_true = GraphKernel.format_general(
        xtitle="True strain, $e$",
        ytitle="True stress, $\sigma$ / MPa",
        w=None,
        h=None,
        r=None,
        xt_space=None,
        yt_space=None,
    )
    fig_plastic, ax_plastic = GraphKernel.format_general(
        xtitle="Plastic strain, $e$",
        ytitle="True stress, $\sigma$ / MPa",
        w=None,
        h=None,
        r=None,
        xt_space=None,
        yt_space=None,
    )

    print(
        "Young's modulus was calculated with certain strain delta and then moving average was applied.\n"
    )
    for args in args_list:
        fn, label, height, area, color, linestyle = (
            args["fn_forcestroke"],
            args["label"],
            args["height"],
            args["area"],
            args["color"],
            args["linestyle"],
        )
        # fn = os.path.join(boxdir, fn)
        ft = np.loadtxt(fn, float, delimiter=",", skiprows=1, encoding="utf-8")
        strain = ft[:, 0] / height
        stress = ft[:, 1] / area

        # calculate Young's modulus
        print(f"\nSpecimen: {label}")
        _, _, _ = ssmanip.youngs(strain, stress, args.get("slope_delta"))

        # save stress strain curve
        fn_ss = os.path.splitext(fn)[0] + "_ss.csv"
        np.savetxt(
            fn_ss, np.column_stack((strain * 100, stress)), header="strain,stress", delimiter=","
        )
        ax.plot(strain * 100, stress, ls=linestyle, lw=1, color=color, label=label)

        if args.get("truecurve"):
            truestrain, truestress, plasticstrain, plasticstress = ssmanip.truecurve(
                strain, stress, args.get("slope_delta")
            )
            # true stress-strain curve
            fn_truess = os.path.splitext(fn_ss)[0] + "_true.csv"
            np.savetxt(
                fn_truess,
                np.column_stack((truestrain, truestress)),
                header="truestrain,truestress",
                delimiter=",",
            )
            ax_true.plot(truestrain, truestress, ls=linestyle, lw=1, color=color, label=label)
            # plastic stress-strain curve
            fn_plasticss = os.path.splitext(fn_ss)[0] + "_plastic.csv"
            np.savetxt(
                fn_plasticss,
                np.column_stack((plasticstrain, plasticstress)),
                header="plasticstrain,plasticstress",
                delimiter=",",
            )
            ax_plastic.plot(
                plasticstrain, plasticstress, ls=linestyle, lw=1, color=color, label=label
            )

    # axis mod
    ax.legend(loc="best", shadow=False, framealpha=0)

    # save figure
    fn_ss_fig = os.path.join(os.path.dirname(fn), output + "_ss.png")
    comp = None  # {"compression": "tiff_lzw"}
    # lims = (0, 90, 0, 1500)
    lims_list = [(0, 90, 0, 1500), (0, 5, 0, 100), (70, 85, 600, 1500)]
    range_list = ["_all", "_5pct", "_80pct"]
    for i, lims in enumerate(lims_list):
        GraphKernel.post_proccessing2(
            fig,
            ax,
            os.path.splitext(fn_ss_fig)[0] + range_list[i] + ".png",
            lims,
            dpi=300,
            comp=comp,
            tight=True,
        )

    if args.get("truecurve"):
        # true stress-strain curve
        ax_true.legend(loc="best", shadow=False, framealpha=0)
        fn_truess_fig = os.path.splitext(fn_ss_fig)[0] + "_true.png"
        lims_true = (0, 2, 0, 300)
        GraphKernel.post_proccessing2(
            fig_true, ax_true, fn_truess_fig, lims_true, dpi=300, comp=comp, tight=True
        )
        # plastic stress-strain curve
        ax_plastic.legend(loc="best", shadow=False, framealpha=0)
        fn_plasticss_fig = os.path.splitext(fn_ss_fig)[0] + "_plastic.png"
        lims_plastic = (0, 2, 0, 300)
        GraphKernel.post_proccessing2(
            fig_plastic, ax_plastic, fn_plasticss_fig, lims_plastic, dpi=300, comp=comp, tight=True
        )

    plt.close()

if __name__ == "__main__":
    exec = {ft2ss: func_param["ft2ss"]}
    [func(arg_list, output) for func, param in exec.items() if param[0] == True]
