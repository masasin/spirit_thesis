from latexify import latexify, figure, fig_size, savefig
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import pymc3 as pm
import seaborn.apionly as sns

from analysis import (
    analyze_data,
    analyze_differences,
    load_best_result,
    load_surveys,
    plot_detailed,
    plot_distribution,
    plot_overview,
    ExperimentType,
)


# Colours
default_cycler = plt.rcParamsDefault["axes.prop_cycle"]
colorblind_cmaps = ["Dark2", "Set2"]
cmap_main, cmap_complement = colorblind_cmaps
# cmap_main, cmap_complement = cmap_complement, cmap_main
colorblind_cyclers = {cmap: plt.cycler("color", plt.cm.get_cmap(cmap).colors)
                      for cmap in colorblind_cmaps}
plt.rcParams["axes.prop_cycle"] = colorblind_cyclers[cmap_main]



def do_paths():
    with figure("paths_overview", figsize=fig_size(0.44, 1.2)):
        ax1 = plt.subplot("121")
        plot_overview(results, ExperimentType.Onboard, color="C0")
        ax2 = plt.subplot("122", sharex=ax1, sharey=ax1)
        plot_overview(results, ExperimentType.Spirit, color="C1", ylabel="")
        plt.setp(ax2.get_yticklabels(), visible=False)

    with figure("paths_detailed", figsize=fig_size(0.44, 1.2)):
        ax1 = plt.subplot("121")
        plot_detailed(results, ExperimentType.Onboard, color="C0",
                      crosshair=True)
        ax2 = plt.subplot("122", sharex=ax1, sharey=ax1)
        plot_detailed(results, ExperimentType.Spirit, color="C1",
                      crosshair=True, ylabel="")
        plt.setp(ax2.get_yticklabels(), visible=False)


def do_distributions():
    with figure("distribution_onboard", figsize=fig_size(0.44, 1)):
        plot_distribution(results, ExperimentType.Onboard, color="C0",
                          crosshair=True)

    with figure("distribution_spirit", figsize=fig_size(0.44, 1)):
        plot_distribution(results, ExperimentType.Spirit, color="C1",
                          crosshair=True)


def do_durations():
    with figure("duration", figsize=fig_size(0.44, 1)):
        sns.factorplot(x="experiment", y="duration", data=analyses, kind="box")
        sns.swarmplot(x="experiment", y="duration", split=True, data=analyses,
                      palette=cmap_complement)
        plt.ylim(0, plt.ylim()[1])
        plt.ylabel("duration (s)")

    with figure("duration_runs", figsize=fig_size(0.44, 1)):
        sns.factorplot(x="order", y="duration", hue="experiment", data=analyses,
                       capsize=0.2)
        plt.ylim(0, plt.ylim()[1])
        plt.ylabel("duration (s)")
        plt.xlabel("run")


