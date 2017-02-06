from latexify import latexify, fig_size, savefig
import matplotlib as mpl
import matplotlib.pyplot as plt

from collections import namedtuple
from enum import Enum
import glob
import pickle
import re

import numpy as np
import pandas as pd
import seaborn.apionly as sns
import pymc3 as pm


# Named Tuples
BestResult = namedtuple("BestResult", "trace model")
RunData = namedtuple("RunData", "experiment user run")
TlxResponse = namedtuple("TlxResponse", "code raw weight score")
Coords = namedtuple("Coords", "x y")
TARGET = Coords(0, 6)

# Regexes
FILENAME_PATTERN = "experiment-(\d)_user-(\d+)_run-(\d+)"
filename_regex = re.compile(pattern=FILENAME_PATTERN)

# Enums
DroneState = Enum("DroneState",
                  "Emergency Inited Landed Flying Hovering Test"
                  "TakingOff GotoHover Landing Looping".split(),
                  start=0)
ExperimentType = Enum("ExperimentType", "Onboard Spirit Combined LineOfSight")


def change_color(color, saturation=0, value=0):
    rgb = mpl.colors.ColorConverter.to_rgb(color)
    h, s, v = mpl.colors.rgb_to_hsv(rgb)
    s *= 1 + saturation/100
    s = np.clip(s, 0, 1)
    v *= 1 + value/100
    v = np.clip(v, 0, 1)
    r, g, b = mpl.colors.hsv_to_rgb((h, s, v))
    return r, g, b


def plot_overview(df, experiment_type, color="C0", title=None, target=TARGET,
                  alpha_path=0.2, zorder_path=0, 
                  alpha_point=0.5, zorder_point=1,
                  xlabel="$x$ (m)", ylabel="$y$ (m)"):
    df_ex = df[df.experiment_type == experiment_type]
    df_arr = df_ex[df_ex.arrived == 1]
    if title is None:
        title = df_ex.experiment.iloc[0]
    for run in set(df_ex.total_ordering):
        df_run = df_ex[df_ex.total_ordering == run]
        plt.plot(df_run.xn, df_run.yn, alpha=alpha_path, color=color,
                 zorder=zorder_path)
    plt.scatter(df_arr.xn, df_arr.yn, alpha=alpha_point, color=color,
                zorder=zorder_point)
    plot_targets(show_start=True, show_final=False, target_coords=[target])
    plt.axis("equal")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)


def plot_by_distance(df, experiment_type, cmap="C0", target=TARGET,
                     alpha_point=0.5, zorder_point=1, crosshair=False,
                     xlabel="$x$ (m)", ylabel="$y$ (m)"):
    df_ex = df[df.experiment_type == experiment_type]
    df_arr = df_ex[df_ex.arrived == 1]
    plt.scatter(df_arr.xn, df_arr.yn,
                c=df_arr.distance, cmap=cmap)
    plt.colorbar(label="distance (m)")
    plt.clim(df[df.arrived==1].distance.min(), df[df.arrived==1].distance.max())
    plot_targets(show_start=False, show_final=False, target_coords=[TARGET],
                 crosshair=crosshair)
    plt.axis("equal")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)


def plot_detailed(df, experiment_type, color="C0", title=None, target=TARGET,
                  alpha_point=0.5, zorder_point=1, crosshair=False,
                  xlabel="$x$ (m)", ylabel="$y$ (m)"):
    df_ex = df[df.experiment_type == experiment_type]
    df_arr = df_ex[df_ex.arrived == 1]
    if title is None:
        title = df_ex.experiment.iloc[0]
    for order in np.arange(1, df.order.max()+1):
        df_run = df_arr[df_arr.order==order]
        plt.scatter(df_run.xn, df_run.yn,
                    label=f"Run {order}",
                    color=change_color(color, value=-50+25*(order-1)))
    plot_targets(show_start=False, show_final=False, target_coords=[TARGET],
                 crosshair=crosshair)
    plt.title(title)
    plt.axis("equal")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()


