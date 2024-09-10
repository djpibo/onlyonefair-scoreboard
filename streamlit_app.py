from datetime import datetime, timedelta
import pytz

import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="ONLYONE FAIR Score Board",
    page_icon="🏆",  # This is an emoji shortcode. Could be a URL too.🥇🏆🎖️
    layout="wide")

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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
                        SUM(CASE WHEN A.quiz_dvcd IN (3, 4) AND A.company_dvcd = 5 
                        THEN A.SCORE ELSE 0 END) AS 입실포인트CJ,
                        SUM(CASE WHEN A.quiz_dvcd IN (3, 4) AND A.company_dvcd = 6 
                        THEN A.SCORE ELSE 0 END) AS 입실포인트LOG,
                        SUM(CASE WHEN A.quiz_dvcd IN (3, 4) AND A.company_dvcd = 7
                         THEN A.SCORE ELSE 0 END) AS 입실포인트OY,
                        SUM(CASE WHEN A.quiz_dvcd IN (3, 4) AND A.company_dvcd = 8
                         THEN A.SCORE ELSE 0 END) AS 입실포인트ENM,
                        SUM(CASE WHEN A.quiz_dvcd IN (3, 4) AND A.company_dvcd = 9 
                        THEN A.SCORE ELSE 0 END) AS 입실포인트ONS,
                        SUM(CASE WHEN A.quiz_dvcd IN (3, 4) AND A.company_dvcd = 13 
                        THEN A.SCORE ELSE 0 END) AS 입실포인트CMS,
                        SUM(CASE WHEN A.quiz_dvcd = 1 THEN A.SCORE ELSE 0 END) AS 퀴즈포인트,
                        SUM(CASE WHEN A.quiz_dvcd = 1 AND A.company_dvcd = 5 THEN A.SCORE ELSE 0 END) AS 퀴즈포인트CJ,
                        SUM(CASE WHEN A.quiz_dvcd = 1 AND A.company_dvcd = 6 THEN A.SCORE ELSE 0 END) AS 퀴즈포인트LOG,
                        SUM(CASE WHEN A.quiz_dvcd = 1 AND A.company_dvcd = 7 THEN A.SCORE ELSE 0 END) AS 퀴즈포인트OY,
                        SUM(CASE WHEN A.quiz_dvcd = 1 AND A.company_dvcd = 8 THEN A.SCORE ELSE 0 END) AS 퀴즈포인트ENM,
                        SUM(CASE WHEN A.quiz_dvcd = 1 AND A.company_dvcd = 9 THEN A.SCORE ELSE 0 END) AS 퀴즈포인트ONS,
                        SUM(CASE WHEN A.quiz_dvcd = 1 AND A.company_dvcd = 13 THEN A.SCORE ELSE 0 END) AS 퀴즈포인트CMS,
                        SUM(CASE WHEN A.quiz_dvcd = 14 THEN A.SCORE ELSE 0 END) AS 미션포인트,
                        SUM(CASE WHEN A.quiz_dvcd = 2 THEN A.SCORE ELSE 0 END) AS 대표작질문포인트
                    FROM "Score_Info" A
                    GROUP BY A.id
                )
                SELECT
                    S.id,
                    S.총점,
                    P.name AS 이름,
                    P.company AS 소속사,
                    S.입실포인트,
                    S.입실포인트CJ,
                    S.입실포인트LOG,
                    S.입실포인트OY,
                    S.입실포인트ENM,
                    S.입실포인트ONS,
                    S.입실포인트CMS,
                    S.퀴즈포인트,
                    S.퀴즈포인트CJ,
                    S.퀴즈포인트LOG,
                    S.퀴즈포인트OY,
                    S.퀴즈포인트ENM,
                    S.퀴즈포인트ONS,
                    S.퀴즈포인트CMS,
                    S.미션포인트,
                    S.대표작질문포인트
                FROM
                    Score_Summary S
                JOIN
                    "Peer_Info" P ON S.id = P.id
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
                        '이름': 'str',
                        '소속사': 'str',
                        '입실포인트': 'float64',
                        '입실포인트cj': 'float64',
                        '입실포인트log': 'float64',
                        '입실포인트oy': 'float64',
                        '입실포인트enm': 'float64',
                        '입실포인트ons': 'float64',
                        '입실포인트cms': 'float64',
                        '퀴즈포인트': 'float64',
                        '퀴즈포인트cj': 'float64',
                        '퀴즈포인트log': 'float64',
                        '퀴즈포인트oy': 'float64',
                        '퀴즈포인트enm': 'float64',
                        '퀴즈포인트ons': 'float64',
                        '퀴즈포인트cms': 'float64',
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
st.balloons()
# st.markdown("""
# <div style="font-family: 'CJFont_tb'; font-size: 24px;">📊 ONLYONE FAIR Scoreboard <br></div>
# """, unsafe_allow_html=True)

