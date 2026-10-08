#!/usr/bin/env python3
"""Evaluate partial monocular ORB-SLAM3 trajectories against Parking_02 GT.

Monocular trajectories are aligned with a metric Sim(3). Missing frames are
not interpolated. Large keyframe gaps are reported and the longest segment
with gaps <= 2 s is evaluated separately from all saved keyframes.
"""

from pathlib import Path
import csv
import re
import sqlite3

import numpy as np
from scipy.spatial.transform import Rotation, Slerp


ROOT = Path("/home/nvidia/drone/stage1_m2dgr_experiments")
GT_PATH = ROOT / "ground_truth/Parking_02/parking2.txt"
RESULT = ROOT / "results/Parking_02/orbslam3"
TRAJECTORIES = [
    RESULT / "KeyFrameTrajectory_TUM_Format.txt",
    RESULT / "KeyFrameTrajectory_TUM_Format_rate0.5.txt",
]


def sim3_align(source, target):
    source_mean = source.mean(axis=0)
    target_mean = target.mean(axis=0)
    x = source - source_mean
    y = target - target_mean
    covariance = x.T @ y / len(source)
    u, singular, vt = np.linalg.svd(covariance)
    correction = np.eye(3)
    if np.linalg.det(vt.T @ u.T) < 0:
        correction[-1, -1] = -1.0
    rotation = vt.T @ correction @ u.T
    variance = np.mean(np.sum(x * x, axis=1))
    scale = float(np.sum(singular * np.diag(correction)) / variance)
    translation = target_mean - scale * rotation @ source_mean
    return scale, rotation, translation


def apply_sim3(position, orientations, scale, rotation, translation):
    transformed_position = scale * (position @ rotation.T) + translation
    transformed_orientation = Rotation.from_matrix(
        np.asarray([rotation @ item.as_matrix() for item in orientations])
    )
    return transformed_position, transformed_orientation


def interp_positions(times, positions, query):
    return np.column_stack(
        [np.interp(query, times, positions[:, i]) for i in range(3)]
    )


def interp_orientations(times, orientations, query):
    return Slerp(times, orientations)(query)


def stats(values):
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        return {"count": 0, "rmse": float("nan"), "mean": float("nan"),
                "median": float("nan"), "max": float("nan")}
    return {
        "count": int(values.size),
        "rmse": float(np.sqrt(np.mean(values**2))),
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "max": float(np.max(values)),
    }


def segments(times, max_gap=2.0):
    boundaries = np.flatnonzero(np.diff(times) > max_gap) + 1
    return np.split(np.arange(times.size), boundaries)


def evaluate_segment(times, positions, orientations, gt_time, gt_pos, gt_rot,
                     indices):
    t = times[indices]
    p = positions[indices]
    r = Rotation.from_quat(orientations[indices])
    gt_p = interp_positions(gt_time, gt_pos, t)
    gt_r = interp_orientations(gt_time, gt_rot, t)

    scale, align_r, align_t = sim3_align(p, gt_p)
    aligned_p, aligned_r = apply_sim3(p, r, scale, align_r, align_t)
    ate_translation = np.linalg.norm(aligned_p - gt_p, axis=1)
    ate_rotation = np.degrees((gt_r.inv() * aligned_r).magnitude())

    rpe = {}
    rpe_rows = []
    for delta in (1.0, 5.0):
        translation_errors = []
        rotation_errors = []
        for i, start in enumerate(t):
            target = start + delta
            j = int(np.searchsorted(t, target))
            choices = [candidate for candidate in (j - 1, j)
                       if 0 <= candidate < t.size]
            if not choices:
                continue
            j = min(choices, key=lambda candidate: abs(t[candidate] - target))
            if abs(t[j] - target) > 0.15:
                continue
            est_delta = aligned_p[j] - aligned_p[i]
            gt_delta = gt_p[j] - gt_p[i]
            trans_error = float(np.linalg.norm(est_delta - gt_delta))
            est_relative = aligned_r[i].inv() * aligned_r[j]
            gt_relative = gt_r[i].inv() * gt_r[j]
            rot_error = float(np.degrees(
                (gt_relative.inv() * est_relative).magnitude()
            ))
            translation_errors.append(trans_error)
            rotation_errors.append(rot_error)
            rpe_rows.append([
                f"{start:.9f}", f"{t[j]:.9f}", f"{delta:.3f}",
                f"{trans_error:.9f}", f"{rot_error:.9f}",
            ])
        rpe[delta] = {
            "translation_m": stats(translation_errors),
            "rotation_deg": stats(rotation_errors),
        }

    return {
        "count": int(indices.size),
        "start": float(t[0]),
        "end": float(t[-1]),
        "span": float(t[-1] - t[0]),
        "scale": float(scale),
        "ate_translation_m": stats(ate_translation),
        "ate_rotation_deg": stats(ate_rotation),
        "rpe": rpe,
        "aligned": (t, gt_p, aligned_p, ate_translation, ate_rotation),
        "rpe_rows": rpe_rows,
    }


def write_stats(handle, title, value):
    handle.write(f"\n{title}\n")
    for key, item in value.items():
        if isinstance(item, dict):
            write_stats(handle, f"{title}.{key}", item)
        elif isinstance(item, float):
            handle.write(f"{key}: {item:.9f}\n")
        else:
            handle.write(f"{key}: {item}\n")