def plot_distribution(df, experiment_type, color="C0", title=None,
                      target_color="C2", background_shade=-50, crosshair=False):
    df_ex = df[df.experiment_type == experiment_type]
    df_arr = df_ex[df_ex.arrived == 1]
    if title is None:
        title = df_ex.experiment.iloc[0]
    g = sns.jointplot(df_arr.xn, df_arr.yn, kind="kde", size=7, space=0,
                      color=color)
    g.plot_marginals(sns.rugplot, height=0.1, color=color)
    g.ax_joint.get_children()[0].set_zorder(-1)
    for child in g.ax_joint.get_children()[1:]:
        if isinstance(child, mpl.collections.PathCollection):
            child.set_alpha(0.8)
    plt.sca(g.ax_joint)
    plot_targets(show_start=False, show_final=False, target_coords=[TARGET],
                 target_color=target_color, zorder=0, crosshair=crosshair)
    g.set_axis_labels("$x$", "$y$")
    plt.axis("equal")

    xmin, xmax = plt.xlim()
    ymin, ymax = plt.ylim()
    xsize = xmax - xmin
    ysize = ymax - ymin

    if xsize > ysize:
        ymin -= (xsize - ysize) / 2
        ymax += (xsize - ysize) / 2
        ysize = xsize
    else:
        xmin -= (ysize - xsize) / 2
        xmax += (ysize - xsize) / 2
        xsize = ysize

    plt.gca().add_patch(mpl.patches.Rectangle(
        (xmin, ymin), xsize, ysize, 
        color=change_color(color, saturation=background_shade),
        zorder=-1))
    g.fig.suptitle(title)


def plot_targets(p_init=Coords(0, 0), p_final=Coords(0, 0),
                 invert_x=False, invert_y=False,
                 target_coords=None, target_coord_offsets=None,
                 target_color="C2", target_size=Coords(0.525, 0.37),
                 show_start=True, show_final=True,
                 scale=100, zorder=0, crosshair=False, background_shade=-50):
    if target_coords is not None and target_coord_offsets is not None:
        raise ValueError("Use either target_coords or target_coord_offsets")
    
    ax = plt.gca()
    
    if target_coords is None:
        if target_coord_offsets is None:
            target_coord_offsets = TARGET_COORD_OFFSETS
        target_coords = [Coords(p_init.x - offset.x, p_init.y - offset.y)
                         for offset in target_coord_offsets]
    
    if show_start:
        plt.scatter(-p_init.x, -p_init.y, marker=(5, 0), s=100, c="g")
    for coord in target_coords:
        if crosshair:
            plt.axhline(coord.y,
                        color=change_color(target_color,
                                           value=background_shade/2),
                        zorder=zorder)
            plt.axvline(coord.x,
                        color=change_color(target_color,
                                           value=background_shade/2),
                        zorder=zorder)
        ax.add_patch(mpl.patches.Rectangle(
            (coord.x * (-1 if invert_x else 1) - target_size.x / 2,
             coord.y * (-1 if invert_y else 1) - target_size.y / 2),
            target_size.x,
            target_size.y,
            color=target_color,
            zorder=zorder))
    if show_final:
        plt.scatter(p_final.x * (-1 if invert_x else 1),
                    p_final.y * (-1 if invert_y else 1),
                    marker=(3, 0), s=scale, c="r")


def distance(df, target):
        return np.sqrt((df.xn - target.x)**2 + (df.yn - target.y)**2)


def usable_filenames():
    filenames = sorted([filename for filename in glob.glob("csv/*.csv")
                        if "user-99" not in filename])
    
    for filename in filenames:
        if filename_regex.search(filename):
            df = pd.read_csv(filename, parse_dates=["time"])
        else:
            continue
        if any(df.arrived):
            yield filename


def extract_run_data(filename):
    data = filename_regex.findall(filename)[0]
    return RunData(ExperimentType(int(data[0])), int(data[1]), int(data[2]))


