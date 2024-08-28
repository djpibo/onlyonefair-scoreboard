from collections import defaultdict
from pathlib import Path
import sqlite3

import streamlit as st
import altair as alt
import pandas as pd
from supabase import create_client, Client

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="OnlyOne Fair Score Board",
    page_icon="📊",  # This is an emoji shortcode. Could be a URL too.🥇🏆🎖️
)


# -----------------------------------------------------------------------------
# Declare some useful functions.


def connect_db():
    """Connects to the sqlite database."""

    DB_FILENAME = Path(__file__).parent / "inventory.db"
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists

    return conn, db_was_just_created

def connect_supabase():
    # Supabase 프로젝트의 URL과 키를 여기에 입력하세요
    SUPABASE_URL = "https://mvqxuteltnxhbwvgxzlb.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12cXh1dGVsdG54aGJ3dmd4emxiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjM0NTkxNDMsImV4cCI6MjAzOTAzNTE0M30.NIYa3m8HA_31Fjgzr52IScmUjA1o-uEW1V7uU_DW2Pw"

    # Supabase 클라이언트 생성
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Supabase 클라이언트 반환
    return supabase


def initialize_data(conn):
    """Initializes the inventory table with some data."""
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            price REAL,
            units_sold INTEGER,
            units_left INTEGER,
            cost_price REAL,
            reorder_point INTEGER,
            description TEXT
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO inventory
            (item_name, price, units_sold, units_left, cost_price, reorder_point, description)
        VALUES
            -- Beverages
            ('Bottled Water (500ml)', 1.50, 115, 15, 0.80, 16, 'Hydrating bottled water'),
            ('Soda (355ml)', 2.00, 93, 8, 1.20, 10, 'Carbonated soft drink'),
            ('Energy Drink (250ml)', 2.50, 12, 18, 1.50, 8, 'High-caffeine energy drink'),
            ('Coffee (hot, large)', 2.75, 11, 14, 1.80, 5, 'Freshly brewed hot coffee'),
            ('Juice (200ml)', 2.25, 11, 9, 1.30, 5, 'Fruit juice blend'),

            -- Snacks
            ('Potato Chips (small)', 2.00, 34, 16, 1.00, 10, 'Salted and crispy potato chips'),
            ('Candy Bar', 1.50, 6, 19, 0.80, 15, 'Chocolate and candy bar'),
            ('Granola Bar', 2.25, 3, 12, 1.30, 8, 'Healthy and nutritious granola bar'),
            ('Cookies (pack of 6)', 2.50, 8, 8, 1.50, 5, 'Soft and chewy cookies'),
            ('Fruit Snack Pack', 1.75, 5, 10, 1.00, 8, 'Assortment of dried fruits and nuts'),

            -- Personal Care
            ('Toothpaste', 3.50, 1, 9, 2.00, 5, 'Minty toothpaste for oral hygiene'),
            ('Hand Sanitizer (small)', 2.00, 2, 13, 1.20, 8, 'Small sanitizer bottle for on-the-go'),
            ('Pain Relievers (pack)', 5.00, 1, 5, 3.00, 3, 'Over-the-counter pain relief medication'),
            ('Bandages (box)', 3.00, 0, 10, 2.00, 5, 'Box of adhesive bandages for minor cuts'),
            ('Sunscreen (small)', 5.50, 6, 5, 3.50, 3, 'Small bottle of sunscreen for sun protection'),

            -- Household
            ('Batteries (AA, pack of 4)', 4.00, 1, 5, 2.50, 3, 'Pack of 4 AA batteries'),
            ('Light Bulbs (LED, 2-pack)', 6.00, 3, 3, 4.00, 2, 'Energy-efficient LED light bulbs'),
            ('Trash Bags (small, 10-pack)', 3.00, 5, 10, 2.00, 5, 'Small trash bags for everyday use'),
            ('Paper Towels (single roll)', 2.50, 3, 8, 1.50, 5, 'Single roll of paper towels'),
            ('Multi-Surface Cleaner', 4.50, 2, 5, 3.00, 3, 'All-purpose cleaning spray'),

            -- Others
            ('Lottery Tickets', 2.00, 17, 20, 1.50, 10, 'Assorted lottery tickets'),
            ('Newspaper', 1.50, 22, 20, 1.00, 5, 'Daily newspaper')
        """
    )
    conn.commit()

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
        # df = df.astype({
        #     "id": "int64",  # id는 보통 정수형
        #     "TOTAL_SCORE": "float64",  # TOTAL_SCORE는 real에 해당, 즉 부동소수점형
        #     "name": "object",  # name은 varchar에 해당, 문자열 데이터
        #     "company": "object",  # company도 varchar에 해당, 문자열 데이터
        #     "ROOM_SCORE": "float64",  # ROOM_SCORE는 real에 해당, 즉 부동소수점형
        #     "QUIZ_SCORE": "float64",  # QUIZ_SCORE는 real에 해당, 즉 부동소수점형
        #     "PHOTO_SCORE": "float64",  # PHOTO_SCORE는 real에 해당, 즉 부동소수점형
        #     "SURVEY_SCORE": "float64"  # SURVEY_SCORE는 real에 해당, 즉 부동소수점형
        # })

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return df


def load_data(conn):
    """Loads the inventory data from the database."""
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM inventory")
        data = cursor.fetchall()
    except:
        return None

    df = pd.DataFrame(
        data,
        columns=[
            "id",
            "item_name",
            "price",
            "units_sold",
            "units_left",
            "cost_price",
            "reorder_point",
            "description",
        ],
    )

    return df


def update_data(conn, df, changes):
    """Updates the inventory data in the database."""
    cursor = conn.cursor()

    if changes["edited_rows"]:
        deltas = st.session_state.inventory_table["edited_rows"]
        rows = []

        for i, delta in deltas.items():
            row_dict = df.iloc[i].to_dict()
            row_dict.update(delta)
            rows.append(row_dict)

        cursor.executemany(
            """
            UPDATE inventory
            SET
                item_name = :item_name,
                price = :price,
                units_sold = :units_sold,
                units_left = :units_left,
                cost_price = :cost_price,
                reorder_point = :reorder_point,
                description = :description
            WHERE id = :id
            """,
            rows,
        )

    if changes["added_rows"]:
        cursor.executemany(
            """
            INSERT INTO inventory
                (id, item_name, price, units_sold, units_left, cost_price, reorder_point, description)
            VALUES
                (:id, :item_name, :price, :units_sold, :units_left, :cost_price, :reorder_point, :description)
            """,
            (defaultdict(lambda: None, row) for row in changes["added_rows"]),
        )

    if changes["deleted_rows"]:
        cursor.executemany(
            "DELETE FROM inventory WHERE id = :id",
            ({"id": int(df.loc[i, "id"])} for i in changes["deleted_rows"]),
        )

    conn.commit()


# -----------------------------------------------------------------------------
# Draw the actual page, starting with the inventory table.

# Set the title that appears at the top of the page.
"""
# 📊Only One Fair Scoreboard 🔢

