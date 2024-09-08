from datetime import datetime, timedelta
import pytz

import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="ONLYONE FAIR Score Board",
    page_icon="🏆",  # This is an emoji shortcode. Could be a URL too.🥇🏆🎖️
)

with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 폰트 파일 경로 (로컬)
font_url_body_light = './font/CJ ONLYONE NEW body Light.ttf'
font_url_body_regular = './font/CJ ONLYONE NEW body Regular.ttf'
font_url_title_bold = './font/CJ ONLYONE NEW title Bold.ttf'
font_url_title_medium = './font/CJ ONLYONE NEW title Medium.ttf'

# HTML/CSS로 폰트 적용
st.markdown(f"""
    <style>
        @font-face {{
            font-family: 'CJFont_bl';
            src: url('{font_url_body_light}');
        }}
        @font-face {{
            font-family: 'CJFont_br';
            src: url('{font_url_body_regular}');
        }}
        @font-face {{
            font-family: 'CJFont_tb';
            src: url('{font_url_title_bold}');
        }}
        @font-face {{
            font-family: 'CJFont_tm';
            src: url('{font_url_title_medium}');
        }}
        .custom-font {{
            font-family: 'CJFont_bl', sans-serif;
        }}
        .stDataFrame {{
            font-family: 'CJFont_bl', sans-serif;
        }}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------

def connect_supabase():
    # Supabase 프로젝트의 URL과 키를 여기에 입력하세요
    SUPABASE_URL = "https://mvqxuteltnxhbwvgxzlb.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12cXh1dGVsdG54aGJ3dmd4emxiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjM0NTkxNDMsImV4cCI6MjAzOTAzNTE0M30.NIYa3m8HA_31Fjgzr52IScmUjA1o-uEW1V7uU_DW2Pw"

    # Supabase 클라이언트 생성
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Supabase 클라이언트 반환
    return supabase

# 쿼리 : 전 사원 스코어
def load_data_s(supabase):
    """Loads the inventory data from the Supabase database."""

    try:
        # Score_Info 테이블에서 데이터 쿼리
        query = """
                WITH Score_Summary AS (
                    SELECT
                        A.id,
                        SUM(A.SCORE) AS 총점,
                        SUM(CASE WHEN A.quiz_dvcd IN (3, 4) THEN A.SCORE ELSE 0 END) AS 입실포인트,
                        SUM(CASE WHEN A.quiz_dvcd = 2 THEN A.SCORE ELSE 0 END) AS 퀴즈포인트,
                        SUM(CASE WHEN A.quiz_dvcd = 14 THEN A.SCORE ELSE 0 END) AS 미션포인트,
                        SUM(CASE WHEN A.quiz_dvcd = 5 THEN A.SCORE ELSE 0 END) AS 대표작질문포인트
                    FROM "Score_Info" A
                    GROUP BY A.id
                )
                SELECT
                    S.id,
                    S.총점,
                    RANK() OVER (ORDER BY S.총점 DESC) AS 순위,
                    P.name AS 이름,
                    P.company AS 소속사,
                    S.입실포인트,
                    S.퀴즈포인트,
                    S.미션포인트,
                    S.대표작질문포인트
                FROM
                    Score_Summary S
                JOIN
                    "Peer_Info" P ON S.id = P.id
                ORDER BY
                    S.총점 DESC
               """

        # Supabase의 SQL 기능을 사용해 쿼리 실행
        response = supabase.rpc('execute_query', {'query': query}).execute()

        # 응답에서 데이터 추출
        data = response.data

        if not data:
            return None

        # Pandas DataFrame으로 변환
        df = pd.DataFrame(data)
        df = df.astype({
                        'id': 'int64',
                        '총점': 'float64',
                        '순위': 'int64',
                        '이름': 'str',
                        '소속사': 'str',
                        '입실포인트': 'float64',
                        '퀴즈포인트': 'float64',
                        '미션포인트': 'float64',
                        '대표작질문포인트': 'float64'
                    })
        df = df.drop(columns=['id'])
        df['총점'] = df['총점'].astype(int)
        df['이름'] = df['이름'] + '님'
        df = df.sort_values(by='총점', ascending=False)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    return df

# -----------------------------------------------------------------------------
# Draw the actual page, starting with the inventory table.

# Set the title that appears at the top of the page.
"""
# 📊 ONLYONE FAIR Scoreboard 
"""
"""
"""
# st.markdown("""
# <div style="font-family: 'CJFont_tb'; font-size: 24px;">📊 ONLYONE FAIR Scoreboard <br></div>
# """, unsafe_allow_html=True)

# **Welcome to Alice's Corner Store's intentory tracker!**
# This page reads and writes directly from/to our inventory database.

st.info(
    """
    실시간 포인트를 확인하시려면 화면을 새로고침하세요\n
    실시간 포인트 보기는 11:30에 종료됩니다\n 
    14:00에 진행되는 라디오 코너에서 순위별 시상식이 있습니다 😀 
    """
)
st.balloons()

# st.info(
#     """
#     😀
#     """
# )

# Connect to database
supabase = connect_supabase()

# Load data from database
df_s = load_data_s(supabase)

st.markdown("<h3><br>포인트 확인하기</h3>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

with st.popover("이름으로 검색하기 👋"):
    st.markdown("이름으로 검색하기 👋")
    name = st.text_input("전체 인원을 보려면 빈 칸 입력")
    if name:
        filtered_df = df_s[df_s['이름'] == f"{name}님"]
    else:
        filtered_df = df_s


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["순위", "전체", "클래스", "퀴즈", "미션", "대표작질문"])
tab1_df = filtered_df.drop(columns=['입실포인트', '퀴즈포인트', '미션포인트', '대표작질문포인트'])
tab2_df = filtered_df.drop(columns=['총점', '순위'])

with tab1:
     edited_df = st.data_editor(
        tab1_df,
        use_container_width=True,
        column_config={
            "총점": st.column_config.ProgressColumn(
                "총점",
                format="%i",
                min_value=0,
                max_value=3000,
            ),
        },
        hide_index=True,
        # Disable editing the ID and Date Submitted columns.
        disabled=["ID", "Date Submitted"]
     )
with tab2:
     edited_df = st.data_editor(
        tab2_df,
        use_container_width=True,
        column_config={
            "입실포인트": st.column_config.ProgressColumn(
                "입실포인트",
                help="체류시간에 따른 포인트입니다.",
                format="%i",
                min_value=0,
                max_value=1260,
            ),
            "퀴즈포인트": st.column_config.ProgressColumn(
                "퀴즈포인트",
                help="클래스 퀴즈에 따른 포인트입니다.",
                format="%i",
                min_value=0,
                max_value=300,
            ),
            "미션포인트": st.column_config.ProgressColumn(
                "미션포인트",
                help="디지털비전보드 포인트입니다.",
                format="%i",
                min_value=0,
                max_value=200,
            ),
            "대표작질문포인트": st.column_config.ProgressColumn(
                "대표작질문포인트",
                help="대표작질문포인트에 따른 포인트입니다.",
                format="%i",
                min_value=0,
                max_value=300,
            )
        },
        hide_index=True,
        # Disable editing the ID and Date Submitted columns.
        disabled=["ID", "Date Submitted"]
     )
with tab3:
    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        column_config={
            "총점": st.column_config.ProgressColumn(
                "총점",
                format="%i",
                min_value=0,
                max_value=3000,
            ),
            "입실포인트": st.column_config.ProgressColumn(
                "입실포인트",
                help="체류시간에 따른 포인트입니다.",
                format="%i",
                min_value=0,
                max_value=1260,
            ),
            "퀴즈포인트": st.column_config.ProgressColumn(
                "퀴즈포인트",
                help="클래스 퀴즈에 따른 포인트입니다.",
                format="%i",
                min_value=0,
                max_value=300,
            ),
            "미션포인트": st.column_config.ProgressColumn(
                "미션포인트",
                help="디지털비전보드 포인트입니다.",
                format="%i",
                min_value=0,
                max_value=200,
            ),
            "대표작질문포인트": st.column_config.ProgressColumn(
                "대표작질문포인트",
                help="대표작질문포인트에 따른 포인트입니다.",
                format="%i",
                min_value=0,
                max_value=300,
            ),
        },
        hide_index=True,
        # Disable editing the ID and Date Submitted columns.
        disabled=["ID", "Date Submitted"],
    )

