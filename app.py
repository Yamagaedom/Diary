"""Warm, accessible Streamlit interface for the Mood Diary MVP."""

from __future__ import annotations

from datetime import datetime
from html import escape

import streamlit as st

from mood_diary.ai import OpenAIEmotionAnalyzer
from mood_diary.crisis import CRISIS_GUIDANCE
from mood_diary.errors import AppError
from mood_diary.service import DiaryService
from mood_diary.storage import JsonDiaryRepository


st.set_page_config(
    page_title="마음결 · AI 공감 다이어리",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)


APP_CSS = """
<style>
:root {
  --paper: #fbf7ef;
  --paper-deep: #f4ecdf;
  --ink: #332f2a;
  --ink-soft: #6b6259;
  --apricot: #e99470;
  --apricot-deep: #a94e2f;
  --apricot-wash: #fae3d7;
  --sage: #80957a;
  --sage-deep: #435d47;
  --sage-wash: #e5ece1;
  --line: #ded4c6;
  --danger: #9b3838;
  --focus: #2d6146;
  --shadow: 0 16px 45px rgba(75, 59, 43, .08);
}

html, body, [class*="css"] { color: var(--ink); }
.stApp {
  background:
    radial-gradient(circle at 7% 7%, rgba(233, 148, 112, .12), transparent 28rem),
    radial-gradient(circle at 94% 26%, rgba(128, 149, 122, .12), transparent 25rem),
    var(--paper);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMain"] { overflow-x: clip; }
.block-container { max-width: 1120px; padding: 2.1rem 2.5rem 5rem; }

h1, h2, h3 { color: var(--ink) !important; letter-spacing: -.035em; }
h1 { font-size: clamp(2.1rem, 5vw, 3.65rem) !important; line-height: 1.12 !important; }
h2 { margin-top: .35rem !important; }
p, label, input, textarea, button { line-height: 1.72 !important; }

.brand-row { display: flex; align-items: center; gap: .65rem; margin-bottom: 2.4rem; }
.brand-mark {
  display: inline-grid; place-items: center; width: 2.35rem; height: 2.35rem;
  border-radius: 50%; background: var(--sage-deep); color: white; font-size: 1.05rem;
  box-shadow: 0 5px 16px rgba(67, 93, 71, .18);
}
.brand-name { font-weight: 760; font-size: 1.08rem; letter-spacing: -.02em; }
.brand-note { color: var(--ink-soft); font-size: .82rem; margin-left: auto; }
.eyebrow {
  color: var(--apricot-deep); font-size: .78rem; font-weight: 800;
  letter-spacing: .13em; text-transform: uppercase; margin-bottom: .6rem;
}
.hero-copy { max-width: 670px; color: var(--ink-soft); font-size: 1.08rem; margin: .7rem 0 2rem; }
.privacy-note {
  display: inline-flex; gap: .5rem; align-items: center; padding: .6rem .85rem;
  background: rgba(229, 236, 225, .72); border: 1px solid #cbd8c5;
  border-radius: 999px; color: var(--sage-deep); font-size: .84rem; font-weight: 650;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: .35rem; border-bottom: 1px solid var(--line); margin: 2.1rem 0 1.25rem;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  height: 3rem; padding: 0 1.15rem; color: var(--ink-soft); font-weight: 700;
}
[data-testid="stTabs"] [aria-selected="true"] { color: var(--sage-deep); }
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: var(--sage-deep); }

[data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(255, 253, 248, .82); border-color: var(--line) !important;
  border-radius: 22px !important; box-shadow: var(--shadow);
}
[data-testid="stTextArea"] textarea {
  min-height: 230px; color: var(--ink); background: #fffdf8;
  border: 1px solid #cfc2b3; border-radius: 14px; line-height: 1.85 !important;
  font-size: 1rem; padding: 1rem 1.05rem;
}
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--focus); box-shadow: 0 0 0 3px rgba(45, 97, 70, .18);
}

.stButton > button, [data-testid="stFormSubmitButton"] > button {
  min-height: 3rem; border-radius: 999px; font-weight: 760; transition: transform .16s ease, box-shadow .16s ease;
}
[data-testid="stFormSubmitButton"] > button {
  color: #fff; background: var(--sage-deep); border: 1px solid var(--sage-deep);
  box-shadow: 0 8px 18px rgba(67, 93, 71, .17);
}
[data-testid="stFormSubmitButton"] > button:hover {
  color: #fff; background: #354d3a; border-color: #354d3a; transform: translateY(-1px);
}
.stButton > button:focus-visible, [data-testid="stFormSubmitButton"] > button:focus-visible,
[role="tab"]:focus-visible, summary:focus-visible {
  outline: 3px solid var(--focus) !important; outline-offset: 3px;
}

.result-kicker { color: var(--sage-deep); font-size: .8rem; font-weight: 800; letter-spacing: .1em; }
.emotion-row { display: flex; flex-wrap: wrap; gap: .45rem; margin: .45rem 0 .8rem; }
.emotion-pill {
  display: inline-block; padding: .35rem .72rem; border-radius: 999px;
  background: var(--apricot-wash); color: #713923; font-weight: 760; font-size: .88rem;
}
.intensity { color: var(--ink-soft); font-size: .9rem; margin: -.25rem 0 1.15rem; }
.section-rule { width: 2.25rem; border-top: 2px solid var(--apricot); margin: .25rem 0 1rem; }
.crisis-title { font-size: 1.05rem; font-weight: 820; color: var(--danger); margin-bottom: .25rem; }
.empty-state { text-align: center; padding: 2rem .75rem 2.4rem; color: var(--ink-soft); }
.empty-icon { font-size: 2rem; margin-bottom: .6rem; }
.footer-note { color: var(--ink-soft); font-size: .78rem; margin-top: 2.75rem; text-align: center; }

[data-testid="stAlert"] { border-radius: 14px; }
[data-testid="stExpander"] {
  background: rgba(255, 253, 248, .8); border: 1px solid var(--line);
  border-radius: 16px; margin-bottom: .75rem; overflow: hidden;
}
[data-testid="stExpander"] summary { min-height: 3.25rem; }
hr { border-color: var(--line) !important; }

@media (max-width: 768px) {
  .block-container { padding: 1.25rem 1.2rem 3.5rem; }
  .brand-row { margin-bottom: 1.65rem; }
  .brand-note { display: none; }
  .hero-copy { font-size: 1rem; }
  [data-testid="stTabs"] [data-baseweb="tab"] { flex: 1; padding-inline: .6rem; }
  [data-testid="stTextArea"] textarea { min-height: 205px; }
  [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
}
@media (max-width: 420px) {
  .block-container { padding: .95rem .8rem 3rem; }
  .privacy-note { border-radius: 14px; align-items: flex-start; }
  [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 17px !important; }
  [data-testid="stTabs"] [data-baseweb="tab"] { font-size: .92rem; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; animation: none !important; }
}
</style>
"""