# **Welcome to Alice's Corner Store's intentory tracker!**
# This page reads and writes directly from/to our inventory database.

st.info(
    """
    실시간 포인트를 확인하시려면 화면을 새로고침해주세요 🔄 \n
    14:00에 진행되는 라디오 코너에서 순위별 시상식이 있습니다 😀 
    """
)

# st.info(
#     """
#     실시간 포인트 보기는 11:00에 종료됐습니다.
#     14:00에 진행되는 라디오 코너에서 순위별 시상식이 있습니다 😀 
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
tab1_df = filtered_df[['이름', '소속사', '총점']]
tab2_df = filtered_df[['이름', '소속사', '총점', '입실포인트', '퀴즈포인트', '미션포인트', '대표작질문포인트']]
_tab3_df = filtered_df[['이름', '소속사', '입실포인트cj', '입실포인트log', '입실포인트oy', '입실포인트enm', '입실포인트cms', '입실포인트ons']]
tab3_df = _tab3_df.rename(columns={
    '입실포인트cj': 'CJ제일제당',
    '입실포인트log': 'CJ대한통운',
    '입실포인트oy': 'CJ올리브영',
    '입실포인트enm': 'CJ ENM 엔터',
    '입실포인트ons': 'CJ 올리브네트웍스',
    '입실포인트cms': 'CJ ENM 커머스',
})
_tab4_df = filtered_df[['이름', '소속사', '퀴즈포인트cj', '퀴즈포인트log', '퀴즈포인트oy', '퀴즈포인트enm', '퀴즈포인트cms', '퀴즈포인트ons']]

tab4_df = _tab4_df.rename(columns={
    '퀴즈포인트cj': 'CJ제일제당',
    '퀴즈포인트log': 'CJ대한통운',
    '퀴즈포인트oy': 'CJ올리브영',
    '퀴즈포인트enm': 'CJ ENM 엔터부문',
    '퀴즈포인트ons': 'CJ 올리브네트웍스',
    '퀴즈포인트cms': 'CJ ENM 커머스부문',
})
tab5_df = filtered_df[['이름', '소속사', '미션포인트']]
tab6_df = filtered_df[['이름', '소속사', '대표작질문포인트']]

with tab1:
     edited_df = st.data_editor(
        tab1_df,
        use_container_width=True,
        #column_order=("순위","이름","소속사","총점"),
        num_rows=20,
        column_config={
            "총점": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=3000,
            ),
        },
        hide_index=True,
        disabled=tab1_df.columns,
     )
with tab2:
     edited_df = st.data_editor(
        tab2_df,
        use_container_width=True,
        column_config={
            "입실포인트": st.column_config.ProgressColumn(
                help="체류시간에 따른 포인트입니다.",
                format="%i",
                min_value=0,
                max_value=1260,
            ),
            "퀴즈포인트": st.column_config.ProgressColumn(
                help="클래스 퀴즈에 따른 포인트입니다.",
                format="%i",
                min_value=0,
                max_value=300,
            ),
            "미션포인트": st.column_config.ProgressColumn(
                help="디지털비전보드 포인트입니다.",
                format="%i",
                min_value=0,
                max_value=200,
            ),
            "대표작질문포인트": st.column_config.ProgressColumn(
                help="대표작질문포인트에 따른 포인트입니다.",
                format="%i",
                min_value=0,
                max_value=900,
            )
        },
        hide_index=True,
        disabled=tab2_df.columns,
     )
with tab3:
    edited_df = st.data_editor(
        tab3_df,
        use_container_width=True,
        column_config={
            "CJ제일제당": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=375,
            ),
            "CJ대한통운": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=375,
            ),
            "CJ올리브영": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=375,
            ),
            "CJ ENM 엔터": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=375,
            ),
            "CJ ENM 커머스": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=375,
            ),
            "CJ 올리브네트웍스": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=375,
            ),
        },
        hide_index=True,
        disabled=tab3_df.columns,
     )

with tab4:
    edited_df = st.data_editor(
        tab4_df,
        use_container_width=True,
        column_config={
            "CJ제일제당": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=50,
            ),
            "CJ대한통운": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=50,
            ),
            "CJ올리브영": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=50,
            ),
            "CJ ENM 엔터": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=50,
            ),
            "CJ ENM 커머스": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=50,
            ),
            "CJ 올리브네트웍스": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=50,
            ),
        },
        hide_index=True,
        disabled=tab4_df.columns,
     )
with tab5:
    edited_df = st.data_editor(
        tab5_df,
        use_container_width=True,
        column_config={
            "미션포인트": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=200,
            )
        },
        hide_index=True,
        disabled=tab5_df.columns,
     )

with tab6:
    edited_df = st.data_editor(
        tab6_df,
        use_container_width=True,
        column_config={
            "대표작질문포인트": st.column_config.ProgressColumn(
                format="%i",
                min_value=0,
                max_value=900,
            )
        },
        hide_index=True,
        disabled=tab6_df.columns,
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
