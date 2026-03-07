#!/usr/bin/env python3
"""Create animated GIFs from git history of a tracked image."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps


def run_git(args: list[str]) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def resolve_repo_file(repo_file: str) -> str:
    candidates = [repo_file]
    normalized = repo_file.lstrip("/")
    if normalized.startswith("skateway_data"):
        candidates.append(normalized[len("skateway_data") :].lstrip("/"))
    if "skateway_dataskateway_status_map.png" in normalized:
        candidates.append("skateway_status_map.png")

    for candidate in candidates:
        if not candidate:
            continue
        tracked = run_git(["ls-files", "--", candidate])
        if tracked:
            return candidate
    raise FileNotFoundError(f"Could not find a tracked file for: {repo_file}")


def load_frames(file_path: str) -> list[Image.Image]:
    commit_ids = run_git(["rev-list", "--reverse", "HEAD", "--", file_path]).splitlines()
    if not commit_ids:
        raise RuntimeError(f"No git history found for {file_path}")

    frames: list[Image.Image] = []
    seen = set()
    first_size = None

    for commit_id in commit_ids:
        blob = subprocess.run(
            ["git", "show", f"{commit_id}:{file_path}"],
            check=True,
            capture_output=True,
        ).stdout
        digest = hashlib.sha256(blob).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)

        with Image.open(BytesIO(blob)) as img:
            rgba = img.convert("RGBA")
            if first_size is None:
                first_size = rgba.size
            elif rgba.size != first_size:
                rgba = ImageOps.pad(rgba, first_size)
            frames.append(rgba.copy())

    if not frames:
        raise RuntimeError(f"No unique frames extracted for {file_path}")
    return frames


def save_gif(frames: list[Image.Image], seconds: int, out_path: Path) -> None:
    ms_per_frame = max(20, int((seconds * 1000) / len(frames)))
    palette_frames = [frame.convert("P", palette=Image.ADAPTIVE) for frame in frames]
    palette_frames[0].save(
        out_path,
        save_all=True,
        append_images=palette_frames[1:],
        duration=ms_per_frame,
        loop=0,
        optimize=False,
        disposal=2,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file",
        default="skateway_status_map.png",
        help="Path to image in git history (default: skateway_status_map.png)",
    )
    parser.add_argument(
        "--durations",
        nargs="+",
        type=int,
        default=[15, 60],
        help="GIF lengths in seconds (default: 15 60)",
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Directory for GIF outputs (default: current directory)",
    )
    args = parser.parse_args()

    file_path = resolve_repo_file(args.file)
    frames = load_frames(file_path)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(file_path).stem
    for seconds in args.durations:
        out_path = out_dir / f"{stem}_history_{seconds}s.gif"
        save_gif(frames, seconds, out_path)
        print(f"Created {out_path} with {len(frames)} frames over {seconds} seconds")


if __name__ == "__main__":
    main()
