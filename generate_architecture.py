import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

matplotlib.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(14, 18))
ax.set_xlim(0, 14)
ax.set_ylim(0, 18)
ax.axis("off")
fig.patch.set_facecolor("white")


def box(ax, x, y, w, h, label, sublabel="", color="#f0f0f0", ec="#cccccc", fontsize=13, subfontsize=10):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                          facecolor=color, edgecolor=ec, linewidth=1.5)
    ax.add_patch(rect)
    cy = y + h / 2 + (0.18 if sublabel else 0)
    ax.text(x + w / 2, cy, label, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color="#222222")
    if sublabel:
        ax.text(x + w / 2, y + h / 2 - 0.22, sublabel, ha="center", va="center",
                fontsize=subfontsize, color="#555555")


def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#555555",
                                lw=1.8, mutation_scale=18))


def section_bg(ax, x, y, w, h, label, color="#e8f0fe", ec="#aabbd4"):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2",
                          facecolor=color, edgecolor=ec, linewidth=1.2, linestyle="--", zorder=0)
    ax.add_patch(rect)
    ax.text(x + 0.25, y + h - 0.25, label, ha="left", va="top",
            fontsize=10, color="#445566", style="italic")


# ── 1. 입력 ────────────────────────────────────────────────────────────────────
box(ax, 0.5, 16.5, 5.5, 1.0, "이미지 업로드", "약품 사진 촬영 또는 파일 선택", color="#f5f5f5")
box(ax, 8.0, 16.5, 5.5, 1.0, "약품명 직접 입력", "텍스트로 약품명 입력", color="#f5f5f5")

# ── 2. 신호 추출 (3개 병렬) ─────────────────────────────────────────────────────
section_bg(ax, 0.3, 13.6, 13.4, 2.6, "신호 추출", color="#f0f7ee", ec="#99bb88")

box(ax, 0.7, 14.0, 3.6, 1.8, "EasyOCR", "텍스트 신호 · 약 1~2초", color="#d4edda", ec="#88bb88")
box(ax, 5.2, 14.0, 3.6, 1.8, "CLIP", "형태 신호 · 1초 미만\n(자유문 설명 반환)", color="#d4edda", ec="#88bb88")
box(ax, 9.7, 14.0, 3.6, 1.8, "HSV 색상 추출", "색상 신호 · 약 0.1초", color="#d4edda", ec="#88bb88")

# ── 3. Symbolic Scene Representation ──────────────────────────────────────────
section_bg(ax, 0.3, 9.8, 13.4, 3.5, "OWL 온톨로지", color="#e8eaf6", ec="#7986cb")

box(ax, 0.7, 12.2, 12.6, 0.9, "build_scene_repr()", "OCR 텍스트 · CLIP 형태 · HSV 색상 → 온톨로지 개념 매핑", color="#c5cae9", ec="#7986cb")

# Scene repr 내용 박스 (4단계)
sr_labels = ["관측", "온톨로지 매핑", "추론 체인", "가설"]
sr_subs = ["OCR / CLIP / HSV", "계열별 점수 산출", "InsulinDrug → ColdChain\n→ Refrigerated → 2~8°C", "최고점 계열 + 근거"]
sr_colors = ["#e8eaf6", "#e8eaf6", "#e8eaf6", "#e8eaf6"]
for i, (lbl, sub, col) in enumerate(zip(sr_labels, sr_subs, sr_colors)):
    bx = 0.7 + i * 3.2
    box(ax, bx, 10.1, 3.0, 1.8, lbl, sub, color=col, ec="#9fa8da", fontsize=11)
    if i < 3:
        arrow(ax, bx + 3.0, 11.0, bx + 3.2, 11.0)

# ── 4. Gemma4 LLM ──────────────────────────────────────────────────────────────
section_bg(ax, 0.3, 7.3, 13.4, 2.2, "AI 이미지 분석", color="#f3e5f5", ec="#ab47bc")

box(ax, 0.7, 7.6, 12.6, 1.6,
    "Gemma4 VLM  (think: False)",
    "이미지 + Symbolic Scene Representation 참조 → 최종 계열 판단\n온톨로지 사전 추론으로 내부 추론 생략 · 약 3~10초",
    color="#e1bee7", ec="#ab47bc")

# ── 5. classify_drug ───────────────────────────────────────────────────────────
section_bg(ax, 0.3, 4.5, 13.4, 2.5, "지식 기반 추론 엔진", color="#e3f2fd", ec="#5c9bd4")

box(ax, 0.7, 4.8, 5.8, 1.8,
    "신뢰도 산출",
    "키워드 스코어 vs LLM 계열 비교\nHIGH / MID / LOW",
    color="#bbdefb", ec="#5c9bd4")
box(ax, 7.5, 4.8, 5.8, 1.8,
    "OWL 추론기 (HermiT)",
    "hasCategoryInd → equivalent_to\n→ requiresStorage → 온도 반환 · 약 0.5~1초",
    color="#bbdefb", ec="#5c9bd4")

# ── 6. 출력 ────────────────────────────────────────────────────────────────────
box(ax, 0.7, 2.5, 5.8, 1.5, "신뢰도", "HIGH / MID / LOW", color="#fff9c4", ec="#f9a825")
box(ax, 7.5, 2.5, 5.8, 1.5, "최종 보관 온도", "결과 저장 및 로그 기록", color="#fff9c4", ec="#f9a825")

# ── 화살표 ─────────────────────────────────────────────────────────────────────
# 입력 → 신호 추출
arrow(ax, 3.25, 16.5, 2.5, 16.2)
arrow(ax, 3.25, 16.5, 7.0, 16.2)
arrow(ax, 10.75, 16.5, 11.5, 16.2)

# 각 신호추출 박스 → build_scene_repr
arrow(ax, 2.5, 14.0, 4.5, 13.1)
arrow(ax, 7.0, 14.0, 7.0, 13.1)
arrow(ax, 11.5, 14.0, 9.5, 13.1)

# build_scene_repr → 4단계 내부 (대표 하나)
arrow(ax, 7.0, 12.2, 7.0, 11.9)

# 온톨로지 → Gemma4
arrow(ax, 7.0, 10.1, 7.0, 9.2)

# 약품명 입력 → Gemma4
arrow(ax, 10.75, 16.5, 10.75, 9.2)

# Gemma4 → classify_drug
arrow(ax, 4.0, 7.6, 3.6, 6.6)
arrow(ax, 10.0, 7.6, 10.4, 6.6)

# classify_drug → 출력
arrow(ax, 3.6, 4.8, 3.6, 4.0)
arrow(ax, 10.4, 4.8, 10.4, 4.0)

plt.tight_layout(pad=0.5)
plt.savefig("assets/architecture.png", dpi=150, bbox_inches="tight",
            facecolor="white", edgecolor="none")
print("저장 완료: assets/architecture.png")
