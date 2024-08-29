from collections import defaultdict
from pathlib import Path
import sqlite3
import time

import streamlit as st
import altair as alt
import pandas as pd
from supabase import create_client, Client

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="ONLYONE FAIR Score Board",
    page_icon="🏆",  # This is an emoji shortcode. Could be a URL too.🥇🏆🎖️
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

def connect_supabase():
    # Supabase 프로젝트의 URL과 키를 여기에 입력하세요
    SUPABASE_URL = "https://mvqxuteltnxhbwvgxzlb.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12cXh1dGVsdG54aGJ3dmd4emxiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjM0NTkxNDMsImV4cCI6MjAzOTAzNTE0M30.NIYa3m8HA_31Fjgzr52IScmUjA1o-uEW1V7uU_DW2Pw"

    # Supabase 클라이언트 생성
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Supabase 클라이언트 반환
    return supabase

# 쿼리 : TOP 10 rank
def load_data_(supabase):
    """Loads the inventory data from the Supabase database."""

    try:
        # Score_Info 테이블에서 데이터 쿼리
        query = """
                SELECT A.id
                     , SUM(SCORE) AS score
                     , RANK() OVER (ORDER BY SUM(SCORE) DESC) AS rank
                     , (SELECT name FROM "Peer_Info" B WHERE B.id = A.id) name
                  FROM "Score_Info" A
                 GROUP BY A.id
                 ORDER BY SUM(SCORE) DESC
                 LIMIT 10
               """

        # Supabase의 SQL 기능을 사용해 쿼리 실행
        response = supabase.rpc('execute_top10_ranker', {'query': query}).execute()

        # 응답에서 데이터 추출
        data = response.data

        if not data:
            return None

        # Pandas DataFrame으로 변환
        df = pd.DataFrame(
            data,
            columns=[
                "id",
                "score",
                "rank",
                "name",
            ],
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return df


# 쿼리 : 전 사원 스코어
def load_data_s(supabase):
    """Loads the inventory data from the Supabase database."""

    try:
        # Score_Info 테이블에서 데이터 쿼리
        query = """
                SELECT A.id
                    , SUM(SCORE) AS total_score
                    , RANK() OVER (ORDER BY SUM(SCORE) DESC) AS rank
                    , (SELECT name FROM "Peer_Info" B WHERE B.id = A.id) name
                    , (SELECT company FROM "Peer_Info" B WHERE B.id = A.id) company
                    , (SELECT SUM(SCORE) FROM "Score_Info" B WHERE A.id = B.id AND quiz_dvcd in (3,4)) AS room_score
                    , (SELECT SUM(SCORE) FROM "Score_Info" B WHERE A.id = B.id AND quiz_dvcd =2) AS quiz_score
                    , (SELECT SUM(SCORE) FROM "Score_Info" B WHERE A.id = B.id AND quiz_dvcd =14) AS photo_score
                    , (SELECT SUM(SCORE) FROM "Score_Info" B WHERE A.id = B.id AND quiz_dvcd =5) AS survey_score
                FROM "Score_Info" A
                GROUP BY A.id
                ORDER BY SUM(SCORE) DESC
               """

        # Supabase의 SQL 기능을 사용해 쿼리 실행
        response = supabase.rpc('execute_query', {'query': query}).execute()

        # 응답에서 데이터 추출
        data = response.data

        if not data:
            return None

        # Pandas DataFrame으로 변환
        df = pd.DataFrame(
            data,
            columns=[
                "id",
                "total_score",
                "rank",
                "name",
                "room_score",
                "quiz_score",
                "photo_score"
                "survey_score"
            ],
        )
        df = df.drop(columns=['id', 'rank'])
        df['total_score'] = df['total_score'].astype(int)
        df['name'] = df['name'] + '님'
        df = df.sort_values(by='total_score', ascending=False)

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return df

# -----------------------------------------------------------------------------
# Draw the actual page, starting with the inventory table.

# Set the title that appears at the top of the page.
"""
# 📊 Only One Fair Scoreboard 
"""
"""
"""

# **Welcome to Alice's Corner Store's intentory tracker!**
# This page reads and writes directly from/to our inventory database.

# st.info(
#     """
#     Use the table below to add, remove, and edit items.
#     And don't forget to commit your changes when you're done.
#     """
# )

# Connect to database
supabase = connect_supabase()

# Load data from database
while True:
    df_ = load_data_(supabase)

    # -----------------------------------------------------------------------------

    st.subheader("🏆️ TOP 10 RANK 하고잡이", divider="orange")

    ""
    ""

    # 차트 : TOP 10 Ranker
    # Altair 막대 차트 생성
    st.altair_chart(alt.Chart(df_)
                    .mark_bar(orient="horizontal", color='teal')
                    .encode(x=alt.X("score", title=None), y=alt.Y("name", title=None).sort("-x"))
                    .properties(width=600, height=300))

    st.subheader("🎯 하고잡이 스코어 ", divider="orange")

    ""
    ""

    # Display data with editable table
    edited_df = st.data_editor(
        df_s,
        disabled=["id_"],  # Don't allow editing the 'id' column.
        num_rows="dynamic",  # Allow appending/deleting rows.

        key="score_table",
    )

    # has_uncommitted_changes = any(len(v) for v in st.session_state.inventory_table.values())

    # -----------------------------------------------------------------------------
    # Now some cool charts

    # Add some space
    ""
    ""
    ""

    # st.subheader("Units left", divider="red")

    # need_to_reorder = df[df["units_left"] < df["reorder_point"]].loc[:, "item_name"]

    # if len(need_to_reorder) > 0:
    #     items = "\n".join(f"* {name}" for name in need_to_reorder)

    #     st.error(f"We're running dangerously low on the items below:\n {items}")

    time.sleep(5)