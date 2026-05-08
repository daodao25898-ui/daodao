"""视频字幕/花字检测脚本。

依赖：
    pip install opencv-python pytesseract
    # 以及系统安装 tesseract-ocr

用法：
    python -m src.video_text_detector /path/to/video.mp4 --sample-every 12
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import pytesseract


@dataclass
class TextHit:
    frame_idx: int
    sec: float
    text: str
    conf: float
    box: Tuple[int, int, int, int]  # x, y, w, h
    region: str  # subtitle / overlay


class VideoTextDetector:
    def __init__(self, video_path: str, sample_every: int = 12, min_conf: float = 45.0):
        self.video_path = video_path
        self.sample_every = max(1, sample_every)
        self.min_conf = min_conf

    def _ocr_frame(self, frame, frame_idx: int, fps: float) -> List[TextHit]:
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        data = pytesseract.image_to_data(
            bw,
            output_type=pytesseract.Output.DICT,
            config="--oem 3 --psm 6",
            lang="chi_sim+eng",
        )

        hits: List[TextHit] = []
        for i, txt in enumerate(data["text"]):
            txt = txt.strip()
            if not txt:
                continue
            try:
                conf = float(data["conf"][i])
            except ValueError:
                continue
            if conf < self.min_conf:
                continue

            x, y = int(data["left"][i]), int(data["top"][i])
            ww, hh = int(data["width"][i]), int(data["height"][i])
            center_y = y + hh / 2

            # 简单启发式：底部 25% 且宽度较大，判定为字幕；其余判定为花字/叠字
            is_subtitle_zone = center_y > h * 0.75 and ww > w * 0.08
            region = "subtitle" if is_subtitle_zone else "overlay"

            hits.append(
                TextHit(
                    frame_idx=frame_idx,
                    sec=frame_idx / fps if fps > 0 else 0.0,
                    text=txt,
                    conf=conf,
                    box=(x, y, ww, hh),
                    region=region,
                )
            )
        return hits

    def detect(self) -> Dict:
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise RuntimeError(f"无法打开视频: {self.video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        hits: List[TextHit] = []
        idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if idx % self.sample_every == 0:
                hits.extend(self._ocr_frame(frame, idx, fps))
            idx += 1

        cap.release()

        grouped = defaultdict(list)
        for h in hits:
            grouped[h.region].append(h)

        subtitle_hits = grouped.get("subtitle", [])
        overlay_hits = grouped.get("overlay", [])

        result = {
            "video": str(Path(self.video_path).resolve()),
            "fps": fps,
            "total_frames": total,
            "sample_every": self.sample_every,
            "has_subtitle": len(subtitle_hits) > 0,
            "has_overlay_text": len(overlay_hits) > 0,
            "subtitle_count": len(subtitle_hits),
            "overlay_count": len(overlay_hits),
            "samples": {
                "subtitle": [
                    {
                        "sec": round(h.sec, 2),
                        "frame_idx": h.frame_idx,
                        "text": h.text,
                        "conf": round(h.conf, 1),
                        "bbox": {
                            "x": h.box[0],
                            "y": h.box[1],
                            "w": h.box[2],
                            "h": h.box[3],
                            "x2": h.box[0] + h.box[2],
                            "y2": h.box[1] + h.box[3],
                        },
                    }
                    for h in subtitle_hits[:20]
                ],
                "overlay": [
                    {
                        "sec": round(h.sec, 2),
                        "frame_idx": h.frame_idx,
                        "text": h.text,
                        "conf": round(h.conf, 1),
                        "bbox": {
                            "x": h.box[0],
                            "y": h.box[1],
                            "w": h.box[2],
                            "h": h.box[3],
                            "x2": h.box[0] + h.box[2],
                            "y2": h.box[1] + h.box[3],
                        },
                    }
                    for h in overlay_hits[:20]
                ],
            },
        }
        return result


def main():
    parser = argparse.ArgumentParser(description="检测视频中是否存在字幕、花字等文本")
    parser.add_argument("video", help="视频路径")
    parser.add_argument("--sample-every", type=int, default=12, help="每隔多少帧采样一次")
    parser.add_argument("--min-conf", type=float, default=45.0, help="OCR 最低置信度")
    parser.add_argument("--json", action="store_true", help="仅输出 JSON")
    args = parser.parse_args()

    detector = VideoTextDetector(args.video, sample_every=args.sample_every, min_conf=args.min_conf)
    result = detector.detect()

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print("==== 检测结果 ====")
    print(f"视频: {result['video']}")
    print(f"是否有字幕: {result['has_subtitle']} (命中 {result['subtitle_count']})")
    print(f"是否有花字/叠字: {result['has_overlay_text']} (命中 {result['overlay_count']})")
    print("\n示例字幕:")
    for x in result["samples"]["subtitle"][:5]:
        b = x["bbox"]
        print(f"  - {x['sec']}s | {x['text']} | conf={x['conf']} | bbox=({b['x']},{b['y']},{b['w']},{b['h']})")
    print("示例花字/叠字:")
    for x in result["samples"]["overlay"][:5]:
        b = x["bbox"]
        print(f"  - {x['sec']}s | {x['text']} | conf={x['conf']} | bbox=({b['x']},{b['y']},{b['w']},{b['h']})")


if __name__ == "__main__":
    main()