def do_movement():
    with figure("movement", figsize=fig_size(0.9, 0.4)):
        molten = pd.melt(analyses,
                         id_vars=["user", "experiment", "order", "group"],
                         value_vars=["path_length", "move_x", "move_y"])
        g = sns.factorplot(x="experiment", y="value", col="variable",
                           data=molten, kind="box")
        g.fig.axes[0].set_title("Path length")
        g.fig.axes[1].set_title("Movement in $x$")
        g.fig.axes[2].set_title("Movement in $y$")
        g.fig.axes[0].set_ylabel("distance (m)")
        plt.ylim(0, plt.ylim()[1])

    with figure("movement_x"):
        molten = pd.melt(analyses,
                         id_vars=["user", "experiment", "order", "group"],
                         value_vars=["move_l", "move_r", "move_x"])
        g = sns.factorplot(x="experiment", y="value", col="variable",
                           data=molten, kind="box")
        g.fig.axes[0].set_title("Movement left")
        g.fig.axes[1].set_title("Movement right")
        g.fig.axes[2].set_title("Movement in $x$")
        g.fig.axes[0].set_ylabel("distance (m)")
        plt.ylim(0, plt.ylim()[1])

    with figure("movement_y"):
        molten = pd.melt(analyses,
                         id_vars=["user", "experiment", "order", "group"],
                         value_vars=["move_b", "move_f", "move_y"])
        g = sns.factorplot(x="experiment", y="value", col="variable",
                           data=molten, kind="box")
        g.fig.axes[0].set_title("Movement backwards")
        g.fig.axes[1].set_title("Movement forwards")
        g.fig.axes[2].set_title("Movement in $y$")
        g.fig.axes[0].set_ylabel("distance (m)")
        plt.ylim(0, plt.ylim()[1])

    with figure("movement_back"):
        sns.factorplot(x="experiment", y="move_b", data=analyses, kind="box")
        sns.swarmplot(x="experiment", y="move_b", split=True, data=analyses,
                      palette=cmap_complement)
        plt.ylabel("distance (m)")
        plt.title("Movement backwards")

    with figure("movement_runs", figsize=fig_size(0.9, 0.4)):
        molten = pd.melt(analyses, id_vars=["user", "experiment", "order", "group"],
                                        value_vars=["path_length", "move_x", "move_y"])
        g = sns.factorplot(x="order", y="value", col="variable",
                           data=molten, hue="experiment", capsize=0.2)
        g.fig.axes[0].set_title("Path length")
        g.fig.axes[1].set_title("Movement in $x$")
        g.fig.axes[2].set_title("Movement in $y$")
        g.fig.axes[0].set_ylabel("distance (m)")
        g.fig.axes[0].set_xlabel("run")
        g.fig.axes[1].set_xlabel("run")
        g.fig.axes[2].set_xlabel("run")
        plt.ylim(0, plt.ylim()[1])

    with figure("movement_x_runs"):
        molten = pd.melt(analyses, id_vars=["user", "experiment", "order", "group"],
                                        value_vars=["move_l", "move_r", "move_x"])
        g = sns.factorplot(x="order", y="value", col="variable",
                           data=molten, hue="experiment")
        g.fig.axes[0].set_title("Movement left")
        g.fig.axes[1].set_title("Movement right")
        g.fig.axes[2].set_title("Movement in $x$")
        g.fig.axes[0].set_ylabel("distance (m)")
        g.fig.axes[0].set_xlabel("run")
        g.fig.axes[1].set_xlabel("run")
        g.fig.axes[2].set_xlabel("run")
        plt.ylim(0, plt.ylim()[1])

    with figure("movement_y_runs"):
        molten = pd.melt(analyses, id_vars=["user", "experiment", "order", "group"],
                                        value_vars=["move_b", "move_f", "move_y"])
        g = sns.factorplot(x="order", y="value", col="variable",
                           data=molten, hue="experiment")
        g.fig.axes[0].set_title("Movement backwards")
        g.fig.axes[1].set_title("Movement forwards")
        g.fig.axes[2].set_title("Movement in $y$")
        g.fig.axes[0].set_ylabel("distance (m)")
        g.fig.axes[0].set_xlabel("run")
        g.fig.axes[1].set_xlabel("run")
        g.fig.axes[2].set_xlabel("run")
        plt.ylim(0, plt.ylim()[1])


def do_errors():
    with figure("rms", figsize=fig_size(0.9, 0.4)):
        g = sns.factorplot(x="experiment", y="value", col="variable",
                           data=pd.melt(analyses, id_vars=["user", "experiment",
                                                           "order", "group"],
                                        value_vars=["rms", "rms_x", "rms_y"]),
                                        kind="box")
        g.fig.axes[0].set_title("RMS Error")
        g.fig.axes[1].set_title("RMS Error in $x$")
        g.fig.axes[2].set_title("RMS Error in $y$")
        g.fig.axes[0].set_ylabel("error (m)")

    with figure("rms_runs", figsize=fig_size(0.9, 0.4)):
        g = sns.factorplot(x="order", y="value", hue="experiment",
                           col="variable",
                           data=pd.melt(analyses, id_vars=["user","experiment",
                                                           "order", "group"],
                                        value_vars=["rms", "rms_x", "rms_y"]),
                                        capsize=0.2)
        g.fig.axes[0].set_title("RMS Error")
        g.fig.axes[1].set_title("RMS Error in $x$")
        g.fig.axes[2].set_title("RMS Error in $y$")
        g.fig.axes[0].set_ylabel("error (m)")
        g.fig.axes[0].set_xlabel("run")
        g.fig.axes[1].set_xlabel("run")
        g.fig.axes[2].set_xlabel("run")

    with figure("distance", figsize=fig_size(0.9, 0.4)):
        g = sns.factorplot(x="experiment", y="value", col="variable",
                           data=pd.melt(analyses, id_vars=["user", "experiment",
                                                           "order", "group"],
                                        value_vars=[r"dist_err", r"x_err",
                                                    r"y_err"]), kind="box")
        g.fig.axes[0].set_title("Distance from target")
        g.fig.axes[1].set_title("Distance from target in $x$")
        g.fig.axes[2].set_title("Distance from target in $y$")
        g.fig.axes[0].set_ylabel("distance (m)")
        g.axes[0][0].axhline(0, color="black", linewidth=1, zorder=-1)
        g.axes[0][1].axhline(0, color="black", linewidth=1, zorder=-1)
        g.axes[0][2].axhline(0, color="black", linewidth=1, zorder=-1)


