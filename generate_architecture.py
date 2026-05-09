import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

matplotlib.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(12, 17))
ax.set_xlim(0, 12)
ax.set_ylim(0, 17)
ax.axis("off")
fig.patch.set_facecolor("white")


def box(ax, x, y, w, h, title, sub="", color="#f5f5f5", ec="#cccccc", tsize=12, ssize=9.5):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.18",
                          facecolor=color, edgecolor=ec, linewidth=1.5, zorder=2)
    ax.add_patch(rect)
    ty = y + h / 2 + (0.22 if sub else 0)
    ax.text(x + w / 2, ty, title, ha="center", va="center",
            fontsize=tsize, fontweight="bold", color="#1a1a2e", zorder=3)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.25, sub, ha="center", va="center",
                fontsize=ssize, color="#555577", zorder=3)


def section(ax, x, y, w, h, label, ec):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25",
                          facecolor="#fafafa", edgecolor=ec, linewidth=1.4,
                          linestyle="--", zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.28, y + h - 0.22, label, ha="left", va="top",
            fontsize=9, color=ec, style="italic", fontweight="bold", zorder=3)


def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#999999",
                                lw=1.6, mutation_scale=15), zorder=4)


# ── 1. 입력 ─────────────────────────────────────────────────────────────────
box(ax, 0.8, 15.4, 4.0, 1.1, "이미지 업로드", "약품 사진", color="#f5f5f5", ec="#bbbbbb")
box(ax, 7.2, 15.4, 4.0, 1.1, "약품명 입력", "텍스트 입력", color="#f5f5f5", ec="#bbbbbb")

# ── 2. 신호 추출 ─────────────────────────────────────────────────────────────
section(ax, 0.3, 12.8, 11.4, 2.3, "신호 추출", "#4a8a4a")

box(ax, 0.7, 13.1, 3.2, 1.6, "EasyOCR", "글자 읽기", color="#d4edda", ec="#7ab87a")
box(ax, 4.4, 13.1, 3.2, 1.6, "CLIP", "형태 파악", color="#d4edda", ec="#7ab87a")
box(ax, 8.1, 13.1, 3.2, 1.6, "HSV 색상", "색상 파악", color="#d4edda", ec="#7ab87a")

# ── 3. OWL 추론기 ────────────────────────────────────────────────────────────
section(ax, 0.3, 7.3, 11.4, 5.2, "OWL 추론기  —  LLM 전에 먼저 추론", "#4455aa")

box(ax, 0.8, 11.3, 10.4, 1.1,
    "장면 표현 생성 (Symbolic Scene Representation)",
    "신호를 온톨로지 개념에 매핑해 LLM에 전달할 구조화된 맥락을 만듭니다",
    color="#c5cae9", ec="#7986cb")

stage_data = [
    ("관측", "신호 정리"),
    ("매핑", "계열 점수"),
    ("추론 체인", "온도 도출"),
    ("가설", "계열 제안"),
]
for i, (title, sub) in enumerate(stage_data):
    bx = 0.7 + i * 2.77
    box(ax, bx, 7.7, 2.45, 3.2, title, sub, color="#e8eaf6", ec="#9fa8da", tsize=11, ssize=9)
    if i < 3:
        arrow(ax, bx + 2.45, 9.3, bx + 2.77, 9.3)

# ── 4. Gemma4 ────────────────────────────────────────────────────────────────
section(ax, 0.3, 5.1, 11.4, 1.9, "AI 최종 판단", "#774488")

box(ax, 0.8, 5.4, 10.4, 1.3,
    "Gemma4  (내부 추론 OFF)",
    "온톨로지 맥락을 참조해 이미지의 약품 계열을 최종 판단합니다",
    color="#e1bee7", ec="#aa55cc")

# ── 5. 결과 ──────────────────────────────────────────────────────────────────
section(ax, 0.3, 2.4, 11.4, 2.4, "결과", "#996600")

box(ax, 0.7, 2.8, 3.3, 1.6, "신뢰도", "HIGH / MID / LOW", color="#fff9c4", ec="#f9a825")
box(ax, 4.4, 2.8, 3.2, 1.6, "OWL 분류기", "온도 자동 도출", color="#fff9c4", ec="#f9a825")
box(ax, 8.0, 2.8, 3.3, 1.6, "최종 온도", "예) 2~8°C", color="#fff9c4", ec="#f9a825")

# ── 화살표 ───────────────────────────────────────────────────────────────────
# 입력 → 신호 추출
arrow(ax, 2.8, 15.4, 2.3, 15.1)
arrow(ax, 6.0, 15.4, 6.0, 15.1)
arrow(ax, 9.2, 15.4, 9.7, 15.1)

# 신호 추출 → 장면 표현
arrow(ax, 2.3, 13.1, 4.0, 12.4)
arrow(ax, 6.0, 13.1, 6.0, 12.4)
arrow(ax, 9.7, 13.1, 8.0, 12.4)

# 장면 표현 → 카드
arrow(ax, 6.0, 11.3, 6.0, 10.9)

# 카드 → Gemma4
arrow(ax, 6.0, 7.7, 6.0, 6.7)

# 약품명 → Gemma4
arrow(ax, 9.2, 15.4, 9.2, 6.7)

# Gemma4 → 결과
arrow(ax, 2.3, 5.4, 2.3, 4.4)
arrow(ax, 6.0, 5.4, 6.0, 4.4)
arrow(ax, 9.7, 5.4, 9.7, 4.4)

# OWL 분류기 → 최종 온도
arrow(ax, 7.6, 3.6, 8.0, 3.6)

plt.tight_layout(pad=0.4)
plt.savefig("assets/architecture.png", dpi=150, bbox_inches="tight",
            facecolor="white", edgecolor="none")
print("저장 완료")
