import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

matplotlib.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(11, 18))
ax.set_xlim(0, 11)
ax.set_ylim(4.5, 18)
ax.axis("off")
fig.patch.set_facecolor("#f8f9fa")


def box(ax, x, y, w, h, title, sub="", color="white", ec="#cccccc", tsize=12, ssize=9.5):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2",
                          facecolor=color, edgecolor=ec, linewidth=2.0, zorder=3)
    ax.add_patch(rect)
    ty = y + h / 2 + (0.2 if sub else 0)
    ax.text(x + w / 2, ty, title, ha="center", va="center",
            fontsize=tsize, fontweight="bold", color="#1a1a2e", zorder=4)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.22, sub, ha="center", va="center",
                fontsize=ssize, color="#666688", zorder=4)


def label(ax, x, y, text, color="#666666"):
    ax.text(x, y, text, ha="center", va="center",
            fontsize=9.5, color=color, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color, linewidth=1.2, alpha=0.9), zorder=5)


def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#aaaaaa",
                                lw=1.8, mutation_scale=16), zorder=2)


def hline(ax, y, color="#dddddd"):
    ax.axhline(y, color=color, lw=1.0, linestyle="--", zorder=1)


# ── 1. 입력 ─────────────────────────────────────────────────────────────────
box(ax, 0.6, 16.4, 3.8, 1.2, "이미지 업로드", "약품 사진")
box(ax, 6.6, 16.4, 3.8, 1.2, "약품명 입력", "텍스트 입력")

# ── 2. 신호 추출 ─────────────────────────────────────────────────────────────
label(ax, 5.5, 15.5, "신호 추출", "#4a8a4a")

box(ax, 0.4, 13.9, 3.0, 1.3, "EasyOCR", "글자 읽기", color="#edfaee", ec="#7ab87a")
box(ax, 4.0, 13.9, 3.0, 1.3, "CLIP", "형태 파악", color="#edfaee", ec="#7ab87a")
box(ax, 7.6, 13.9, 3.0, 1.3, "HSV 색상", "색상 파악", color="#edfaee", ec="#7ab87a")

hline(ax, 13.5)

# ── 3. OWL 추론기 ────────────────────────────────────────────────────────────
label(ax, 5.5, 13.2, "OWL 추론기  —  LLM 전에 먼저 실행", "#4455aa")

box(ax, 0.6, 11.8, 9.8, 1.1,
    "장면 표현 생성 (Symbolic Scene Representation)",
    "신호를 온톨로지 개념에 매핑해 LLM에 전달할 구조화된 맥락을 만듭니다",
    color="#eef0fb", ec="#7986cb")

box(ax, 0.4, 9.7, 2.3, 1.8, "관측", "신호 정리", color="#eef0fb", ec="#9fa8da", tsize=11)
box(ax, 3.0, 9.7, 2.3, 1.8, "매핑", "계열 점수", color="#eef0fb", ec="#9fa8da", tsize=11)
box(ax, 5.6, 9.7, 2.3, 1.8, "추론 체인", "온도 도출", color="#eef0fb", ec="#9fa8da", tsize=11)
box(ax, 8.2, 9.7, 2.3, 1.8, "가설", "계열 제안", color="#eef0fb", ec="#9fa8da", tsize=11)

arrow(ax, 2.7, 10.6, 3.0, 10.6)
arrow(ax, 5.3, 10.6, 5.6, 10.6)
arrow(ax, 7.9, 10.6, 8.2, 10.6)

hline(ax, 9.3)

# ── 4. Gemma4 ────────────────────────────────────────────────────────────────
label(ax, 5.5, 8.9, "AI 최종 판단", "#774488")

box(ax, 0.6, 7.5, 9.8, 1.2,
    "Gemma4  (내부 추론 OFF)",
    "온톨로지 맥락을 참조해 약품 계열을 최종 판단합니다",
    color="#f8eefa", ec="#bb66dd")

hline(ax, 7.1)

# ── 5. 결과 ──────────────────────────────────────────────────────────────────
label(ax, 5.5, 6.7, "결과", "#996600")

box(ax, 0.4, 5.2, 3.1, 1.3, "신뢰도", "HIGH / MID / LOW", color="#fffde7", ec="#f9a825")
box(ax, 4.0, 5.2, 3.0, 1.3, "OWL 분류기", "온도 자동 도출", color="#fffde7", ec="#f9a825")
box(ax, 7.6, 5.2, 3.0, 1.3, "최종 온도", "예) 2~8°C", color="#fffde7", ec="#f9a825")

# ── 화살표 ───────────────────────────────────────────────────────────────────
# 입력 → 신호 추출
arrow(ax, 2.5, 16.4, 1.9, 15.2)
arrow(ax, 5.5, 16.4, 5.5, 15.2)
arrow(ax, 8.5, 16.4, 9.1, 15.2)

# 신호 추출 → 장면 표현
arrow(ax, 1.9, 13.9, 3.5, 12.9)
arrow(ax, 5.5, 13.9, 5.5, 12.9)
arrow(ax, 9.1, 13.9, 7.5, 12.9)

# 장면 표현 → 카드
arrow(ax, 5.5, 11.8, 5.5, 11.5)

# 카드 → Gemma4
arrow(ax, 5.5, 9.7, 5.5, 8.7)

# 약품명 → Gemma4
arrow(ax, 8.5, 16.4, 8.5, 8.7)

# Gemma4 → 결과
arrow(ax, 2.0, 7.5, 2.0, 6.5)
arrow(ax, 5.5, 7.5, 5.5, 6.5)
arrow(ax, 9.0, 7.5, 9.1, 6.5)

# OWL 분류기 → 최종 온도
arrow(ax, 7.0, 5.85, 7.6, 5.85)

plt.tight_layout(pad=0.5)
plt.savefig("assets/architecture.png", dpi=150, bbox_inches="tight",
            facecolor="#f8f9fa", edgecolor="none")
print("저장 완료")