**Welcome to Alice's Corner Store's intentory tracker!**
This page reads and writes directly from/to our inventory database.
"""

st.info(
    """
    Use the table below to add, remove, and edit items.
    And don't forget to commit your changes when you're done.
    """
)

# Connect to database and create table if needed
conn, db_was_just_created = connect_db()
supabase = connect_supabase()

# Initialize data.
if db_was_just_created:
    initialize_data(conn)
    st.toast("Database initialized with some sample data.")

# Load data from database
df = load_data(conn)
df_ = load_data_(supabase)


# -----------------------------------------------------------------------------

st.subheader("🏆️TOP 10 RANK 하고잡이🎖", divider="orange")

""
""

# 차트 : TOP 10 Ranker
# Altair 막대 차트 생성
st.altair_chart(alt.Chart(df_)
                .mark_bar(orient="horizontal", color='teal')
                .encode(x=alt.X("score", title=None), y=alt.Y("name", title=None).sort("-x"))
                .properties(width=600, height=300))

# Display data with editable table
edited_df = st.data_editor(
    df,
    disabled=["id"],  # Don't allow editing the 'id' column.
    num_rows="dynamic",  # Allow appending/deleting rows.
    column_config={
        # Show dollar sign before price columns.
        "price": st.column_config.NumberColumn(format="$%.2f"),
        "cost_price": st.column_config.NumberColumn(format="$%.2f"),
    },
    key="inventory_table",
)

has_uncommitted_changes = any(len(v) for v in st.session_state.inventory_table.values())

st.button(
    "Commit changes",
    type="primary",
    disabled=not has_uncommitted_changes,
    # Update data in database
    on_click=update_data,
    args=(conn, df, st.session_state.inventory_table),
)


# -----------------------------------------------------------------------------
# Now some cool charts

# Add some space
""
""
""

st.subheader("Units left", divider="red")

need_to_reorder = df[df["units_left"] < df["reorder_point"]].loc[:, "item_name"]

if len(need_to_reorder) > 0:
    items = "\n".join(f"* {name}" for name in need_to_reorder)

    st.error(f"We're running dangerously low on the items below:\n {items}")

""
""

st.altair_chart(
    # Layer 1: Bar chart.
    alt.Chart(df)
    .mark_bar(
        orient="horizontal",
    )
    .encode(
        x="units_left",
        y="item_name",
    )
    # Layer 2: Chart showing the reorder point.
    + alt.Chart(df)
    .mark_point(
        shape="diamond",
        filled=True,
        size=50,
        color="salmon",
        opacity=1,
    )
    .encode(
        x="reorder_point",
        y="item_name",
    ),
    use_container_width=True,
)

st.caption("NOTE: The :diamonds: location shows the reorder point.")

""
""
""