st.markdown(APP_CSS, unsafe_allow_html=True)


@st.cache_resource
def get_service() -> DiaryService:
    """Build the application boundary once; no API request happens here."""
    return DiaryService(OpenAIEmotionAnalyzer.from_env(), JsonDiaryRepository())


def format_timestamp(value: datetime) -> str:
    return value.astimezone().strftime("%Y년 %m월 %d일 · %H:%M")


def show_crisis_guidance() -> None:
    st.error("도움이 급히 필요한 순간일 수 있어요", icon="☎️")
    st.markdown('<p class="crisis-title">지금의 안전이 가장 중요해요.</p>', unsafe_allow_html=True)
    st.write(CRISIS_GUIDANCE)
    st.caption("AI의 답장은 전문적인 진단이나 응급 지원을 대신하지 않습니다.")


def show_analysis(analysis, *, heading: str = "마음 답장") -> None:
    """Render validated model fields through Streamlit's escaped text components."""
    with st.container(border=True):
        st.markdown('<p class="result-kicker">AI가 함께 살펴본 마음</p>', unsafe_allow_html=True)
        st.subheader(heading)
        pills = "".join(
            f'<span class="emotion-pill">{escape(emotion)}</span>' for emotion in analysis.emotions
        )
        st.markdown(f'<div class="emotion-row">{pills}</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="intensity">감정의 선명도 <strong>{analysis.intensity} / 5</strong></p>', unsafe_allow_html=True)

        st.markdown("**오늘의 마음 한 줄**")
        st.write(analysis.summary)
        st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
        st.markdown("**당신에게 건네는 공감**")
        st.write(analysis.empathy)
        st.info(analysis.comfort, icon="🌿")
        st.markdown("**오늘을 위한 작은 한 걸음**")
        st.write(analysis.suggestion)

    if analysis.crisis:
        show_crisis_guidance()


def show_page_intro() -> None:
    st.markdown(
        """
        <div class="brand-row">
          <span class="brand-mark" aria-hidden="true">결</span>
          <span class="brand-name">마음결</span>
          <span class="brand-note">나만의 기기에 조용히 남기는 마음 기록</span>
        </div>
        <p class="eyebrow">오늘의 마음 기록</p>
        """,
        unsafe_allow_html=True,
    )
    st.title("오늘의 마음에,\n잠시 머물러 보세요")
    st.markdown(
        '<p class="hero-copy">잘 쓰려고 애쓰지 않아도 괜찮아요. 오늘 있었던 일을 편안히 적으면, AI가 감정의 결을 살피고 다정한 답장을 건넬게요.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="privacy-note"><span aria-hidden="true">⌂</span><span>작성한 일기는 이 기기의 로컬 파일에만 저장돼요.</span></div>',
        unsafe_allow_html=True,
    )


