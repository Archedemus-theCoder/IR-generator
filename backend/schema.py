"""Rovothome IR slide data schema — all 15+ slides."""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


# --- Reusable field types ---

class KpiCard(BaseModel):
    label: str = ""
    value: str = ""

class DataCard(BaseModel):
    label: str = ""
    value: str = ""
    sub: str = ""

class ContactInfo(BaseModel):
    name: str = "윤세용"
    phone: str = "010-7900-5910"
    email: str = "leo.yun@rovothome.com"

class TeamMember(BaseModel):
    name: str = ""
    title: str = ""
    bio: str = ""

class PhaseItem(BaseModel):
    phase: str = ""
    period: str = ""
    description: str = ""

class PLRow(BaseModel):
    label: str = ""
    values: dict[str, str] = Field(default_factory=dict)  # year -> value


# --- Slide models ---

class SlideCover(BaseModel):
    company_name: str = "Rovothome"
    tagline: str = "당신의 삶을 바꾸는 로봇, 그리고 홈"
    kpis: list[KpiCard] = Field(default_factory=lambda: [
        KpiCard(label="계약·협의 파이프라인", value="240억+"),
        KpiCard(label="정부지원사업", value="45억원+"),
        KpiCard(label="Pre-A 모집", value="125억/40억"),
    ])
    contact: ContactInfo = Field(default_factory=ContactInfo)

class SlideProblem(BaseModel):
    section_label: str = "The Problem"
    headline: str = "부족한 도심의 공간은 이미 억 단위를 넘어섰고,\n주거비는 계속 상승하고 있습니다."
    body: str = "도시 인구 밀도가 높아지면서 개인 공간 부족 문제가 심화되고 있습니다."
    data_cards: list[DataCard] = Field(default_factory=lambda: [
        DataCard(label="호텔 월 숙박료", value="293만원/월"),
        DataCard(label="주택 매매가", value="1억원"),
        DataCard(label="주택 월 임대료", value="28만원/월"),
    ])

class SlideSolution(BaseModel):
    section_label: str = "The Solution"
    headline: str = "한정된 면적을 최대로 활용하는 것입니다.\n천장이나 벽을 이동시켜 새로운 공간을 만들어냅니다."
    left_title: str = "Ceily"
    left_desc: str = "천장 이동 로보틱스 시스템\n천장 리프트 침대로 공간 활용 극대화"
    right_title: str = "Wally"
    right_desc: str = "벽면 이동 로보틱스 시스템\n슬라이딩 워드로브로 공간 분리"

class SlideWhyNow(BaseModel):
    section_label: str = "Why Now"
    headline: str = "도시 공간 문제가 임계점을 넘어선 지금,\n기술적 해결이 가능해졌습니다."
    points: list[DataCard] = Field(default_factory=lambda: [
        DataCard(label="도시화 가속", value="", sub="전 세계 도시 인구 비율 56% 돌파"),
        DataCard(label="기술 성숙", value="", sub="IoT, 로보틱스, AI 융합 기술 상용화 단계"),
        DataCard(label="주거비 위기", value="", sub="서울 평균 아파트 가격 10억 돌파"),
    ])

class SlideMarketSize(BaseModel):
    section_label: str = "Market Size"
    headline: str = "글로벌 스마트 가구 시장은 빠르게 성장하고 있습니다."
    tam: KpiCard = Field(default_factory=lambda: KpiCard(label="TAM", value="$45B"))
    sam: KpiCard = Field(default_factory=lambda: KpiCard(label="SAM", value="$12B"))
    som: KpiCard = Field(default_factory=lambda: KpiCard(label="SOM", value="$500M"))
    growth_note: str = "CAGR 18% 성장 전망"

class SlideBusinessModel(BaseModel):
    section_label: str = "Business Model"
    headline: str = "B2B 로보톰 인사이드형:\n파트너의 영업력을 통해 대규모 공급 시장으로 빠르게 확장합니다."
    model_types: list[DataCard] = Field(default_factory=lambda: [
        DataCard(label="B2B 인사이드형", value="가구사/건설사 파트너십", sub="초기 개발비 + 지속적 HW 공급 수익"),
        DataCard(label="호텔 렌탈형", value="호텔/숙박업소 월정액", sub="월정액 렌탈 구독 모델"),
        DataCard(label="B2C 직접판매", value="프리미엄 라인 직판", sub="개인 고객 대상 고급 제품 직접 판매"),
    ])

