#!/usr/bin/env bash
set -Eeuo pipefail

# Upload only the approved project areas through a temporary Git worktree.
SOURCE_ROOT="/home/nvidia"
REPO_URL="https://github.com/CYYCCC001/lidar-visual-slam-graduation.git"
GITHUB_USER="CYYCCC001"

command -v git >/dev/null || {
    echo "ERROR: git is not installed." >&2
    exit 1
}

command -v rsync >/dev/null || {
    echo "ERROR: rsync is not installed." >&2
    exit 1
}

command -v git-lfs >/dev/null || {
    echo "ERROR: git-lfs is not installed. Run: sudo apt install -y git-lfs" >&2
    exit 1
}

read -r -s -p "GitHub Token (input hidden): " GITHUB_TOKEN
printf '\n'

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "ERROR: GitHub Token is empty." >&2
    exit 1
fi

ASKPASS="$(mktemp /tmp/lidar-slam-askpass.XXXXXX)"
WORK="$(mktemp -d /tmp/lidar-slam-upload.XXXXXX)"

cleanup() {
    unset GITHUB_TOKEN
    unset GIT_ASKPASS
    rm -f "$ASKPASS"
    rm -rf "$WORK"
}
trap cleanup EXIT

chmod 700 "$ASKPASS"

printf '%s\n' '#!/bin/sh' \
    'case "$1" in' \
    '  *Username*) printf "%s\n" "$GITHUB_USER" ;;' \
    '  *) printf "%s\n" "$GITHUB_TOKEN" ;;' \
    'esac' > "$ASKPASS"

export GITHUB_TOKEN
export GITHUB_USER
export GIT_ASKPASS="$ASKPASS"
export GIT_TERMINAL_PROMPT=0

REPO_DIR="$WORK/repo"

echo "Cloning the current GitHub repository into a temporary directory..."
git -c credential.helper= clone "$REPO_URL" "$REPO_DIR"
cd "$REPO_DIR"

if git rev-parse --verify HEAD >/dev/null 2>&1; then
    BRANCH="$(git branch --show-current)"
    [[ -n "$BRANCH" ]] || BRANCH="main"
else
    BRANCH="main"
    git checkout --orphan "$BRANCH"
fi

mkdir -p drone ros2_ws/src third_party

echo "Copying approved drone content..."
rsync -a \
    --exclude='bin/***' \
    --exclude='backup/***' \
    --exclude='camera/yolo/***' \
    --exclude='stage1_m2dgr_experiments/bags/***' \
    --exclude='**/.git/***' \
    --exclude='**/build/***' \
    --exclude='**/install/***' \
    --exclude='**/log/***' \
    --exclude='**/__pycache__/***' \
    --exclude='**/CMakeFiles/***' \
    --exclude='**/*.pyc' \
    --exclude='**/*.pyo' \
    --exclude='**/*.o' \
    --exclude='**/*.so' \
    --exclude='**/*.a' \
    --exclude='**/*.d' \
    --exclude='camera/orbslam3/ORB_SLAM3-master/lib/***' \
    --exclude='camera/orbslam3/ORB_SLAM3-master/Vocabulary/ORBvoc.txt' \
    --exclude='camera/orbslam3/ORB_SLAM3-master/Examples_old/***' \
    --exclude='stage1_m2dgr_experiments/results/Parking_02/fastlio_filter03/map.pcd' \
    --exclude='stage1_m2dgr_experiments/results/Parking_02/fastlio_default/map.pcd' \
    --exclude='stage1_m2dgr_experiments/results/Street_02/fastlio_default/map.pcd' \
    "$SOURCE_ROOT/drone/" \
    "$REPO_DIR/drone/"

echo "Copying selected YOLO model files..."
mkdir -p "$REPO_DIR/drone/camera/yolo/models"
cp "$SOURCE_ROOT/drone/camera/yolo/models/yolov8n.pt" \
    "$REPO_DIR/drone/camera/yolo/models/"
