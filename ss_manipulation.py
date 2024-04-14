import os
import socket

import numpy as np
from scipy.ndimage import uniform_filter1d


def truecurve(strain, stress, slope_delta):
    # convert engineering stress to true stress
    truestress = stress * (1 - strain)

    # convert engineering strain to true strain
    truestrain = -1 * np.log(1 - strain)

    # convert to true stress - plastic strain curve
    # find maximum slope point in stress-strain curve in the strain range of 0-2%
    slope_max, slope_max_idx, delta = slopemax(truestrain, truestress, slope_delta)

    print(
        f"True stress-strain\nMaximum slope was: {slope_max:.2f} MPa at ({truestrain[slope_max_idx]*100:.4f}-{(truestrain[slope_max_idx+delta])*100:.4f} %, {truestress[slope_max_idx]:.2f}-{truestress[slope_max_idx+delta]:.2f} MPa)"
    )

    yield_idx = yieldpoint(truestrain, truestress, slope_max, slope_max_idx)
    plastic_strain = truestrain[yield_idx:] - truestrain[yield_idx]
    plastic_stress = truestress[yield_idx:]

    return truestrain, truestress, plastic_strain, plastic_stress


def yieldpoint(strain, stress, slope_max, slope_max_idx):
    offset_strain = 0.002  # for 0.2 % proof stress
    b = stress[slope_max_idx] - slope_max * strain[slope_max_idx]  # y-intercept

    diff_max = np.inf
    i = 0
    while strain[i] < 0.03:  # find the intersection until 3% in strain
        diff = np.abs(stress[i] - (slope_max * (strain[i] - offset_strain) + b))
        if diff < diff_max:
            diff_max = diff
            yield_idx = i
        i += 1

    print(
        f"{offset_strain*100:.1f}% yield point was: {strain[yield_idx]*100:.4f} %, {stress[yield_idx]:.2f} MPa"
    )

    return yield_idx


def slopemax(strain, stress, slope_delta):
    # find index of strain_delta
    delta = np.nonzero(strain < slope_delta)[0][-1]

    # calculate slope with delta in stress-strain curve in the strain range of 0-2%
    slope_max = 0.0
    i = 0
    max_idx = np.nonzero(strain < (0.02 - slope_delta))[0][-1]
    slopes = np.zeros(max_idx, dtype=float)
    for i in range(max_idx):
        stress_delta = stress[i + delta] - stress[i]
        strain_delta = strain[i + delta] - strain[i]
        slopes[i] = stress_delta / strain_delta
        if slopes[i] > slope_max:
            slope_max = slopes[i]
            slope_max_idx = i

    # take moving average of slopes and find maximum slope
    averaged_slopes = uniform_filter1d(
        slopes, size=12, mode="nearest"
    )  # windows size of 12, according to Ichikawa's analysis
    slope_max = np.max(averaged_slopes)
    slope_max_idx = np.argmax(averaged_slopes)

    return slope_max, slope_max_idx, delta


def youngs(strain, stress, slope_delta):
    if slope_delta == None:
        slope_delta = 0.001  # default value (0.1 %)

    # find maximum slope point in stress-strain curve in the strain range of 0-2%
    slope_max, slope_max_idx, delta = slopemax(strain, stress, slope_delta)

    print(
        f"Maximum slope was: {slope_max:.2f} MPa at ({strain[slope_max_idx]*100:.4f}-{(strain[slope_max_idx+delta])*100:.4f} %, {stress[slope_max_idx]:.2f}-{stress[slope_max_idx+delta]:.2f} MPa)"
    )

    yield_idx = yieldpoint(strain, stress, slope_max, slope_max_idx)

    return slope_max, slope_max_idx, yield_idx


def ssoffset(strain, stress, slope_delta):
    # find maximum slope point in stress-strain curve in the strain range of 0-2%
    slope_max, slope_max_idx, _ = slopemax(strain, stress, slope_delta)

    # calculate the crossing point of the maximum slope line and the strain axis
    offset_strain = strain[slope_max_idx] - (stress[slope_max_idx] / slope_max)
    offset = np.nonzero(strain < offset_strain)[0][-1]

    # offset stress-strain curve
    stress = stress[offset:]
    strain = strain[offset:] - strain[offset]

    return strain, stress


def ft2ss(args, ax, ax_true, ax_plastic):
    # define box sync directory
    devname = socket.gethostname()
    if devname == "Desktop-Endeavor":
        gkdir = r"C:\Users\Mahiro Sawada\Git\UltimateGraph"
        boxdir = r"D:\Box Sync\Personal\Sawada"
        hpc_wd = r"D:\Box Sync\Personal\Sawada\Discussion\220927_StructuralOptimization\HPC_copy"
    elif devname == "X1CarbonGen10":
        gkdir = r"C:\Users\MahiroSawada\Documents\Github\UltimateGraph"
        boxdir = r"C:\Users\MahiroSawada\Box Sync\Personal\Sawada"
        hpc_wd = r"C:\Users\MahiroSawada\Documents\HPC-CORE\PoreArrangement"
    elif devname == "Desktop-Radiant":
        gkdir = r"D:\M.Sawada\Documents\Git\UltimateGraph"
        boxdir = r"D:\Box Sync\Personal\Sawada"
        hpc_wd = r" "

    # read arguments
    fn, label, height, area, color, linestyle, slope_delta = (
        args["fn_forcestroke"],
        args["label"],
        args["height"],
        args["area"],
        args["color"],
        args["linestyle"],
        args["slope_delta"],
    )
    fn = os.path.join(boxdir, fn)
    ft = np.loadtxt(fn, float, delimiter=",", skiprows=1, encoding="utf-8")
    strain = ft[:, 0] / height
    stress = ft[:, 1] / area

    # manipulate stress strain curve
    print(f"\nSpecimen: {label}")
    if slope_delta:
        strain, stress = ssoffset(strain, stress, slope_delta)
    _, _, _ = youngs(strain, stress, slope_delta)

    # save stress strain curve
    fn_ss = os.path.splitext(fn)[0] + "_ss.csv"
    np.savetxt(
        fn_ss, np.column_stack((strain * 100, stress)), header="strain,stress", delimiter=","
    )
    ax.plot(strain * 100, stress, ls=linestyle, lw=1, color=color, label=label)

    if args.get("truecurve"):
        truestrain, truestress, plasticstrain, plasticstress = truecurve(
            strain, stress, slope_delta
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
        ax_plastic.plot(plasticstrain, plasticstress, ls=linestyle, lw=1, color=color, label=label)

    return ax, ax_true, ax_plastic