def analyze_data():
    print("Loading files...")
    analyses = pd.DataFrame(columns="user experiment_type run "
                                    "dist_err x_err y_err "
                                    "dist_std x_std y_std "
                                    "rms rms_x rms_y "
                                    "idx_start idx_end t_start t_end duration "
                                    "path_length "
                                    "move_l move_r move_x "
                                    "move_b move_f move_y".split())
    
    records = []
    
    for i, filename in enumerate(usable_filenames()):
        df = pd.read_csv(filename, parse_dates=["time"])
        data = extract_run_data(filename)
        df.xn *= -1
        df.yn *= -1
        
        df["experiment_type"] = data.experiment
        df["user"] = data.user
        df["run"] = data.run
        records.append(df)
        
        found = df[df.arrived == 1]

        distances = distance(found, TARGET)
        dist_err = distances.mean()
        dist_std = distances.std()

        dx = found.xn - TARGET.x
        x_err = dx.mean()
        x_std = dx.std()

        dy = found.yn - TARGET.y
        y_err = dy.mean()
        y_std = dy.std()

        rms = np.sqrt(np.mean(((found.xn - TARGET.x)**2
                               + (found.yn - TARGET.y)**2)))
        rms_x = np.sqrt(np.mean((dx)**2))
        rms_y = np.sqrt(np.mean((dy)**2))
        
        t_start = df[df.z > 0.25].time.iloc[0]
        t_end = found.time.iloc[0]
        duration = (t_end - t_start).total_seconds()

        idx_start = df[df.time==t_start].index[0]
        idx_end = df[df.time==t_end].index[0]

        df_running = df[["xn", "yn"]].iloc[idx_start:idx_end+1]
        points = np.array(df_running)
        lengths = np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1))
        path = lengths.sum()

        diff_x = np.diff(points[:, 0])
        move_l = np.abs(np.sum(diff_x[diff_x > 0]))
        move_r = np.abs(np.sum(diff_x[diff_x < 0]))
        move_x = move_l + move_r

        diff_y = np.diff(points[:, 1])
        move_b = np.abs(np.sum(diff_y[diff_y > 0]))
        move_f = np.abs(np.sum(diff_y[diff_y < 0]))
        move_y = move_b + move_f

        analyses.loc[i] = [
            data.user, data.experiment, data.run,
            dist_err, x_err, y_err,
            dist_std, x_std, y_std,
            rms, rms_x, rms_y,
            idx_start, idx_end, t_start, t_end, duration,
            path,
            move_x, move_l, move_r,
            move_y, move_b, move_f,
        ]
        
    results = pd.concat(records, ignore_index=True)

    analyses["group"] = (analyses.user % 2).astype(int)
    analyses["start"] = [ExperimentType(e % 2 + 1) for e in analyses.user]
    analyses["experiment_int"] = [e.value for e in analyses.experiment_type]
    analyses["experiment"] = [e.name for e in analyses.experiment_type]
    analyses.experiment.replace("Spirit", "SPIRIT", inplace=True)

    results["group"] = (results.user % 2).astype(int)
    results["start"] = [ExperimentType(e % 2 + 1) for e in results.user]
    results["experiment_int"] = [e.value for e in results.experiment_type]
    results["experiment"] = [e.name for e in results.experiment_type]
    results.experiment.replace("Spirit", "SPIRIT", inplace=True)
    results.distance = distance(results, TARGET)
    results.dx = results.xn - TARGET.x
    results.dy = results.yn - TARGET.y
    results["total_ordering"] = (
        (results.run.diff(1) != 0)
        | (results.experiment_int.diff(1) != 0)
        | (results.user.diff(1) != 0)
    ).astype('int').cumsum() - 1

    for user in set(analyses.user):
        df = analyses[analyses.user == user].sort_values(
            by="experiment_int", ascending=np.all(analyses[analyses.user==user]
                                             .start==ExperimentType.Onboard))
        df["order"] = range(1, len(df) + 1)
        for idx in df.index:
            analyses.loc[idx, "order"] = int(df.loc[idx, "order"])
            results.loc[results.total_ordering==idx,
                        "order"] = int(df.loc[idx, "order"])

    for col in ["user", "run", "group", "order"]:
        analyses[col] = analyses[col].astype(int)
    for col in ["arrived", "order"]:
        results[col] = results[col].astype(int)

    return results, analyses


def load_surveys():
    with open("data.pickle", "rb") as fin:
        data = pickle.load(fin)
    users = _load_users(data)
    tlx = _load_tlx(data)
    surveys = _load_surveys(data, tlx)
    return users, tlx, surveys


def _load_users(data):
    users = pd.DataFrame({"user_id": user.id_, "name": user.name,
                          "age": user.age, "teleop": user.teleop,
                          "flying": user.flying} for user in data)


def _parse_tlx_component(component):
    return TlxResponse(component.code, component.score, component.weight,
                       component.weighted_score)


