#!/usr/bin/env python3
"""Evaluate FAST-LIO2 Parking_02 against the supplied ground truth.

The FAST-LIO2 pos_log time is relative to the first LiDAR timestamp. The
absolute time base is therefore read from the converted ROS 2 bag database.
ATE uses metric SE(3) Umeyama alignment. RPE uses relative poses at 1 s and
5 s, with no additional per-interval alignment.
"""

from pathlib import Path
import csv
import sqlite3

import numpy as np
from scipy.spatial.transform import Rotation, Slerp


ROOT = Path("/home/nvidia/drone/stage1_m2dgr_experiments")
TRUTH_FILE = ROOT / "ground_truth/Parking_02/parking2.txt"
EST_FILE = ROOT / "results/Parking_02/fastlio_filter03/fastlio_logs/pos_log.txt"
BAG_DB = ROOT / "bags/Parking_02/parking2_ros2/parking2_ros2.db3"
OUT_DIR = ROOT / "results/Parking_02/fastlio_filter03/metrics"


def first_lidar_timestamp_ns(db_path: Path) -> int:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT MIN(m.timestamp)
            FROM messages AS m
            JOIN topics AS t ON t.id = m.topic_id
            WHERE t.name = '/rslidar_points'
            """
        ).fetchone()
    if row[0] is None:
        raise RuntimeError("No /rslidar_points messages found in the ROS 2 bag")
    return int(row[0])


def umeyama_se3(source: np.ndarray, target: np.ndarray):
    source_centroid = source.mean(axis=0)
    target_centroid = target.mean(axis=0)
    x = source - source_centroid
    y = target - target_centroid
    u, _, vt = np.linalg.svd(x.T @ y)
    correction = np.eye(3)
    if np.linalg.det(vt.T @ u.T) < 0:
        correction[-1, -1] = -1.0
    rotation = vt.T @ correction @ u.T
    translation = target_centroid - rotation @ source_centroid
    return rotation, translation


def interp_vector(times, values, query):
    return np.column_stack(
        [np.interp(query, times, values[:, i]) for i in range(values.shape[1])]
    )


def interp_rotations(times, quaternions_xyzw, query):
    return Slerp(times, Rotation.from_quat(quaternions_xyzw))(query)


def summarize(values):
    values = np.asarray(values)
    return {
        "count": int(values.size),
        "rmse": float(np.sqrt(np.mean(values**2))),
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "max": float(np.max(values)),
    }


def write_csv(path, header, rows):
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    truth = np.loadtxt(TRUTH_FILE)
    estimate = np.loadtxt(EST_FILE)
    if truth.shape[1] < 8:
        raise RuntimeError("Ground truth must contain timestamp, xyz, and xyzw")
    if estimate.shape[1] < 7:
        raise RuntimeError("FAST-LIO pos_log must contain time, Euler angles, xyz")

    truth_time = truth[:, 0]
    truth_pos = truth[:, 1:4]
    truth_rot = Rotation.from_quat(truth[:, 4:8])

    lidar_time_ns = first_lidar_timestamp_ns(BAG_DB)
    time_base = lidar_time_ns * 1e-9
    estimate_time = time_base + estimate[:, 0]
    estimate_pos = estimate[:, 4:7]
    estimate_rot = Rotation.from_euler("xyz", estimate[:, 1:4], degrees=True)

    valid = (
        (estimate_time >= truth_time[0])
        & (estimate_time <= truth_time[-1])
    )
    estimate_time = estimate_time[valid]
    estimate_pos = estimate_pos[valid]
    estimate_rot = Rotation.concatenate(
        [estimate_rot[i] for i in np.flatnonzero(valid)]
    )
    truth_at_est = interp_vector(truth_time, truth_pos, estimate_time)
    truth_rot_at_est = interp_rotations(
        truth_time, truth_rot.as_quat(), estimate_time
    )

    align_r, align_t = umeyama_se3(estimate_pos, truth_at_est)
    aligned_pos = estimate_pos @ align_r.T + align_t
    position_errors = np.linalg.norm(aligned_pos - truth_at_est, axis=1)

    aligned_rot = Rotation.from_matrix(
        np.asarray([align_r @ r.as_matrix() for r in estimate_rot])
    )
    orientation_errors = (
        truth_rot_at_est.inv() * aligned_rot
    ).magnitude()

    rows = []
    for i in range(estimate_time.size):
        rows.append(
            [
                f"{estimate_time[i]:.9f}",
                *[f"{x:.9f}" for x in truth_at_est[i]],
                *[f"{x:.9f}" for x in aligned_pos[i]],
                f"{position_errors[i]:.9f}",
                f"{np.degrees(orientation_errors[i]):.9f}",
            ]
        )
    write_csv(
        OUT_DIR / "ate_aligned_trajectory.csv",
        [
            "timestamp",
            "gt_x",
            "gt_y",
            "gt_z",
            "est_aligned_x",
            "est_aligned_y",
            "est_aligned_z",
            "position_error_m",
            "orientation_error_deg",
        ],
        rows,
    )

    rpe_rows = []
    rpe_summary = {}
    for delta in (1.0, 5.0):
        trans_errors = []
        rot_errors = []
        used = []
        for i, current_time in enumerate(estimate_time):
            target_time = current_time + delta
            j = int(np.searchsorted(estimate_time, target_time))
            candidates = [j - 1, j]
            candidates = [k for k in candidates if 0 <= k < estimate_time.size]
            if not candidates:
                continue
            j = min(candidates, key=lambda k: abs(estimate_time[k] - target_time))
            if abs(estimate_time[j] - target_time) > 0.15:
                continue

            est_delta = aligned_pos[j] - aligned_pos[i]
            gt_delta = truth_at_est[j] - truth_at_est[i]
            trans_errors.append(float(np.linalg.norm(est_delta - gt_delta)))

            est_rel = aligned_rot[i].inv() * aligned_rot[j]
            gt_rel = truth_rot_at_est[i].inv() * truth_rot_at_est[j]
            rot_errors.append(float(np.degrees((gt_rel.inv() * est_rel).magnitude())))
            used.append(
                [
                    f"{current_time:.9f}",
                    f"{estimate_time[j]:.9f}",
                    f"{delta:.3f}",
                    f"{trans_errors[-1]:.9f}",
                    f"{rot_errors[-1]:.9f}",
                ]
            )

        trans_stats = summarize(trans_errors)
        rot_stats = summarize(rot_errors)
        rpe_summary[f"{delta:g}s"] = {
            "translation_m": trans_stats,
            "rotation_deg": rot_stats,
        }
        rpe_rows.extend(used)

    write_csv(
        OUT_DIR / "rpe_pairs.csv",
        [
            "start_timestamp",
            "matched_end_timestamp",
            "requested_delta_s",
            "translation_error_m",
            "rotation_error_deg",
        ],
        rpe_rows,
    )

    ate_stats = summarize(position_errors)
    orientation_stats = summarize(np.degrees(orientation_errors))
    with (OUT_DIR / "metrics.txt").open("w") as handle:
        handle.write("Parking_02 FAST-LIO2 ATE/RPE evaluation\n")
        handle.write("========================================\n")
        handle.write(f"ground_truth: {TRUTH_FILE}\n")
        handle.write(f"estimate: {EST_FILE}\n")
        handle.write(f"bag_first_lidar_timestamp_ns: {lidar_time_ns}\n")
        handle.write(f"time_base_seconds: {time_base:.9f}\n")
        handle.write(f"matched_pose_count: {estimate_time.size}\n")
        handle.write(f"ground_truth_time_range: {truth_time[0]:.9f} .. {truth_time[-1]:.9f}\n")
        handle.write(f"estimate_time_range: {estimate_time[0]:.9f} .. {estimate_time[-1]:.9f}\n")
        handle.write("\nATE position after SE(3) Umeyama alignment [m]\n")
        for key, value in ate_stats.items():
            handle.write(f"{key}: {value:.9f}\n" if key != "count" else f"{key}: {value}\n")
        handle.write("\nAbsolute orientation error after the same alignment [deg]\n")
        for key, value in orientation_stats.items():
            handle.write(f"{key}: {value:.9f}\n" if key != "count" else f"{key}: {value}\n")
        handle.write("\nRPE (no per-interval alignment)\n")
        for delta, values in rpe_summary.items():
            handle.write(f"\nDelta {delta}, translation [m]\n")
            for key, value in values["translation_m"].items():
                handle.write(f"{key}: {value:.9f}\n" if key != "count" else f"{key}: {value}\n")
            handle.write(f"Delta {delta}, rotation [deg]\n")
            for key, value in values["rotation_deg"].items():
                handle.write(f"{key}: {value:.9f}\n" if key != "count" else f"{key}: {value}\n")
        handle.write(
            "\nNote: The supplied ground truth and FAST-LIO pose convention may "
            "refer to different physical sensor frames. The reported ATE is "
            "therefore the standard trajectory-level SE(3)-aligned result; "
            "sensor-frame offset refinement was not applied.\n"
        )

    print((OUT_DIR / "metrics.txt").read_text())


if __name__ == "__main__":
    main()