def load_p(supabase):
    response = supabase.table("Entrance_Info").select("*").in_("enter_dvcd", [10,11,12]).execute()

    df = pd.DataFrame(response.data)
    #df = df.dropna()

    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    five_minutes_ago = datetime.now(pytz.utc) - timedelta(minutes=5)

    df_filtered = df[df['created_at'] > five_minutes_ago] # 최근 5분 이내
    df_enter = df_filtered[(df_filtered['enter_dvcd'] == 10)]
    df_exit = df_filtered[(df_filtered['enter_dvcd'] == 11)]

    return {
        'count_cj': df[(df['exit_yn'] == False) & (df['company_dvcd'] == 5)].shape[0],
        'count_log': df[(df['exit_yn'] == False) & (df['company_dvcd'] == 6)].shape[0],
        'count_oy': df[(df['exit_yn'] == False) & (df['company_dvcd'] == 7)].shape[0],
        'count_enm': df[(df['exit_yn'] == False) & (df['company_dvcd'] == 8)].shape[0],
        'count_ons': df[(df['exit_yn'] == False) & (df['company_dvcd'] == 9)].shape[0],
        'count_cms': df[(df['exit_yn'] == False) & (df['company_dvcd'] == 13)].shape[0],

        'diff_cj': df_enter[(df_enter['company_dvcd'] == 5)].shape[0] - df_exit[(df_exit['company_dvcd'] == 5)].shape[0],
        'diff_log': df_enter[(df_enter['company_dvcd'] == 6)].shape[0] - df_exit[(df_exit['company_dvcd'] == 6)].shape[0],
        'diff_oy': df_enter[(df_enter['company_dvcd'] == 7)].shape[0] - df_exit[(df_exit['company_dvcd'] == 7)].shape[0],
        'diff_enm': df_enter[(df_enter['company_dvcd'] == 8)].shape[0] - df_exit[(df_exit['company_dvcd'] == 8)].shape[0],
        'diff_ons': df_enter[(df_enter['company_dvcd'] == 9)].shape[0] - df_exit[(df_exit['company_dvcd'] == 9)].shape[0],
        'diff_cms': df_enter[(df_enter['company_dvcd'] == 13)].shape[0] - df_exit[(df_exit['company_dvcd'] ==13)].shape[0]
    }
plot_data = load_p(supabase)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3><br>클래스별 입장 인원</h3>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("CJ제일제당", plot_data['count_cj'], plot_data['diff_cj'])
col2.metric("CJ대한통운", plot_data['count_log'], plot_data['diff_log'])
col3.metric("CJ올리브영", plot_data['count_oy'], plot_data['diff_oy'])

col4, col5, col6 = st.columns(3)
col4.metric("CJ ENM 엔터테인먼트부문", plot_data['count_enm'], plot_data['diff_enm'])
col5.metric("CJ ENM 커머스부문", plot_data['count_cms'], plot_data['diff_cms'])
col6.metric("CJ올리브네트웍스", plot_data['count_ons'], plot_data['diff_ons'])
