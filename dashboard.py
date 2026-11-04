"""NextGenLearners — Program Performance Dashboard (Part B). Run: streamlit run dashboard.py"""
import sqlite3
import pandas as pd
import streamlit as st

DB = "nextgen.db"
st.set_page_config(page_title="NextGenLearners Dashboard", page_icon="📊", layout="wide")


@st.cache_data
def run(sql: str, params: tuple = ()) -> pd.DataFrame:
    with sqlite3.connect(DB) as conn:
        return pd.read_sql(sql, conn, params=params)


# ---------- Header + domain filter ----------
st.title("📊 NextGenLearners — Program Performance")
st.caption("Applicants → Interns → Hackathon results")

domains = run("SELECT DISTINCT domain FROM applicants ORDER BY domain")["domain"].tolist()
selected = st.selectbox("Filter by Domain", ["All"] + domains)
# '?' = 'All' lets one SQL statement serve both cases
p = (selected, selected)
FILTER_A = "(? = 'All' OR a.domain = ?)"
FILTER_I = "(? = 'All' OR i.domain = ?)"

# ---------- 1. Funnel ----------
funnel = run(f"""
    SELECT COUNT(DISTINCT a.applicant_id) AS applicants,
           COUNT(DISTINCT CASE WHEN a.status = 'Selected' THEN a.applicant_id END) AS selected,
           COUNT(DISTINCT i.intern_id) AS completed
    FROM applicants a
    LEFT JOIN interns i ON a.applicant_id = i.applicant_id AND i.completion_status = 'Completed'
    WHERE {FILTER_A}""", p).iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Applicants", int(funnel.applicants))
c2.metric("Selected", int(funnel.selected))
c3.metric("Completed Interns", int(funnel.completed))
c4.metric("Overall Completion Rate",
          f"{100.0 * funnel.completed / funnel.applicants:.1f}%" if funnel.applicants else "–")

st.divider()

# ---------- 2 & 3. Charts ----------
left, right = st.columns(2)

conv = run(f"""
    SELECT a.domain,
           ROUND(100.0 * COUNT(DISTINCT i.intern_id) / COUNT(DISTINCT a.applicant_id), 2) AS conversion_rate_pct
    FROM applicants a
    LEFT JOIN interns i ON a.applicant_id = i.applicant_id AND i.completion_status = 'Completed'
    WHERE {FILTER_A}
    GROUP BY a.domain ORDER BY conversion_rate_pct DESC""", p)
with left:
    st.subheader("Completion Rate per Domain (%)")
    st.bar_chart(conv.set_index("domain"))

avg = run(f"""
    SELECT i.domain, ROUND(AVG(h.score), 2) AS avg_score
    FROM hackathon_scores h JOIN interns i ON h.intern_id = i.intern_id
    WHERE {FILTER_I}
    GROUP BY i.domain ORDER BY avg_score DESC""", p)
with right:
    st.subheader("Average Hackathon Score per Domain")
    st.bar_chart(avg.set_index("domain"))

st.divider()

# ---------- 4. Leaderboard ----------
st.subheader("🏆 Top 10 Performers")
top = run(f"""
    SELECT a.name AS Name, a.university AS University, i.domain AS Domain, h.score AS Score
    FROM hackathon_scores h
    JOIN interns i    ON h.intern_id = i.intern_id
    JOIN applicants a ON i.applicant_id = a.applicant_id
    WHERE {FILTER_I}
    ORDER BY h.score DESC LIMIT 10""", p)
top.insert(0, "Rank", range(1, len(top) + 1))
st.dataframe(top, hide_index=True, width="stretch")