cp "$SOURCE_ROOT/drone/camera/yolo/models/yolov8n.onnx" \
    "$REPO_DIR/drone/camera/yolo/models/"
cp "$SOURCE_ROOT/drone/camera/yolo/models/yolov8n.engine" \
    "$REPO_DIR/drone/camera/yolo/models/"

echo "Copying selected runtime assets and upload scripts..."
mkdir -p \
    "$REPO_DIR/drone/bin" \
    "$REPO_DIR/drone/camera/orbslam3/ORB_SLAM3-master/Vocabulary" \
    "$REPO_DIR/drone/stage1_m2dgr_experiments/results/Parking_02/fastlio_filter03" \
    "$REPO_DIR/drone/stage1_m2dgr_experiments/results/Parking_02/fastlio_default" \
    "$REPO_DIR/drone/stage1_m2dgr_experiments/results/Street_02/fastlio_default"
rsync -a "$SOURCE_ROOT/drone/bin/" "$REPO_DIR/drone/bin/"
cp "$SOURCE_ROOT/drone/camera/orbslam3/ORB_SLAM3-master/Vocabulary/ORBvoc.txt" \
    "$REPO_DIR/drone/camera/orbslam3/ORB_SLAM3-master/Vocabulary/"
cp "$SOURCE_ROOT/drone/stage1_m2dgr_experiments/results/Parking_02/fastlio_filter03/map.pcd" \
    "$REPO_DIR/drone/stage1_m2dgr_experiments/results/Parking_02/fastlio_filter03/"
cp "$SOURCE_ROOT/drone/stage1_m2dgr_experiments/results/Parking_02/fastlio_default/map.pcd" \
    "$REPO_DIR/drone/stage1_m2dgr_experiments/results/Parking_02/fastlio_default/"
cp "$SOURCE_ROOT/drone/stage1_m2dgr_experiments/results/Street_02/fastlio_default/map.pcd" \
    "$REPO_DIR/drone/stage1_m2dgr_experiments/results/Street_02/fastlio_default/"

echo "Copying ROS 2 source packages..."
rsync -a \
    --exclude='**/.git/***' \
    --exclude='**/build/***' \
    --exclude='**/install/***' \
    --exclude='**/log/***' \
    --exclude='**/__pycache__/***' \
    --exclude='**/CMakeFiles/***' \
    --exclude='**/*.pyc' \
    --exclude='**/*.pyo' \
    --exclude='**/*.o' \
    --exclude='**/*.so' \
    --exclude='**/*.a' \
    --exclude='**/*.d' \
    "$SOURCE_ROOT/ros2_ws/src/" \
    "$REPO_DIR/ros2_ws/src/"

echo "Copying Livox SDK source..."
rsync -a \
    --exclude='**/.git/***' \
    --exclude='**/build/***' \
    --exclude='**/__pycache__/***' \
    --exclude='**/*.pyc' \
    --exclude='**/*.pyo' \
    --exclude='**/*.o' \
    --exclude='**/*.so' \
    --exclude='**/*.a' \
    --exclude='**/*.d' \
    "$SOURCE_ROOT/third_party/Livox-SDK2/" \
    "$REPO_DIR/third_party/Livox-SDK2/"

touch "$REPO_DIR/.gitignore"

if ! grep -qF '# lidar-visual-slam upload exclusions' "$REPO_DIR/.gitignore"; then
    printf '%s\n' \
        '' \
        '# lidar-visual-slam upload exclusions' \
        '**/__pycache__/' \
        '*.pyc' \
        '*.pyo' \
        '*.o' \
        '*.so' \
        '*.a' \
        '*.d' \
        '**/build/' \
        '**/install/' \
        '**/CMakeFiles/' \
        '**/log/' \
        '**/.git/' \
        'drone/bin/' \
        'drone/backup/' \
        'drone/camera/yolo/' \
        'drone/stage1_m2dgr_experiments/bags/' \
        'drone/camera/orbslam3/ORB_SLAM3-master/Vocabulary/ORBvoc.txt' \
        'drone/stage1_m2dgr_experiments/results/Parking_02/fastlio_filter03/map.pcd' \
        'drone/stage1_m2dgr_experiments/results/Parking_02/fastlio_default/map.pcd' \
        'drone/stage1_m2dgr_experiments/results/Street_02/fastlio_default/map.pcd' \
        >> "$REPO_DIR/.gitignore"