def main():
    RESULT.mkdir(parents=True, exist_ok=True)
    gt = np.loadtxt(GT_PATH)
    gt_time = gt[:, 0]
    gt_pos = gt[:, 1:4]
    gt_rot = Rotation.from_quat(gt[:, 4:8])

    image_db = ROOT / "bags/Parking_02/parking2_ros2/parking2_ros2.db3"
    with sqlite3.connect(image_db) as conn:
        image_min, image_max, image_count = conn.execute(
            """
            SELECT MIN(m.timestamp), MAX(m.timestamp), COUNT(*)
            FROM messages AS m JOIN topics AS t ON t.id = m.topic_id
            WHERE t.name = '/camera/color/image_raw'
            """
        ).fetchone()
    image_min = image_min / 1e9
    image_max = image_max / 1e9

    summary_path = RESULT / "metrics_orbslam3.txt"
    csv_path = RESULT / "ate_aligned_trajectory_rate0.5.csv"
    rpe_path = RESULT / "rpe_pairs_rate0.5.csv"
    with summary_path.open("w") as summary:
        summary.write("Parking_02 ORB-SLAM3 partial Sim(3) evaluation\n")
        summary.write("===============================================\n")
        summary.write(f"ground_truth: {GT_PATH}\n")
        summary.write(f"image_count: {image_count}\n")
        summary.write(f"image_time_range: {image_min:.9f} .. {image_max:.9f}\n")
        summary.write(f"image_duration_s: {image_max - image_min:.9f}\n")
        summary.write("No missing frames were interpolated.\n")
        summary.write("Segment threshold: keyframe gap <= 2.0 s.\n")

        for trajectory_path in TRAJECTORIES:
            data = np.loadtxt(trajectory_path)
            if data.ndim == 1:
                data = data[None, :]
            valid = (data[:, 0] >= gt_time[0]) & (data[:, 0] <= gt_time[-1])
            data = data[valid]
            times = data[:, 0]
            positions = data[:, 1:4]
            quaternions = data[:, 4:8]
            trajectory_segments = segments(times)
            longest = max(trajectory_segments, key=len)
            all_indices = np.arange(times.size)
            all_eval = evaluate_segment(
                times, positions, quaternions, gt_time, gt_pos, gt_rot,
                all_indices,
            )
            longest_eval = evaluate_segment(
                times, positions, quaternions, gt_time, gt_pos, gt_rot,
                longest,
            )
            coverage = (
                (times[-1] - times[0]) / (image_max - image_min) * 100.0
            )
            summary.write(f"\n\nTrajectory: {trajectory_path.name}\n")
            summary.write(f"keyframes: {times.size}\n")
            summary.write(f"keyframe_start: {times[0]:.9f}\n")
            summary.write(f"keyframe_end: {times[-1]:.9f}\n")
            summary.write(f"keyframe_span_s: {times[-1] - times[0]:.9f}\n")
            summary.write(f"bag_time_coverage_percent: {coverage:.6f}\n")
            summary.write(f"segment_count: {len(trajectory_segments)}\n")
            summary.write(f"largest_gap_s: {np.max(np.diff(times)):.9f}\n")
            summary.write(f"longest_segment_keyframes: {len(longest)}\n")
            write_stats(summary, "all_saved_keyframes", {
                "ATE_translation_m": all_eval["ate_translation_m"],
                "ATE_rotation_deg": all_eval["ate_rotation_deg"],
                "RPE": all_eval["rpe"],
                "sim3_scale": all_eval["scale"],
            })
            write_stats(summary, "longest_continuous_segment", {
                "ATE_translation_m": longest_eval["ate_translation_m"],
                "ATE_rotation_deg": longest_eval["ate_rotation_deg"],
                "RPE": longest_eval["rpe"],
                "sim3_scale": longest_eval["scale"],
            })

            if trajectory_path.name.endswith("rate0.5.txt"):
                t, gt_p, est_p, ate_t, ate_r = all_eval["aligned"]
                with csv_path.open("w", newline="") as handle:
                    writer = csv.writer(handle)
                    writer.writerow([
                        "timestamp", "gt_x", "gt_y", "gt_z",
                        "est_aligned_x", "est_aligned_y", "est_aligned_z",
                        "position_error_m", "orientation_error_deg",
                    ])
                    for row in zip(t, gt_p, est_p, ate_t, ate_r):
                        timestamp, gt_xyz, est_xyz, pos_err, rot_err = row
                        writer.writerow([
                            f"{timestamp:.9f}", *[f"{x:.9f}" for x in gt_xyz],
                            *[f"{x:.9f}" for x in est_xyz],
                            f"{pos_err:.9f}", f"{rot_err:.9f}",
                        ])
                with rpe_path.open("w", newline="") as handle:
                    writer = csv.writer(handle)
                    writer.writerow([
                        "start_timestamp", "matched_end_timestamp",
                        "delta_s", "translation_error_m", "rotation_error_deg",
                    ])
                    writer.writerows(all_eval["rpe_rows"])

        direct_log = (RESULT / "orbslam3_direct_run.log").read_text(
            errors="replace")
        slow_log = (RESULT / "orbslam3_rate0.5_run.log").read_text(
            errors="replace")
        summary.write("\n\nStability diagnostics\n")
        for name, text in (("real_time", direct_log), ("rate_0.5", slow_log)):
            summary.write(f"{name}.local_map_failures: "
                          f"{len(re.findall(r'Fail to track local map!', text))}\n")
            summary.write(f"{name}.lost_frame_reports: "
                          f"{len(re.findall(r'Frames set to lost', text))}\n")
            summary.write(f"{name}.new_maps: "
                          f"{len(re.findall(r'New Map created', text))}\n")
            summary.write(f"{name}.map_reset_mentions: "
                          f"{len(re.findall(r'Reseting active map|Reseting active map', text))}\n")

    print(summary_path.read_text())
    print(f"wrote: {csv_path}")
    print(f"wrote: {rpe_path}")


if __name__ == "__main__":
    main()
