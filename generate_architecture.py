import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

matplotlib.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(12, 15))
ax.set_xlim(0, 12)
ax.set_ylim(0, 15)
ax.axis("off")
fig.patch.set_facecolor("white")


def box(ax, x, y, w, h, title, sub="", color="#f5f5f5", ec="#cccccc", tsize=12, ssize=9.5):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                          facecolor=color, edgecolor=ec, linewidth=1.6, zorder=2)
    ax.add_patch(rect)
    ty = y + h / 2 + (0.17 if sub else 0)
    ax.text(x + w / 2, ty, title, ha="center", va="center",
            fontsize=tsize, fontweight="bold", color="#1a1a2e", zorder=3)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.2, sub, ha="center", va="center",
                fontsize=ssize, color="#444466", zorder=3)


def section(ax, x, y, w, h, label, color, ec):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2",
                          facecolor=color, edgecolor=ec, linewidth=1.4,
                          linestyle="--", zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.25, y + h - 0.18, label, ha="left", va="top",
            fontsize=9, color=ec, style="italic", fontweight="bold", zorder=3)


def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#888888",
                                lw=1.8, mutation_scale=16), zorder=4)


# ── 1. 입력 ────────────────────────────────────────────────────────────────────
box(ax, 0.8, 13.6, 4.2, 0.9, "이미지 업로드", "약품 사진", color="#f5f5f5", ec="#aaaaaa")
box(ax, 7.0, 13.6, 4.2, 0.9, "약품명 입력", "텍스트로 입력", color="#f5f5f5", ec="#aaaaaa")

# ── 2. 신호 추출 ────────────────────────────────────────────────────────────────
section(ax, 0.3, 11.2, 11.4, 2.1, "신호 추출", "#5a8a5a", "#5a8a5a")

box(ax, 0.6, 11.5, 3.3, 1.5, "EasyOCR", "글자 읽기 · 1~2초", color="#d4edda", ec="#7ab87a", tsize=11)
box(ax, 4.35, 11.5, 3.3, 1.5, "CLIP", "형태 파악 · 1초 미만", color="#d4edda", ec="#7ab87a", tsize=11)
box(ax, 8.1, 11.5, 3.3, 1.5, "HSV 색상", "색상 파악 · 0.1초", color="#d4edda", ec="#7ab87a", tsize=11)

# ── 3. 온톨로지 ─────────────────────────────────────────────────────────────────
section(ax, 0.3, 6.3, 11.4, 4.6, "OWL 온톨로지  —  LLM 전에 먼저 추론", "#5566bb", "#5566bb")

box(ax, 0.7, 9.8, 10.6, 1.0,
    "OWL 추론기  —  장면 표현 생성",
    "세 신호를 온톨로지 개념에 매핑해 구조화된 맥락 텍스트를 만듭니다",
    color="#c5cae9", ec="#7986cb", tsize=11.5)

stage_data = [
    ("관측", "OCR · CLIP · HSV\n신호 정리"),
    ("매핑", "계열별\n점수 부여"),
    ("추론 체인", "인슐린 → 냉장\n→ 2~8°C"),
    ("가설", "유력 계열\n제안"),
]
for i, (title, sub) in enumerate(stage_data):
    bx = 0.6 + i * 2.85
    box(ax, bx, 6.6, 2.55, 2.9, title, sub, color="#e8eaf6", ec="#9fa8da", tsize=10.5, ssize=9)
    if i < 3:
        arrow(ax, bx + 2.55, 8.05, bx + 2.85, 8.05)

# ── 4. Gemma4 ──────────────────────────────────────────────────────────────────
section(ax, 0.3, 4.2, 11.4, 1.8, "AI 최종 판단", "#884499", "#884499")

box(ax, 0.7, 4.5, 10.6, 1.2,
    "Gemma4  (내부 추론 OFF)",
    "이미지를 직접 보면서 온톨로지 제안 계열을 확인하거나 수정합니다 · 3~10초",
    color="#e1bee7", ec="#aa55cc", tsize=11.5)

# ── 5. 결과 ────────────────────────────────────────────────────────────────────
section(ax, 0.3, 1.5, 11.4, 2.4, "결과", "#aa7700", "#aa7700")

box(ax, 0.6, 1.8, 3.5, 1.7, "신뢰도", "HIGH · MID · LOW\nLLM ↔ 온톨로지 일치", color="#fff9c4", ec="#f9a825", tsize=11)
box(ax, 4.5, 1.8, 3.0, 1.7, "OWL 분류기", "계층 규칙으로\n온도 자동 도출", color="#fff9c4", ec="#f9a825", tsize=11)
box(ax, 8.0, 1.8, 3.2, 1.7, "최종 온도", "예) 2~8°C\n냉장 보관", color="#fff9c4", ec="#f9a825", tsize=11)

# ── 화살표 ─────────────────────────────────────────────────────────────────────
# 입력 → 신호 추출
arrow(ax, 2.9, 13.6, 2.2, 13.3)
arrow(ax, 6.0, 13.6, 6.0, 13.3)
arrow(ax, 9.1, 13.6, 9.8, 13.3)

# 신호 추출 → 장면 표현
arrow(ax, 2.2, 11.5, 4.0, 10.8)
arrow(ax, 6.0, 11.5, 6.0, 10.8)
arrow(ax, 9.8, 11.5, 8.0, 10.8)

# 장면 표현 → 카드
arrow(ax, 6.0, 9.8, 6.0, 9.5)

# 카드 → Gemma4
arrow(ax, 6.0, 6.6, 6.0, 5.7)

# 약품명 → Gemma4
arrow(ax, 9.1, 13.6, 9.1, 5.7)

# Gemma4 → 결과
arrow(ax, 2.5, 4.5, 2.3, 3.5)
arrow(ax, 6.0, 4.5, 6.0, 3.5)
arrow(ax, 9.5, 4.5, 9.6, 3.5)

# OWL 분류기 → 최종 온도
arrow(ax, 7.5, 2.65, 8.0, 2.65)

plt.tight_layout(pad=0.3)
plt.savefig("assets/architecture.png", dpi=150, bbox_inches="tight",
            facecolor="white", edgecolor="none")
print("저장 완료")