fi

git lfs install --local
git lfs track \
    "drone/camera/orbslam3/ORB_SLAM3-master/Vocabulary/ORBvoc.txt" \
    "drone/stage1_m2dgr_experiments/results/Parking_02/fastlio_filter03/map.pcd" \
    "drone/stage1_m2dgr_experiments/results/Parking_02/fastlio_default/map.pcd" \
    "drone/stage1_m2dgr_experiments/results/Street_02/fastlio_default/map.pcd"

LARGE_FILES="$(find "$REPO_DIR" -path "$REPO_DIR/.git" -prune -o -type f -size +95M -print)"
while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    relative="${file#"$REPO_DIR"/}"
    case "$relative" in
        drone/camera/orbslam3/ORB_SLAM3-master/Vocabulary/ORBvoc.txt|\
        drone/stage1_m2dgr_experiments/results/Parking_02/fastlio_filter03/map.pcd|\
        drone/stage1_m2dgr_experiments/results/Parking_02/fastlio_default/map.pcd|\
        drone/stage1_m2dgr_experiments/results/Street_02/fastlio_default/map.pcd)
            ;;
        *)
            echo "ERROR: unexpected file above 95 MB; nothing will be committed:" >&2
            printf '%s\n' "$file" >&2
            exit 1
            ;;
    esac
done <<< "$LARGE_FILES"

if rg -n -i \
    --hidden \
    --glob '!**/.git/**' \
    --glob '!**/build/**' \
    --glob '!**/install/**' \
    --glob '!**/log/**' \
    '(ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|CUSTOM_CODEX_API_KEY=|BEGIN .*PRIVATE KEY)' \
    "$REPO_DIR"; then
    echo "ERROR: possible credential found; nothing will be committed." >&2
    exit 1
fi

git add -A
git add -f \
    drone/bin/ \
    drone/camera/yolo/models/yolov8n.pt \
    drone/camera/yolo/models/yolov8n.onnx \
    drone/camera/yolo/models/yolov8n.engine \
    drone/camera/orbslam3/ORB_SLAM3-master/Vocabulary/ORBvoc.txt \
    drone/stage1_m2dgr_experiments/results/Parking_02/fastlio_filter03/map.pcd \
    drone/stage1_m2dgr_experiments/results/Parking_02/fastlio_default/map.pcd \
    drone/stage1_m2dgr_experiments/results/Street_02/fastlio_default/map.pcd

echo
echo "========== Staged summary =========="
git diff --cached --stat
echo
echo "========== Git LFS files =========="
git lfs status
echo
echo "========== First staged paths =========="
git diff --cached --name-only | sed -n '1,160p'
echo
echo "Excluded from this upload:"
printf '%s\n' \
    '  drone/backup/' \
    '  YOLO source, virtual-environment, and build directories (only three model files are included)' \
    '  drone/stage1_m2dgr_experiments/bags/' \
    '  ros2_ws/build/' \
    '  ros2_ws/install/' \
    '  ros2_ws/log/' \
    '  third_party/Livox-SDK2/build/' \
    '  other generated binaries and files above 95 MB'
echo

read -r -p "Type PUSH to commit and push, or anything else to cancel: " CONFIRM
if [[ "$CONFIRM" != "PUSH" ]]; then
    echo "Cancelled. No commit or push was performed."
    exit 0
fi

git config user.name "CYYCCC001"
git config user.email "CYYCCC001@users.noreply.github.com"
git commit -m "Update lidar visual SLAM project"
git push -u origin "$BRANCH"

echo "Upload completed."
echo "Temporary worktree removed automatically."