show_page_intro()

try:
    service = get_service()
except AppError as exc:
    st.error(exc.user_message, icon="⚙️")
    st.info("프로젝트 폴더의 `.env`에 `OPENAI_API_KEY`를 설정한 뒤 앱을 다시 시작해 주세요. 키 값은 화면에 표시되지 않아요.")
    st.markdown('<p class="footer-note">마음결은 의료·심리 진단 서비스가 아닙니다.</p>', unsafe_allow_html=True)
    st.stop()


write_tab, history_tab = st.tabs(["✎  오늘 작성", "▤  지난 기록"])

with write_tab:
    with st.container(border=True):
        st.subheader("오늘, 어떤 일이 있었나요?")
        st.caption("떠오르는 대로 적어도 충분해요. 1자 이상 5,000자 이하로 작성해 주세요.")
        with st.form("diary_form", clear_on_submit=False):
            content = st.text_area(
                "오늘의 일기",
                height=230,
                max_chars=5000,
                placeholder="예: 퇴근길에 문득 지쳤다는 생각이 들었어요. 그래도 친구가 건넨 따뜻한 말이 오래 남았어요…",
                key="diary_draft",
                help="민감한 개인정보는 필요한 만큼만 적어 주세요.",
            )
            st.caption(f"{len(content):,} / 5,000자")
            submitted = st.form_submit_button("내 마음 들여다보기", use_container_width=True)

    if submitted:
        if not content.strip():
            st.error("오늘 있었던 일을 한 글자 이상 적어 주세요.", icon="✍️")
        else:
            try:
                with st.spinner("마음을 조심스럽게 살펴보고 있어요… 잠시만 기다려 주세요."):
                    st.session_state["latest_entry"] = service.create(content)
                st.success("오늘의 마음을 안전하게 기록했어요.", icon="✅")
            except AppError as exc:
                st.error(exc.user_message, icon="⚠️")
                if exc.retryable:
                    st.caption("작성한 내용은 그대로 두었어요. 잠시 후 같은 버튼을 다시 눌러 주세요.")

    latest_entry = st.session_state.get("latest_entry")
    if latest_entry is not None:
        show_analysis(latest_entry.analysis)

with history_tab:
    st.subheader("천천히 쌓여 온 마음")
    st.caption("최근 기록부터 최대 100개까지 보여드려요.")
    try:
        entries = service.recent()
        if not entries:
            with st.container(border=True):
                st.markdown(
                    '<div class="empty-state"><div class="empty-icon" aria-hidden="true">❦</div><strong>아직 남겨진 기록이 없어요.</strong><br>오늘의 첫 마음부터 천천히 시작해 보세요.</div>',
                    unsafe_allow_html=True,
                )
        for entry in entries:
            title = f"{format_timestamp(entry.created_at)}  ·  {' · '.join(entry.analysis.emotions)}"
            with st.expander(title):
                st.markdown("**그날의 기록**")
                st.write(entry.content)
                show_analysis(entry.analysis, heading="그날의 마음 답장")
                st.divider()
                st.caption("삭제하면 되돌릴 수 없어요. 아래 확인란을 먼저 선택해 주세요.")
                confirm = st.checkbox("이 기록을 영구적으로 삭제할게요", key=f"confirm-{entry.id}")
                if st.button(
                    "기록 삭제",
                    key=f"delete-{entry.id}",
                    disabled=not confirm,
                    type="secondary",
                    help="확인란을 선택한 뒤 삭제할 수 있어요.",
                ):
                    try:
                        deleted = service.delete(entry.id)
                        if deleted:
                            if getattr(st.session_state.get("latest_entry"), "id", None) == entry.id:
                                del st.session_state["latest_entry"]
                            st.toast("기록을 삭제했어요.", icon="✅")
                            st.rerun()
                        else:
                            st.warning("이미 삭제되었거나 찾을 수 없는 기록이에요.")
                    except AppError as exc:
                        st.error(exc.user_message)
    except AppError as exc:
        st.error(exc.user_message, icon="⚠️")
        if exc.retryable:
            st.caption("잠시 후 페이지를 새로고침해 주세요.")

st.markdown(
    '<p class="footer-note">AI의 답장은 감정을 정리하기 위한 참고이며 의료·심리 진단을 대신하지 않습니다.</p>',
    unsafe_allow_html=True,
)
