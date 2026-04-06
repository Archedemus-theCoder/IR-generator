"""IR Management System - Web Dashboard

브라우저에서 IR 콘텐츠와 재무 프로젝션을 편집하고,
PPT를 자동 생성/다운로드하는 웹 대시보드.
"""

import io
import sys
import copy
from pathlib import Path

import streamlit as st
import yaml
import pandas as pd

# Ensure src/ is importable (no pip install -e . needed)
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Project root
PROJECT_ROOT = Path(__file__).parent

# --- Utility Functions ---

def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def save_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False), encoding="utf-8")


def load_slide(path: Path) -> dict:
    """Parse markdown slide with YAML front matter."""
    text = path.read_text(encoding="utf-8")
    front_matter = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            front_matter = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()
    return {"front_matter": front_matter, "body": body, "path": str(path)}


def save_slide(path: Path, front_matter: dict, body: str) -> None:
    fm_text = yaml.dump(front_matter, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content = f"---\n{fm_text}---\n\n{body}\n"
    path.write_text(content, encoding="utf-8")


# --- Page Config ---
st.set_page_config(
    page_title="IR Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar Navigation ---
st.sidebar.title("IR Management")
page = st.sidebar.radio(
    "메뉴",
    ["📊 재무 프로젝션", "📝 슬라이드 편집", "📋 덱 구성", "⬇️ PPT 내보내기"],
)


# ===================================================
# 📊 재무 프로젝션 페이지
# ===================================================
if page == "📊 재무 프로젝션":
    st.title("📊 재무 프로젝션")
    st.caption("숫자를 직접 편집하면 모든 슬라이드에 자동 반영됩니다")

    pl_path = PROJECT_ROOT / "financials" / "pl.yaml"
    assumptions_path = PROJECT_ROOT / "financials" / "assumptions.yaml"

    pl_data = load_yaml(pl_path)
    assumptions_data = load_yaml(assumptions_path)

    # --- Assumptions Section ---
    st.subheader("핵심 가정")
    col1, col2, col3 = st.columns(3)
    with col1:
        growth_rate = st.number_input(
            "월간 매출 성장률 (%)",
            value=float(assumptions_data.get("revenue_growth_rate_monthly", 0.12)) * 100,
            step=1.0, format="%.1f",
        )
        assumptions_data["revenue_growth_rate_monthly"] = growth_rate / 100
    with col2:
        churn = st.number_input(
            "월간 이탈률 (%)",
            value=float(assumptions_data.get("churn_rate_monthly", 0.03)) * 100,
            step=0.5, format="%.1f",
        )
        assumptions_data["churn_rate_monthly"] = churn / 100
    with col3:
        acv = st.number_input(
            "평균 계약 금액 ($)",
            value=int(assumptions_data.get("average_contract_value", 2500)),
            step=100,
        )
        assumptions_data["average_contract_value"] = acv

    st.divider()

    # --- P&L Table ---
    st.subheader("손익계산서 (P&L)")

    periods = pl_data.get("periods", [])

    if periods:
        # Build revenue DataFrame
        st.markdown("**매출 (Revenue)**")
        revenue_data = {}
        for key, item in pl_data.get("revenue", {}).items():
            revenue_data[item.get("label", key)] = [
                item.get("values", {}).get(p, 0) for p in periods
            ]
        if revenue_data:
            rev_df = pd.DataFrame(revenue_data, index=periods).T
            edited_rev = st.data_editor(
                rev_df,
                use_container_width=True,
                num_rows="fixed",
                key="revenue_editor",
            )
            # Write back edited values
            for (key, item), (_, row) in zip(
                pl_data.get("revenue", {}).items(), edited_rev.iterrows()
            ):
                for p, val in zip(periods, row):
                    item["values"][p] = int(val)

        st.markdown("**비용 (Costs)**")
        cost_data = {}
        for key, item in pl_data.get("costs", {}).items():
            cost_data[item.get("label", key)] = [
                item.get("values", {}).get(p, 0) for p in periods
            ]
        if cost_data:
            cost_df = pd.DataFrame(cost_data, index=periods).T
            edited_cost = st.data_editor(
                cost_df,
                use_container_width=True,
                num_rows="fixed",
                key="cost_editor",
            )
            for (key, item), (_, row) in zip(
                pl_data.get("costs", {}).items(), edited_cost.iterrows()
            ):
                for p, val in zip(periods, row):
                    item["values"][p] = int(val)

        # --- Computed Summary ---
        st.divider()
        st.subheader("자동 계산 요약")

        summary_data = {"Period": periods}
        total_rev = []
        total_cost = []
        for p in periods:
            r = sum(item.get("values", {}).get(p, 0) for item in pl_data.get("revenue", {}).values())
            c = sum(item.get("values", {}).get(p, 0) for item in pl_data.get("costs", {}).values())
            total_rev.append(r)
            total_cost.append(c)

        profit = [r - c for r, c in zip(total_rev, total_cost)]
        margin = [p / r * 100 if r > 0 else 0 for p, r in zip(profit, total_rev)]

        summary_df = pd.DataFrame({
            "기간": periods,
            "총 매출": [f"${v:,.0f}" for v in total_rev],
            "총 비용": [f"${v:,.0f}" for v in total_cost],
            "이익": [f"${v:,.0f}" for v in profit],
            "마진": [f"{v:.1f}%" for v in margin],
        })
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # Year-by-year summary cards
        years = sorted(set(p.split("-")[0] for p in periods))
        cols = st.columns(len(years))
        for col, year in zip(cols, years):
            year_periods = [p for p in periods if p.startswith(year)]
            yr_rev = sum(total_rev[periods.index(p)] for p in year_periods)
            yr_cost = sum(total_cost[periods.index(p)] for p in year_periods)
            yr_profit = yr_rev - yr_cost
            with col:
                st.metric(f"FY{year} 매출", f"${yr_rev:,.0f}")
                st.metric(f"FY{year} 이익", f"${yr_profit:,.0f}",
                         delta=f"{yr_profit/yr_rev*100:.1f}%" if yr_rev > 0 else "N/A")

        # Chart
        st.divider()
        st.subheader("매출 vs 비용 추이")
        chart_df = pd.DataFrame({
            "매출": total_rev,
            "비용": total_cost,
            "이익": profit,
        }, index=periods)
        st.line_chart(chart_df, use_container_width=True)

    # Save button
    st.divider()
    if st.button("💾 재무 데이터 저장", type="primary", use_container_width=True):
        save_yaml(pl_path, pl_data)
        save_yaml(assumptions_path, assumptions_data)
        st.success("재무 데이터가 저장되었습니다! 슬라이드에 자동 반영됩니다.")


# ===================================================
# 📝 슬라이드 편집 페이지
# ===================================================
elif page == "📝 슬라이드 편집":
    st.title("📝 슬라이드 편집")
    st.caption("슬라이드 내용을 직접 편집합니다. {{ 변수 }}는 재무 데이터에서 자동으로 채워집니다.")

    slides_dir = PROJECT_ROOT / "content" / "slides"
    defaults_path = PROJECT_ROOT / "content" / "_defaults.yaml"

    # Load defaults
    defaults = load_yaml(defaults_path)

    st.subheader("기본 정보")
    col1, col2 = st.columns(2)
    with col1:
        defaults["company_name"] = st.text_input("회사명", value=defaults.get("company_name", ""))
        defaults["tagline"] = st.text_input("태그라인", value=defaults.get("tagline", ""))
    with col2:
        defaults["round"] = st.text_input("라운드", value=defaults.get("round", ""))
        defaults["round_size"] = st.text_input("투자 규모", value=defaults.get("round_size", ""))

    if st.button("💾 기본 정보 저장"):
        save_yaml(defaults_path, defaults)
        st.success("저장되었습니다!")

    st.divider()

    # Load all slides
    if slides_dir.exists():
        slide_files = sorted(slides_dir.glob("*.md"))

        if slide_files:
            st.subheader("슬라이드 목록")

            for i, sf in enumerate(slide_files):
                slide = load_slide(sf)
                fm = slide["front_matter"]
                title = fm.get("title", sf.stem)
                layout = fm.get("layout", "content")
                audiences = fm.get("audiences", ["internal", "external"])

                with st.expander(f"**{i+1}. {title}** ({layout}) — {', '.join(audiences)}", expanded=False):
                    # Edit title
                    new_title = st.text_input(
                        "슬라이드 제목", value=title, key=f"title_{i}"
                    )
                    fm["title"] = new_title

                    # Edit layout
                    layout_options = ["title", "content", "two_column", "metric_highlight", "table"]
                    new_layout = st.selectbox(
                        "레이아웃",
                        layout_options,
                        index=layout_options.index(layout) if layout in layout_options else 1,
                        key=f"layout_{i}",
                    )
                    fm["layout"] = new_layout

                    # Edit audiences
                    new_audiences = st.multiselect(
                        "대상",
                        ["internal", "external"],
                        default=audiences,
                        key=f"audience_{i}",
                    )
                    fm["audiences"] = new_audiences

                    # Edit body
                    new_body = st.text_area(
                        "내용 (Markdown + {{ 변수 }} 사용 가능)",
                        value=slide["body"],
                        height=200,
                        key=f"body_{i}",
                    )

                    # Variables hint
                    st.caption("사용 가능한 변수: `{{ company_name }}`, `{{ total_revenue_2025 | currency }}`, `{{ gross_margin_2026 | percent }}`, `{{ nrr }}` 등")

                    # Save individual slide
                    if st.button(f"💾 저장", key=f"save_{i}"):
                        save_slide(sf, fm, new_body)
                        st.success(f"'{new_title}' 슬라이드가 저장되었습니다!")

            # Add new slide
            st.divider()
            st.subheader("새 슬라이드 추가")
            col1, col2 = st.columns(2)
            with col1:
                new_slide_title = st.text_input("새 슬라이드 제목", key="new_title")
            with col2:
                new_slide_layout = st.selectbox(
                    "레이아웃 선택",
                    ["content", "title", "two_column", "metric_highlight", "table"],
                    key="new_layout",
                )
            if st.button("➕ 슬라이드 추가") and new_slide_title:
                next_num = len(slide_files) + 1
                slug = new_slide_title.lower().replace(" ", "-")[:30]
                new_path = slides_dir / f"{next_num:02d}-{slug}.md"
                save_slide(
                    new_path,
                    {"layout": new_slide_layout, "audiences": ["internal", "external"], "title": new_slide_title},
                    f"## {new_slide_title}\n\n내용을 입력하세요.",
                )
                st.success(f"'{new_slide_title}' 슬라이드가 추가되었습니다!")
                st.rerun()


# ===================================================
# 📋 덱 구성 페이지
# ===================================================
elif page == "📋 덱 구성":
    st.title("📋 덱 구성")
    st.caption("어떤 슬라이드를 어떤 순서로 포함할지 설정합니다")

    decks_dir = PROJECT_ROOT / "content" / "decks"
    slides_dir = PROJECT_ROOT / "content" / "slides"

    # Available slides
    available_slides = sorted([f.name for f in slides_dir.glob("*.md")]) if slides_dir.exists() else []

    if decks_dir.exists():
        deck_files = sorted(decks_dir.glob("*.yaml"))

        for df in deck_files:
            deck = load_yaml(df)
            deck_name = deck.get("name", df.stem)

            with st.expander(f"**{deck_name}** — {deck.get('description', '')}", expanded=True):
                deck["name"] = st.text_input("덱 이름", value=deck_name, key=f"dname_{df.stem}")
                deck["description"] = st.text_input("설명", value=deck.get("description", ""), key=f"ddesc_{df.stem}")

                # Slide selection and ordering
                current_slides = deck.get("slides", [])
                selected = st.multiselect(
                    "포함할 슬라이드 (순서대로 선택)",
                    available_slides,
                    default=[s for s in current_slides if s in available_slides],
                    key=f"dslides_{df.stem}",
                )
                deck["slides"] = selected

                st.caption(f"현재 {len(selected)}장 선택됨")

                if st.button(f"💾 '{deck_name}' 저장", key=f"dsave_{df.stem}"):
                    save_yaml(df, deck)
                    st.success("덱 구성이 저장되었습니다!")


# ===================================================
# ⬇️ PPT 내보내기 페이지
# ===================================================
elif page == "⬇️ PPT 내보내기":
    st.title("⬇️ PPT 내보내기")
    st.caption("현재 저장된 콘텐츠와 재무 데이터로 PPT를 생성합니다")

    decks_dir = PROJECT_ROOT / "content" / "decks"
    deck_files = sorted(decks_dir.glob("*.yaml")) if decks_dir.exists() else []

    deck_options = {df.stem: df for df in deck_files}
    deck_options["전체 슬라이드"] = None

    selected_deck = st.selectbox("내보낼 덱 선택", list(deck_options.keys()))

    audience_filter = st.selectbox("대상 필터", ["전체", "external", "internal"])

    if st.button("🔨 PPT 생성", type="primary", use_container_width=True):
        with st.spinner("PPT를 생성하고 있습니다..."):
            try:
                from ir_generator.builder import build_deck
                from ir_generator.models import BuildConfig

                config = BuildConfig(
                    deck_name=selected_deck if selected_deck != "전체 슬라이드" else None,
                    audience=audience_filter if audience_filter != "전체" else None,
                    output_dir=PROJECT_ROOT / "output",
                )
                result = build_deck(PROJECT_ROOT, config)

                # Provide download
                with open(result, "rb") as f:
                    pptx_bytes = f.read()

                st.success(f"PPT가 생성되었습니다! ({len(pptx_bytes) // 1024}KB)")

                st.download_button(
                    label="📥 PPT 다운로드",
                    data=pptx_bytes,
                    file_name=f"{selected_deck or 'deck'}.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PPT 생성 실패: {e}")

    st.divider()
    st.subheader("미리보기")
    st.info("위에서 PPT를 생성하면 다운로드 버튼이 나타납니다. 다운로드한 파일을 PowerPoint나 Google Slides에서 열어 확인하세요.")
