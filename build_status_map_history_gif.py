#!/usr/bin/env python3
"""
Create optimized animated GIFs and WebP animations from git history
of a tracked image file.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps, ImageChops, ImageStat


# -----------------------
# Git helpers
# -----------------------

def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def resolve_repo_file(repo_file: str) -> str:
    candidates = [repo_file]
    normalized = repo_file.lstrip("/")

    if normalized.startswith("skateway_data"):
        candidates.append(normalized[len("skateway_data"):].lstrip("/"))

    if "skateway_dataskateway_status_map.png" in normalized:
        candidates.append("skateway_status_map.png")

    for candidate in candidates:
        if not candidate:
            continue
        if run_git(["ls-files", "--", candidate]):
            return candidate

    raise FileNotFoundError(f"Could not find tracked file: {repo_file}")


# -----------------------
# Image processing
# -----------------------

MAX_WIDTH = 900        # 🔥 biggest size lever
PALETTE_COLORS = 128   # 64–128 recommended
SIMILARITY_THRESHOLD = 6.0


def downscale(img: Image.Image) -> Image.Image:
    if img.width <= MAX_WIDTH:
        return img
    scale = MAX_WIDTH / img.width
    new_size = (int(img.width * scale), int(img.height * scale))
    return img.resize(new_size, Image.LANCZOS)


def is_similar(a: Image.Image, b: Image.Image) -> bool:
    diff = ImageChops.difference(a, b)
    stat = ImageStat.Stat(diff)
    return sum(stat.mean) < SIMILARITY_THRESHOLD


def load_frames(file_path: str) -> list[Image.Image]:
    commit_ids = run_git(
        ["rev-list", "--reverse", "HEAD", "--", file_path]
    ).splitlines()

    if not commit_ids:
        raise RuntimeError(f"No git history for {file_path}")

    frames: list[Image.Image] = []
    seen_hashes = set()
    base_size = None

    for commit_id in commit_ids:
        blob = subprocess.run(
            ["git", "show", f"{commit_id}:{file_path}"],
            check=True,
            capture_output=True,
        ).stdout

        digest = hashlib.sha256(blob).hexdigest()
        if digest in seen_hashes:
            continue
        seen_hashes.add(digest)

        with Image.open(BytesIO(blob)) as img:
            rgba = img.convert("RGBA")
            rgba = downscale(rgba)

            if base_size is None:
                base_size = rgba.size
            elif rgba.size != base_size:
                rgba = ImageOps.pad(rgba, base_size)

            if frames and is_similar(rgba, frames[-1]):
                continue

            frames.append(rgba.copy())

    if not frames:
        raise RuntimeError("No usable frames extracted")

    return frames


# -----------------------
# GIF + WebP output
# -----------------------

def quantize_frames(frames: list[Image.Image]) -> list[Image.Image]:
    base = frames[0].convert(
        "P",
        palette=Image.ADAPTIVE,
        colors=PALETTE_COLORS,
        dither=Image.NONE,
    )

    palette = base.getpalette()
    out = [base]

    for frame in frames[1:]:
        q = frame.convert("RGB").quantize(
            palette=base,
            dither=Image.NONE,
        )
        out.append(q)

    return out


def save_gif(frames: list[Image.Image], seconds: int, out_path: Path) -> None:
    ms_per_frame = max(40, int((seconds * 1000) / len(frames)))
    q_frames = quantize_frames(frames)

    q_frames[0].save(
        out_path,
        save_all=True,
        append_images=q_frames[1:],
        duration=ms_per_frame,
        loop=0,
        optimize=True,
        disposal=1,
    )


def save_webp(frames: list[Image.Image], seconds: int, out_path: Path) -> None:
    ms_per_frame = max(40, int((seconds * 1000) / len(frames)))

    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=ms_per_frame,
        loop=0,
        format="WEBP",
        lossless=False,
        quality=75,
        method=6,
    )


# -----------------------
# Main
# -----------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file",
        default="skateway_status_map.png",
        help="Tracked image path in git",
    )
    parser.add_argument(
        "--durations",
        nargs="+",
        type=int,
        default=[15, 60],
        help="Animation lengths in seconds",
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory",
    )

    args = parser.parse_args()

    file_path = resolve_repo_file(args.file)
    frames = load_frames(file_path)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(file_path).stem

    for seconds in args.durations:
        gif_path = out_dir / f"{stem}_history_{seconds}s.gif"
        webp_path = out_dir / f"{stem}_history_{seconds}s.webp"

        save_gif(frames, seconds, gif_path)
        save_webp(frames, seconds, webp_path)

        print(
            f"Created {gif_path} and {webp_path} "
            f"({len(frames)} frames, {seconds}s)"
        )


if __name__ == "__main__":
    main()