class SlideTraction(BaseModel):
    section_label: str = "Traction & Pipeline"
    headline: str = "계약·협의 파이프라인 240억+,\n정부지원사업 45억원+ 수주"
    items: list[DataCard] = Field(default_factory=lambda: [
        DataCard(label="BDC 총판 계약", value="체결 완료", sub="일본 시장 진출 교두보"),
        DataCard(label="산와텔렘", value="협의 중", sub="부동산 개발사 파트너십"),
        DataCard(label="정부과제", value="45억원+", sub="다수 정부지원사업 수주"),
    ])

class SlideTechMoat(BaseModel):
    section_label: str = "Technology Moat"
    headline: str = "건축 융합 로봇 설계 역량을 기반으로\n장기적 구동 신뢰성을 확보하였습니다."
    moats: list[DataCard] = Field(default_factory=lambda: [
        DataCard(label="정밀 보정 구동", value="건축 오차 보정 메커니즘"),
        DataCard(label="내구성 설계", value="장기 처짐 보정 프레임"),
        DataCard(label="실시간 센싱", value="레일리스 평행 주행 보정"),
        DataCard(label="특허 포트폴리오", value="핵심 기술 특허 다수 보유"),
    ])

class SlideGTM(BaseModel):
    section_label: str = "Go-to-Market"
    headline: str = "Phase별 시장 진입 전략으로\n체계적으로 시장을 확대합니다."
    phases: list[PhaseItem] = Field(default_factory=lambda: [
        PhaseItem(phase="Phase 1", period="2025-2026", description="일본 엔트리 라인 진출\nBDC·산와텔렘 총판 채널"),
        PhaseItem(phase="Phase 2", period="2027-2028", description="국내 B2B 확대\n호텔/오피스텔 렌탈 모델"),
        PhaseItem(phase="Phase 3", period="2029+", description="글로벌 B2C 확장\n플랫폼 생태계 구축"),
    ])

class SlideRoadmap(BaseModel):
    section_label: str = "Business Roadmap"
    headline: str = "2단계 성장 전략으로\n빠른 시장 확대와 수익성을 동시에 추구합니다."
    phases: list[PhaseItem] = Field(default_factory=lambda: [
        PhaseItem(phase="Phase 1: Global Entry", period="2025-2027", description="일본 시장 엔트리 라인 대량 공급\n총판 계약 기반 안정적 매출 확보"),
        PhaseItem(phase="Phase 2: Platform", period="2028-2030", description="B2C 프리미엄 + 호텔 렌탈\n앱스토어 생태계 모델 전환"),
    ])

class SlidePL(BaseModel):
    section_label: str = "P&L Summary"
    headline: str = "2026년부터 본격 매출 발생,\n2028년 영업이익 흑자전환을 목표합니다."
    years: list[str] = Field(default_factory=lambda: ["2026", "2027", "2028", "2029"])
    rows: list[PLRow] = Field(default_factory=lambda: [
        PLRow(label="매출", values={"2026": "15억", "2027": "89억", "2028": "280억", "2029": "520억"}),
        PLRow(label="영업이익", values={"2026": "-18억", "2027": "-5억", "2028": "42억", "2029": "105억"}),
        PLRow(label="영업이익률", values={"2026": "-120%", "2027": "-6%", "2028": "15%", "2029": "20%"}),
    ])

class SlideInvestment(BaseModel):
    section_label: str = "투자 제안"
    headline: str = "Pre-A 라운드 40억원 투자를 제안드립니다."
    amount: str = "40억원"
    valuation: str = "Pre 125억"
    use_of_funds: list[DataCard] = Field(default_factory=lambda: [
        DataCard(label="R&D", value="50%", sub="제품 개발 및 양산 준비"),
        DataCard(label="해외 진출", value="30%", sub="일본 시장 진입 및 마케팅"),
        DataCard(label="운영", value="20%", sub="인력 충원 및 운영비"),
    ])

class SlideTeam(BaseModel):
    section_label: str = "Team"
    headline: str = "건축 + 로보틱스 + 비즈니스를 아우르는 팀"
    members: list[TeamMember] = Field(default_factory=lambda: [
        TeamMember(name="윤세용 (Leo)", title="CEO / Founder", bio="건축 융합 로봇 설계 전문\n前 삼성물산 건설부문"),
        TeamMember(name="COO", title="COO", bio="사업 개발 및 운영 총괄"),
    ])

