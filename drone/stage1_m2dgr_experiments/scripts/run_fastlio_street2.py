#!/usr/bin/env python3
"""Run the Street_02 FAST-LIO2 experiment and collect its fixed-path outputs."""

from __future__ import annotations

import csv
import os
import shutil
import signal
import subprocess
import time
from datetime import datetime
from pathlib import Path


ROOT = Path("/home/nvidia/drone/stage1_m2dgr_experiments")
RESULT = ROOT / "results/Street_02/fastlio_default"
CONFIG = ROOT / "configs/fastlio_street2.yaml"
BAG = ROOT / "bags/Street_02/street2_ros2"
FASTLIO_SRC = Path("/home/nvidia/ros2_ws/src/fast_lio2")
FIXED_LOG = FASTLIO_SRC / "Log"


def run_logged(command: list[str], output: Path, env: dict[str, str]) -> subprocess.Popen:
    handle = output.open("w")
    process = subprocess.Popen(
        command,
        stdout=handle,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        env=env,
        start_new_session=True,
    )
    process._codex_log_handle = handle  # type: ignore[attr-defined]
    return process


def close_logged(process: subprocess.Popen) -> None:
    handle = getattr(process, "_codex_log_handle", None)
    if handle is not None:
        handle.close()


def fastlio_pid() -> int | None:
    result = subprocess.run(
        ["pgrep", "-x", "fastlio_mapping"],
        text=True,
        capture_output=True,
        check=False,
    )
    pids = [int(line) for line in result.stdout.split() if line.strip().isdigit()]
    return pids[0] if pids else None


def copy_fixed_outputs(destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("pos_log.txt", "fast_lio_time_log.csv", "mat_pre.txt", "mat_out.txt", "dbg.txt", "imu.txt"):
        source = FIXED_LOG / name
        if source.exists():
            shutil.copy2(source, destination / name)


def main() -> int:
    RESULT.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    attempt = RESULT / f"run_{run_id}"
    attempt.mkdir(parents=True, exist_ok=True)
    fixed_copy = attempt / "fastlio_logs"
    resource_file = attempt / "resource_samples.csv"
    shutil.copy2(CONFIG, attempt / "config_used.yaml")

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["ROS_DOMAIN_ID"] = env.get("ROS_DOMAIN_ID", "0")

    # FAST-LIO2 writes runtime logs to this fixed source-tree directory.
    # Remove only stale timing output so it cannot be mistaken for this run.
    stale_timing = FIXED_LOG / "fast_lio_time_log.csv"
    if stale_timing.exists():
        stale_timing.unlink()

    launch = run_logged(
        [
            "ros2",
            "launch",
            "fast_lio",
            "mapping.launch.py",
            f"config_path:={CONFIG.parent}",
            "config_file:=fastlio_street2.yaml",
            "use_sim_time:=true",
            "rviz:=false",
        ],
        attempt / "run.log",
        env,
    )

    pid = None
    for _ in range(60):
        pid = fastlio_pid()
        if pid is not None:
            break
        if launch.poll() is not None:
            break
        time.sleep(1)
    if pid is None:
        launch.terminate()
        launch.wait(timeout=10)
        close_logged(launch)
        raise RuntimeError("fastlio_mapping did not start; inspect run.log")

    with resource_file.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["wall_time", "pid", "cpu_percent", "rss_kb"])
        bag = run_logged(
            ["ros2", "bag", "play", str(BAG), "--clock"],
            attempt / "bag_play.log",
            env,
        )
        while bag.poll() is None:
            sample = subprocess.run(
                ["ps", "-p", str(pid), "-o", "%cpu=,rss="],
                text=True,
                capture_output=True,
                check=False,
            ).stdout.strip().split()
            if len(sample) == 2:
                writer.writerow([datetime.now().astimezone().isoformat(timespec="seconds"), pid, *sample])
                handle.flush()
            time.sleep(5)
        bag.wait()
        close_logged(bag)

    time.sleep(5)
    save = subprocess.run(
        ["ros2", "service", "call", "/map_save", "std_srvs/srv/Trigger", "{}"],
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    (attempt / "map_save.log").write_text(save.stdout + save.stderr)

    # Signal the mapping node first. Sending SIGINT to the whole launch
    # process group can terminate it before the node writes its timing CSV.
    mapping_pid = fastlio_pid()
    if mapping_pid is not None:
        os.kill(mapping_pid, signal.SIGINT)
        for _ in range(30):
            if fastlio_pid() is None:
                break
            time.sleep(1)

    os.kill(launch.pid, signal.SIGINT)
    try:
        launch.wait(timeout=30)
    except subprocess.TimeoutExpired:
        os.killpg(launch.pid, signal.SIGTERM)
        launch.wait(timeout=10)
    close_logged(launch)

    time.sleep(1)
    copy_fixed_outputs(fixed_copy)
    for name in ("pos_log.txt", "fast_lio_time_log.csv", "mat_pre.txt", "mat_out.txt", "dbg.txt", "imu.txt"):
        source = fixed_copy / name
        if source.exists():
            shutil.copy2(source, RESULT / name)
    map_path = RESULT / "map.pcd"
    if not map_path.exists():
        raise RuntimeError("map.pcd was not created; inspect map_save.log")
    if not (RESULT / "pos_log.txt").exists():
        raise RuntimeError("pos_log.txt was not collected")
    print(attempt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