def do_surveys():
    with figure("tlx_results", figsize=fig_size(0.44, 1)):
        sns.factorplot(x="experiment", y="tlx", data=tlx, kind="box")
        sns.swarmplot(x="experiment", y=r"tlx",
                      data=tlx, palette=cmap_complement, split=True)
        plt.ylim(0, plt.ylim()[1])
        plt.ylabel("NASA-TLX weighted score")

    with figure("tlx_components", figsize=fig_size(0.44, 1)):
        molten = pd.melt(tlx, id_vars=["user", "experiment", "order"],
                         value_vars=["mental", "physical", "temporal",
                                     "performance", "effort", "frustration"],
                         var_name="component", value_name="score")
        g = sns.barplot(x=r"component", y="score", hue="experiment",
                        data=molten)

        plt.gca().set_xticklabels(
                ["MD", "PD", "TD", "P", "E", "F"])

        plt.xlabel("NASA-TLX component")
        plt.ylabel("score")

    with figure("survey_overview", figsize=fig_size(0.9, 0.5)):
        molten = pd.melt(surveys, id_vars=["user", "experiment", "order"],
                         value_vars=[r"orientation_understanding",
                                     r"orientation_control",
                                     r"position_understanding",
                                     r"position_control",
                                     r"spacial_understanding",
                                     r"spacial_control"],
                         var_name="question", value_name="rating")
        g = sns.barplot(x=r"rating", y=r"question", hue="experiment",
                        data=molten)
        sns.swarmplot(x="rating", y=r"question", data=molten, hue="experiment",
                      split=True, palette=cmap_complement)

        plt.gca().set_yticklabels(
                ["angle aware", "angle control",
                 "position aware", "position control",
                 "rel. pos. aware", "rel. pos. control"])

        handles, labels = g.get_legend_handles_labels()
        plt.legend(handles[2:], labels[2:])
        plt.xlabel("rating")
        plt.title("Survey results")


def do_differences(recalculate=False):
    trace_cols = ["duration", "dist_err", "x_err", "y_err", "rms_x", "rms_y"]
    trace_coeffs = [[(5, 50), 50]] + [[(0, 2), 0.5]]*5
    trace_cols = ["path_length", "move_l", "move_r", "move_x", "move_b",
                  "move_f", "move_y"]
    trace_coeffs = [[(0, 10), 10], [(0, 5), 3], [(0, 5), 3], [(0, 10), 6],
                    [(0, 5), 1.5], [(0, 5), 7], [(0, 10), 9]]

    if recalculate:
        traces = analyze_differences(analyses, trace_cols, trace_coeffs)
    else:
        traces = {col: load_best_result(col) for col in trace_cols}
    for col, best_result in traces.items():
        trace = best_result.trace
        with figure(f"mean_std_{col}"):
            ax = pm.plot_posterior(trace[100:],
                                   varnames=[r"group1_mean", r"group2_mean",
                                             r"group1_std", "group2_std"],
                                   kde_plot=True, color="C0")
            for a in (1, 3):
                ax[a].lines[0].set_color("C1")

        with figure(f"difference_{col}"):
            pm.plot_posterior(trace[1000:],
                              varnames=["difference of means", "effect size"],
                              ref_val=0, kde_plot=True, color="C2")


if __name__ == "__main__":
    latexify()

    # results, analyses = analyze_data()
    # print("Loaded files")

    # do_paths()
    # do_distributions()
    # do_durations()
    # do_movement()
    # do_errors()

    # users, tlx, surveys = load_surveys()
    # print("Loaded surveys")

    # do_surveys()

    # WARNING: Takes a long time with recalculate.
    # do_differences()