class SlideClosing(BaseModel):
    section_label: str = "Rovothome"
    headline: str = "우리는 공간의 한계를 기술로 최적화한다."
    body: str = "공간을 확장하는 기술로, 더 높은 효율과 더 풍요로운 생활을 가능하게 합니다."
    contact: ContactInfo = Field(default_factory=ContactInfo)

# --- Optional slides ---

class SlideOptBMDetail(BaseModel):
    section_label: str = "Business Model Detail"
    headline: str = "호텔 렌탈형 상세 구조"
    body: str = "호텔/숙박업소에 로봇가구를 월정액으로 렌탈하여 안정적 반복 매출을 창출합니다."

class SlideOptTechDetail(BaseModel):
    section_label: str = "Technology Detail"
    headline: str = "4대 핵심 기술 드릴다운"
    body: str = "정밀 보정 구동, 내구성 설계, 실시간 센싱, 특허 포트폴리오의 기술 상세입니다."

class SlideOptCompetitor(BaseModel):
    section_label: str = "Competitive Landscape"
    headline: str = "글로벌 경쟁 구도와 Rovothome의 포지셔닝"
    body: str = "Ori Living(미국)이 주요 벤치마크. Rovothome은 건축 융합 설계 역량으로 차별화."


# --- Master IR document ---

class SlideConfig(BaseModel):
    id: str
    enabled: bool = True
    order: int = 0

class IRDocument(BaseModel):
    """전체 IR 문서 — 모든 슬라이드 데이터 + 설정"""
    # Slide order/visibility
    slide_config: list[SlideConfig] = Field(default_factory=lambda: [
        SlideConfig(id="cover", order=1),
        SlideConfig(id="problem", order=2),
        SlideConfig(id="solution", order=3),
        SlideConfig(id="why_now", order=4),
        SlideConfig(id="market_size", order=5),
        SlideConfig(id="business_model", order=6),
        SlideConfig(id="traction", order=7),
        SlideConfig(id="tech_moat", order=8),
        SlideConfig(id="gtm", order=9),
        SlideConfig(id="roadmap", order=10),
        SlideConfig(id="pl", order=11),
        SlideConfig(id="investment", order=12),
        SlideConfig(id="team", order=13),
        SlideConfig(id="closing", order=14),
        SlideConfig(id="opt_bm_detail", order=15, enabled=False),
        SlideConfig(id="opt_tech_detail", order=16, enabled=False),
        SlideConfig(id="opt_competitor", order=17, enabled=False),
    ])

    # Core slides
    cover: SlideCover = Field(default_factory=SlideCover)
    problem: SlideProblem = Field(default_factory=SlideProblem)
    solution: SlideSolution = Field(default_factory=SlideSolution)
    why_now: SlideWhyNow = Field(default_factory=SlideWhyNow)
    market_size: SlideMarketSize = Field(default_factory=SlideMarketSize)
    business_model: SlideBusinessModel = Field(default_factory=SlideBusinessModel)
    traction: SlideTraction = Field(default_factory=SlideTraction)
    tech_moat: SlideTechMoat = Field(default_factory=SlideTechMoat)
    gtm: SlideGTM = Field(default_factory=SlideGTM)
    roadmap: SlideRoadmap = Field(default_factory=SlideRoadmap)
    pl: SlidePL = Field(default_factory=SlidePL)
    investment: SlideInvestment = Field(default_factory=SlideInvestment)
    team: SlideTeam = Field(default_factory=SlideTeam)
    closing: SlideClosing = Field(default_factory=SlideClosing)

    # Optional slides
    opt_bm_detail: SlideOptBMDetail = Field(default_factory=SlideOptBMDetail)
    opt_tech_detail: SlideOptTechDetail = Field(default_factory=SlideOptTechDetail)
    opt_competitor: SlideOptCompetitor = Field(default_factory=SlideOptCompetitor)


# Slide ID → display name mapping
SLIDE_NAMES = {
    "cover": "01. Cover",
    "problem": "02. Problem",
    "solution": "03. Solution",
    "why_now": "04. Why Now",
    "market_size": "05. Market Size",
    "business_model": "06. Business Model",
    "traction": "07. Traction & Pipeline",
    "tech_moat": "08. Technology Moat",
    "gtm": "09. Go-to-Market",
    "roadmap": "10. Business Roadmap",
    "pl": "11. P&L Summary",
    "investment": "12. 투자 제안",
    "team": "13. Team",
    "closing": "14. Closing",
    "opt_bm_detail": "A. BM 상세",
    "opt_tech_detail": "B. 기술 상세",
    "opt_competitor": "C. 경쟁사 비교",
}