def _load_tlx(data):
    tlx_data = []
    for user in data:
        for experiment in user.experiments:
            d = {"user": user.id_, "experiment_type": experiment.type_}
            for component in experiment.tlx.components.values():
                parsed = _parse_tlx_component(component)
                d[parsed.code] = parsed.score
            tlx_data.append(d)
    tlx = pd.DataFrame(tlx_data)
    tlx["group"] = tlx.user % 2
    tlx["tlx"] = tlx.mental + tlx.physical + tlx.temporal + tlx.performance + tlx.effort + tlx.frustration
    tlx["order"] = [1, 2]*(len(tlx)//2)
    tlx["experiment_int"] = [e.value for e in tlx.experiment_type]
    tlx["experiment"] = [e.name for e in tlx.experiment_type]
    tlx.experiment.replace("Spirit", "SPIRIT", inplace=True)
    return tlx


def _load_surveys(data, tlx):
    survey_data = []

    for user in data:
        for experiment in user.experiments:
            d = {"user": user.id_, "experiment_type": experiment.type_}
            d.update({i.code:i.score for i in experiment.survey.questions.values()})
            survey_data.append(d)

    surveys = pd.DataFrame(survey_data)
    surveys["group"] = tlx.user % 2
    surveys["order"] = [1, 2]*(len(surveys)//2)
    surveys["experiment"] = [e.name for e in surveys.experiment_type]
    surveys["experiment_int"] = [e.value for e in surveys.experiment_type]
    surveys.experiment.replace("Spirit", "SPIRIT", inplace=True)
    return surveys


def best(sample1, sample2, σ_range, exponential_m, n_iter=2000, n_jobs=2):
    y1 = np.array(sample1)
    y2 = np.array(sample2)
    y = pd.DataFrame(dict(value=np.r_[y1, y2],
                          group=np.r_[["onboard"]*len(sample1),
                                      ["spirit"]*len(sample2)]))
    μ_m = y.value.mean()
    μ_s = y.value.std() * 2

    with pm.Model() as model:
        group1_mean = pm.Normal("group1_mean", μ_m, sd=μ_s)
        group2_mean = pm.Normal("group2_mean", μ_m, sd=μ_s)
        σ_low, σ_high = σ_range
        group1_std = pm.Uniform("group1_std", lower=σ_low, upper=σ_high)
        group2_std = pm.Uniform("group2_std", lower=σ_low, upper=σ_high)
        ν = pm.Exponential("ν_minus_one", abs(1/(exponential_m-1))) + 1    
        
        λ1 = group1_std**-2
        λ2 = group2_std**-2

        group1 = pm.StudentT("onboard",
                             nu=ν, mu=group1_mean, lam=λ1, observed=y1)
        group2 = pm.StudentT("spirit",
                             nu=ν, mu=group2_mean, lam=λ2, observed=y2)
        
        diff_of_means = pm.Deterministic("difference of means",
                                         group1_mean - group2_mean)
        diff_of_stds = pm.Deterministic("difference of stds",
                                        group1_std - group2_std)
        effect_size = pm.Deterministic("effect size",
                                       diff_of_means / np.sqrt((group1_std**2
                                                                + group2_std**2)
                                                                / 2))
        trace = pm.sample(n_iter, init=None, njobs=n_jobs)
    return BestResult(trace, model)


def summarize(best_result, kde=True, plot=True):
    trace, model = best_result
    if plot:
        ax = pm.plot_posterior(trace[100:],
                               varnames=[r"group1_mean", r"group2_mean",
                                         r"group1_std", "group2_std",
                                         r"ν_minus_one"],
                               kde_plot=kde, color="C0")
        if kde:
            for a in (1, 3):
                ax[a].lines[0].set_color("C1")
        plt.figure()
        pm.plot_posterior(trace[1000:],
                          varnames=["difference of means", "difference of stds",
                                    "effect size"],
                          ref_val=0, kde_plot=True, color="C2")
        plt.figure()
        pm.forestplot(trace[1000:], varnames=[v.name for v in model.vars[:2]])
        plt.figure()
        pm.forestplot(trace[1000:], varnames=[v.name for v in model.vars[2:]])

    pm.summary(trace[1000:],
               varnames=["difference of means", "difference of stds",
                         "effect size"])


def analyze_differences(df, columns, params, n_iter=2000, n_jobs=2,
                        show_summaries=True, plot=False, save=True):
    traces = {}
    for column, param in zip(columns, params):
        print(f"Analyzing difference in {column}...")
        sample1 = df[df.experiment_type==ExperimentType.Onboard][column]
        sample2 = df[df.experiment_type==ExperimentType.Spirit][column]
        best_result = best(sample1, sample2, *param,
                           n_iter=n_iter, n_jobs=n_jobs)
        traces[column] = best_result
        if show_summaries:
            summarize(best_result, plot=plot)
        if save:
            with open(f"best_{column}.dat", "wb") as fout:
                pickle.dump(best_result, fout)
    return traces


def load_best_result(column):
    with open(f"best_{column}.dat", "rb") as fin:
        return pickle.load(fin)


if __name__ == "__main__":
    results, analyses = analyze_data()
    # analyze_differences(analyses, ["duration", "dist_err", "x_err", "y_err",
    #                                "rms_x", "rms_y"])
