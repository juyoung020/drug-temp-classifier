import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

matplotlib.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

W, H = 10, 13
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, W)
ax.set_ylim(2.5, H)
ax.axis("off")
fig.patch.set_facecolor("white")


def box(ax, x, y, w, h, title, sub="", color="white", ec="#cccccc", tsize=11, ssize=8.5):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                          facecolor=color, edgecolor=ec, linewidth=1.8, zorder=3)
    ax.add_patch(rect)
    if sub:
        ax.text(x + w/2, y + h/2 + 0.18, title, ha="center", va="center",
                fontsize=tsize, fontweight="bold", color="#1a1a2e", zorder=4)
        ax.text(x + w/2, y + h/2 - 0.18, sub, ha="center", va="center",
                fontsize=ssize, color="#667788", zorder=4)
    else:
        ax.text(x + w/2, y + h/2, title, ha="center", va="center",
                fontsize=tsize, fontweight="bold", color="#1a1a2e", zorder=4)


def chip(ax, x, y, text, color):
    ax.text(x, y, text, ha="center", va="center", fontsize=8,
            color="white", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=color,
                      edgecolor="none", alpha=0.85), zorder=5)


def arr(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#aaaaaa",
                                lw=1.5, mutation_scale=13), zorder=2)


# ── 입력 ──────────────────────────────────────────────────────────────────────
box(ax, 0.4, 11.5, 3.6, 1.0, "이미지 업로드", "약품 사진")
box(ax, 6.0, 11.5, 3.6, 1.0, "약품명 입력", "텍스트 입력")

# ── 신호 추출 ──────────────────────────────────────────────────────────────────
chip(ax, 5.0, 10.8, "신호 추출", "#4a8a4a")

box(ax, 0.3, 9.7, 2.8, 1.0, "EasyOCR", "글자 읽기", color="#f0faf0", ec="#7ab87a")
box(ax, 3.6, 9.7, 2.8, 1.0, "CLIP", "형태 파악", color="#f0faf0", ec="#7ab87a")
box(ax, 6.9, 9.7, 2.8, 1.0, "HSV 색상", "색상 파악", color="#f0faf0", ec="#7ab87a")

# ── OWL 추론기 ─────────────────────────────────────────────────────────────────
chip(ax, 5.0, 9.1, "OWL 추론기  —  LLM 전에 먼저 실행", "#4455aa")

box(ax, 0.3, 7.9, 9.4, 0.9,
    "장면 표현 생성 (Symbolic Scene Representation)",
    "신호를 온톨로지에 매핑해 LLM에 전달할 구조화된 맥락을 만듭니다",
    color="#f0f1fc", ec="#7986cb")

for i, (t, s) in enumerate([("관측","신호 정리"), ("매핑","계열 점수"), ("추론 체인","온도 도출"), ("가설","계열 제안")]):
    bx = 0.3 + i * 2.38
    box(ax, bx, 6.2, 2.1, 1.4, t, s, color="#f0f1fc", ec="#9fa8da", tsize=10, ssize=8)
    if i < 3:
        arr(ax, bx + 2.1, 6.9, bx + 2.38, 6.9)

# ── Gemma4 ─────────────────────────────────────────────────────────────────────
chip(ax, 5.0, 5.8, "AI 최종 판단", "#774488")

box(ax, 0.3, 4.8, 9.4, 0.9,
    "Gemma4  (내부 추론 OFF)",
    "온톨로지 맥락을 참조해 약품 계열을 최종 판단합니다",
    color="#faf0fc", ec="#bb66dd")

# ── 결과 ───────────────────────────────────────────────────────────────────────
chip(ax, 5.0, 4.3, "결과", "#996600")

box(ax, 0.3, 3.1, 2.9, 1.0, "신뢰도", "HIGH / MID / LOW", color="#fffde7", ec="#f9a825")
box(ax, 3.6, 3.1, 2.8, 1.0, "OWL 분류기", "온도 자동 도출", color="#fffde7", ec="#f9a825")
box(ax, 6.9, 3.1, 2.8, 1.0, "최종 온도", "예) 2~8°C", color="#fffde7", ec="#f9a825")

# ── 화살표 ─────────────────────────────────────────────────────────────────────
# 이미지 → 세 신호박스로
arr(ax, 2.2, 11.5, 1.7, 10.7)
arr(ax, 2.2, 11.5, 5.0, 10.7)
arr(ax, 2.2, 11.5, 8.3, 10.7)

# 약품명 → Gemma4 (오른쪽 가장자리를 따라 내려감)
ax.plot([9.6, 9.85, 9.85], [12.0, 12.0, 5.3], color="#aaaaaa", lw=1.5, zorder=2)
arr(ax, 9.85, 5.3, 9.65, 5.3)

# 세 신호 → 장면표현으로 수렴
arr(ax, 1.7, 9.7, 3.5, 8.8)
arr(ax, 5.0, 9.7, 5.0, 8.8)
arr(ax, 8.3, 9.7, 6.5, 8.8)

# 장면표현 → 4단계 카드
arr(ax, 5.0, 7.9, 5.0, 7.6)

# 카드 → Gemma4
arr(ax, 5.0, 6.2, 5.0, 5.7)

# Gemma4 → 결과
arr(ax, 1.8, 4.8, 1.8, 4.1)
arr(ax, 5.0, 4.8, 5.0, 4.1)
arr(ax, 8.3, 4.8, 8.3, 4.1)

# OWL 분류기 → 최종 온도
arr(ax, 6.4, 3.6, 6.9, 3.6)

plt.tight_layout(pad=0.3)
plt.savefig("assets/architecture.png", dpi=150, bbox_inches="tight",
            facecolor="white", edgecolor="none")
print("저장 완료")
