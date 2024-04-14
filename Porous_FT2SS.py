import os
import socket
import sys

import matplotlib.pyplot as plt
import numpy as np

import ss_manipulation as ssmanip
import TRAPEZIUMParser as tparser

devname = socket.gethostname()

gkdir = r"C:\Git\UltimateGraph"
boxdir = r"D:\Box Sync\Personal"

sys.path.insert(1, gkdir)
import GraphKernel

output = "ComparisonWithPastTests"  # dir is same as the last input file

arg_list = "TRAPEZIUM"

# 180711 Irregular compression tests
arg_list = [
    {
        "fn_forcestroke": r"Experiments\ss.csv",
        "label": "Regular(180711)",
        "height": 25,
        "area": 625,
        "color": "green",
        "linestyle": (0, (1, 7)),
        "slope_delta": 0.001,
        "truecurve": False,
    },
]

func_param = {
    "ft2ss": [
        True,
    ]
}


def ft2ss(arg_list, output):
    # if arg_list is not specified, use TRAPEZIUMParser
    if arg_list == "TRAPEZIUM":
        fn_trapezium = [  # [ (fn_forcestroke, fn_dimension), ... ]

        ]
        arg_list = tparser.trapezium_parser(fn_trapezium)

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
    # calculate ft2ss
    for args in arg_list:
        ax, ax_true, ax_plastic = ssmanip.ft2ss(args, ax, ax_true, ax_plastic)

    # axis mod
    ax.legend(loc="best", shadow=False, framealpha=0)

    # save figure
    fn_ss_fig = os.path.join(
        boxdir, os.path.dirname(args.get("fn_forcestroke")), output + "_ss.png"
    )
    comp = None
    lims_list = [(0, 80, 0, 500), (0, 3, 0, 40), (0, 35, 0, 100), (35, 80, 50, 450)]
    range_list = ["_all", "_3pct", "_35pct", "_80pct"]
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
