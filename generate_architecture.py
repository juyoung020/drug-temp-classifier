import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

matplotlib.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(13, 22))
ax.set_xlim(0, 13)
ax.set_ylim(0, 22)
ax.axis("off")
fig.patch.set_facecolor("white")


def box(ax, x, y, w, h, title, sub="", color="#f5f5f5", ec="#cccccc", tsize=13, ssize=10.5):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2",
                          facecolor=color, edgecolor=ec, linewidth=1.8, zorder=2)
    ax.add_patch(rect)
    ty = y + h / 2 + (0.22 if sub else 0)
    ax.text(x + w / 2, ty, title, ha="center", va="center",
            fontsize=tsize, fontweight="bold", color="#1a1a2e", zorder=3)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.25, sub, ha="center", va="center",
                fontsize=ssize, color="#444466", zorder=3)


def section(ax, x, y, w, h, label, color, ec):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25",
                          facecolor=color, edgecolor=ec, linewidth=1.5,
                          linestyle="--", zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.3, y + h - 0.2, label, ha="left", va="top",
            fontsize=10, color=ec, style="italic", fontweight="bold", zorder=3)


def arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#888888",
                                lw=2.0, mutation_scale=20), zorder=4)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.15, my, label, fontsize=9, color="#666666", va="center", zorder=4)


# ── 1. 입력 ────────────────────────────────────────────────────────────────────
box(ax, 1.0, 20.0, 4.5, 1.3, "이미지 업로드", "약품 사진", color="#f5f5f5", ec="#aaaaaa")
box(ax, 7.5, 20.0, 4.5, 1.3, "약품명 입력", "텍스트로 입력", color="#f5f5f5", ec="#aaaaaa")

# ── 2. 신호 추출 ────────────────────────────────────────────────────────────────
section(ax, 0.4, 16.5, 12.2, 3.0, "신호 추출", "#5a8a5a", "#5a8a5a")

box(ax, 0.8, 17.0, 3.4, 2.0, "EasyOCR", "글자 읽기\n1~2초", color="#d4edda", ec="#7ab87a", tsize=12)
box(ax, 4.8, 17.0, 3.4, 2.0, "CLIP", "형태 파악\n1초 미만", color="#d4edda", ec="#7ab87a", tsize=12)
box(ax, 8.8, 17.0, 3.4, 2.0, "HSV 색상", "색상 파악\n0.1초", color="#d4edda", ec="#7ab87a", tsize=12)

# ── 3. 온톨로지 ─────────────────────────────────────────────────────────────────
section(ax, 0.4, 10.5, 12.2, 5.5, "OWL 온톨로지  —  LLM 대신 먼저 추론", "#5566bb", "#5566bb")

box(ax, 1.0, 13.8, 11.0, 1.7,
    "OWL 추론기  —  장면 표현 생성",
    "세 가지 신호를 온톨로지 개념에 대응시켜 구조화된 맥락 텍스트를 만듭니다",
    color="#c5cae9", ec="#7986cb", tsize=13)

# 4단계 카드
stage_data = [
    ("관측", "OCR · CLIP · HSV\n원본 신호 정리"),
    ("매핑", "각 약품 계열에\n점수 부여"),
    ("추론 체인", "인슐린 → 냉장 보관\n→ 2~8°C"),
    ("가설", "가장 유력한\n계열 제안"),
]
for i, (title, sub) in enumerate(stage_data):
    bx = 0.8 + i * 3.0
    box(ax, bx, 11.0, 2.6, 2.5, title, sub, color="#e8eaf6", ec="#9fa8da", tsize=11, ssize=9.5)
    if i < 3:
        arrow(ax, bx + 2.6, 12.25, bx + 3.0, 12.25)

# ── 4. Gemma4 ──────────────────────────────────────────────────────────────────
section(ax, 0.4, 7.2, 12.2, 2.9, "AI 최종 판단", "#884499", "#884499")

box(ax, 1.0, 7.7, 11.0, 2.0,
    "Gemma4  (내부 추론 OFF)",
    "이미지를 직접 보면서 온톨로지가 제안한 계열을 확인하거나 수정합니다\n3~10초",
    color="#e1bee7", ec="#aa55cc", tsize=13)

# ── 5. 결과 ────────────────────────────────────────────────────────────────────
section(ax, 0.4, 3.8, 12.2, 3.0, "결과", "#aa7700", "#aa7700")

box(ax, 0.8, 4.3, 3.8, 2.0, "신뢰도", "HIGH · MID · LOW\nLLM ↔ 온톨로지 일치 여부", color="#fff9c4", ec="#f9a825", tsize=12)
box(ax, 5.0, 4.3, 3.0, 2.0, "OWL 분류기", "계층 규칙으로\n온도 자동 도출", color="#fff9c4", ec="#f9a825", tsize=11)
box(ax, 9.0, 4.3, 3.2, 2.0, "최종 온도", "예) 2~8°C\n냉장 보관", color="#fff9c4", ec="#f9a825", tsize=12)

# ── 화살표 ─────────────────────────────────────────────────────────────────────
# 입력 → 신호 추출
arrow(ax, 3.25, 20.0, 2.5, 19.5)
arrow(ax, 9.75, 20.0, 11.0, 19.5)
arrow(ax, 6.5, 20.0, 6.5, 19.5)

# 신호 추출 → 장면 표현 생성
arrow(ax, 2.5, 17.0, 4.5, 15.5)
arrow(ax, 6.5, 17.0, 6.5, 15.5)
arrow(ax, 11.0, 17.0, 8.5, 15.5)

# 장면 표현 → 카드
arrow(ax, 6.5, 13.8, 6.5, 13.5)

# 카드 → Gemma4
arrow(ax, 6.5, 11.0, 6.5, 9.7)

# 약품명 → Gemma4
arrow(ax, 9.75, 20.0, 9.75, 9.7)

# Gemma4 → 결과
arrow(ax, 3.5, 7.7, 2.7, 6.3)
arrow(ax, 6.5, 7.7, 6.5, 6.3)
arrow(ax, 9.5, 7.7, 10.6, 6.3)

# OWL → 최종온도
arrow(ax, 8.0, 5.3, 9.0, 5.3)

plt.tight_layout(pad=0.5)
plt.savefig("assets/architecture.png", dpi=150, bbox_inches="tight",
            facecolor="white", edgecolor="none")
print("저장 완료")
