# ============================================================
#  UCAR-Insight 360 — University Management Dashboard
#  Stack : Streamlit · SQLite (sqlite3) · Pandas · Plotly
#  DB    : ucar_360_real_fr.db  (place in same folder)
# ============================================================

import os
import sqlite3
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="UCAR-Insight 360",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0b0f1a;
    color: #e2e8f0;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2.5rem 2rem; }

.brand-bar { display:flex; align-items:center; gap:14px; margin-bottom:0.25rem; }
.brand-logo {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.55rem; font-weight: 700; letter-spacing: -0.5px;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 60%, #e879f9 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.brand-tag {
    font-size: 0.72rem; font-weight: 500; color: #64748b;
    letter-spacing: 0.08em; text-transform: uppercase; margin-top: 4px;
}

div[data-testid="stHorizontalBlock"] button {
    border-radius: 999px !important; font-size: 0.80rem !important;
    font-weight: 500 !important; padding: 0.35rem 1.1rem !important;
    transition: all 0.2s ease;
}

div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #131929 0%, #1a2235 100%);
    border: 1px solid #1e293b; border-radius: 14px;
    padding: 1.1rem 1.4rem !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(56,189,248,0.12);
    border-color: #38bdf830;
}
div[data-testid="metric-container"] label {
    font-size: 0.72rem !important; font-weight: 600 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    color: #94a3b8 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2.1rem !important; font-weight: 700 !important; color: #f1f5f9 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.80rem !important; font-weight: 500 !important;
}

.chart-card {
    background: linear-gradient(135deg, #131929 0%, #161f30 100%);
    border: 1px solid #1e293b; border-radius: 16px;
    padding: 1.2rem 1.4rem 0.5rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3); margin-bottom: 1.2rem;
}
.chart-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 0.90rem;
    font-weight: 600; color: #cbd5e1; letter-spacing: 0.01em; margin-bottom: 0.15rem;
}
.chart-sub { font-size: 0.72rem; color: #475569; margin-bottom: 0.6rem; }

.section-label {
    font-family: 'Space Grotesk', sans-serif; font-size: 0.70rem; font-weight: 600;
    letter-spacing: 0.15em; text-transform: uppercase; color: #475569;
    margin: 1.4rem 0 0.8rem; display: flex; align-items: center; gap: 10px;
}
.section-label::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(to right, #1e293b, transparent);
}

div[data-testid="stAlert"] {
    border-radius: 10px !important; border-left-width: 4px !important;
    font-size: 0.82rem !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATABASE — SQLite connector
# ─────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ucar_360_real_fr.db")


@st.cache_data(ttl=300, show_spinner=False)
def query(sql: str) -> pd.DataFrame:
    """Execute a SQL query against the SQLite DB and return a DataFrame."""
    try:
        with sqlite3.connect(DB_PATH) as con:
            return pd.read_sql_query(sql, con)
    except Exception as e:
        st.toast(f"⚠️ DB error: {e}", icon="🔴")
        return pd.DataFrame()


# ─────────────────────────────────────────────
#  CHART THEME HELPERS
# ─────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#94a3b8", size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(
        bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.05)",
        borderwidth=1, font=dict(size=10),
    ),
)
PALETTE = [
    "#38bdf8", "#818cf8", "#e879f9", "#34d399", "#fb923c",
    "#facc15", "#f472b6", "#a78bfa", "#2dd4bf", "#f87171",
    "#60a5fa", "#4ade80", "#fbbf24", "#c084fc", "#67e8f9",
]


def apply_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_xaxes(gridcolor="#1e293b", zeroline=False, tickfont=dict(size=10))
    fig.update_yaxes(gridcolor="#1e293b", zeroline=False, tickfont=dict(size=10))
    return fig


def cc(title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="chart-card">'
        f'<div class="chart-title">{title}</div>'
        f'<div class="chart-sub">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def cc_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def section(label: str) -> None:
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SESSION STATE — active tab
# ─────────────────────────────────────────────
TABS = ["Enrollment", "Exams", "Pedagogy", "Strategy",
        "Partnerships", "Finance", "HR", "Infrastructure", "ESG/CSR"]

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Enrollment"


# ─────────────────────────────────────────────
#  HEADER + NAVIGATION
# ─────────────────────────────────────────────
st.markdown("""
<div class="brand-bar">
    <span class="brand-logo">UCAR-Insight 360</span>
    <span class="brand-tag">Plateforme Analytique Universitaire — Tunisie &nbsp;·&nbsp; AY 2023-2024</span>
</div>
""", unsafe_allow_html=True)

nav_cols = st.columns(len(TABS))
for col, tab in zip(nav_cols, TABS):
    with col:
        btn_type = "primary" if st.session_state.active_tab == tab else "secondary"
        if st.button(tab, key=f"nav_{tab}", type=btn_type, use_container_width=True):
            st.session_state.active_tab = tab
            st.rerun()

st.markdown(
    "<hr style='border:none;border-top:1px solid #1e293b;margin:0.6rem 0 1.2rem;'>",
    unsafe_allow_html=True,
)

active = st.session_state.active_tab


# ══════════════════════════════════════════════════════════════════════════════
#  ENROLLMENT
# ══════════════════════════════════════════════════════════════════════════════
if active == "Enrollment":

    kpi24 = query("""
        SELECT SUM(enrolled_count) AS total, SUM(new_intake) AS intake,
               ROUND(AVG(dropout_rate),2) AS dropout, ROUND(AVG(repeat_rate),2) AS repeat_r,
               SUM(graduates) AS grads
        FROM enrollment_stats WHERE academic_year = 2024
    """)
    kpi23 = query("""
        SELECT SUM(enrolled_count) AS total, SUM(new_intake) AS intake
        FROM enrollment_stats WHERE academic_year = 2023
    """)

    tot24 = int(kpi24["total"].iloc[0])
    tot23 = int(kpi23["total"].iloc[0])
    int24 = int(kpi24["intake"].iloc[0])
    int23 = int(kpi23["intake"].iloc[0])
    drop  = float(kpi24["dropout"].iloc[0])
    rep   = float(kpi24["repeat_r"].iloc[0])

    d_tot = round((tot24 - tot23) / tot23 * 100, 1) if tot23 else 0
    d_int = round((int24 - int23) / int23 * 100, 1) if int23 else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Inscrits",           f"{tot24:,}",   delta=f"{d_tot:+.1f}% vs 2023")
    k2.metric("Nouveaux Entrants",        f"{int24:,}",   delta=f"{d_int:+.1f}% vs 2023")
    k3.metric("Taux d'Abandon moyen",     f"{drop:.1f}%", delta="moy. nationale", delta_color="off")
    k4.metric("Taux de Redoublement moy.",f"{rep:.1f}%",  delta="moy. nationale", delta_color="off")

    section("Analyse Institutionnelle & Temporelle")
    c1, c2 = st.columns(2)

    with c1:
        cc("Inscrits par Établissement", "Comparaison 2023 vs 2024")
        df_inst = query("""
            SELECT i.short_name AS institution, e.academic_year AS year,
                   SUM(e.enrolled_count) AS enrolled
            FROM enrollment_stats e
            JOIN institutions i ON i.id = e.institution_id
            WHERE e.academic_year IN (2023, 2024)
            GROUP BY i.short_name, e.academic_year ORDER BY institution, year
        """)
        df_inst["year"] = df_inst["year"].astype(str)
        fig = px.bar(df_inst, x="institution", y="enrolled", color="year",
                     barmode="group", color_discrete_sequence=["#818cf8", "#38bdf8"],
                     labels={"enrolled": "Inscrits", "institution": "", "year": "Année"})
        fig.update_traces(marker_line_width=0, opacity=0.9)
        fig.update_xaxes(tickangle=-30)
        st.plotly_chart(apply_theme(fig), use_container_width=True, config={"displayModeBar": False})
        cc_close()

    with c2:
        cc("Tendance 5 Ans", "Inscrits · Diplômés · Entrants · Abandon (%)")
        df_tr = query("""
            SELECT academic_year AS year,
                   SUM(enrolled_count) AS enrolled, SUM(graduates) AS graduates,
                   SUM(new_intake) AS intake, ROUND(AVG(dropout_rate),2) AS dropout_rate
            FROM enrollment_stats WHERE academic_year BETWEEN 2020 AND 2024
            GROUP BY academic_year ORDER BY year
        """)
        fig2 = go.Figure()
        for col, name, color, fill, yax in [
            ("enrolled",     "Inscrits",  "#38bdf8", True,  "y"),
            ("graduates",    "Diplômés",  "#34d399", True,  "y"),
            ("intake",       "Entrants",  "#e879f9", False, "y"),
            ("dropout_rate", "Abandon %", "#fb923c", False, "y2"),
        ]:
            fig2.add_trace(go.Scatter(
                x=df_tr["year"], y=df_tr[col], name=name,
                line=dict(color=color, width=2.5),
                fill="tozeroy" if fill else "none",
                fillcolor="rgba(56,189,248,0.06)" if fill else None,
                mode="lines+markers",
                marker=dict(size=6, line=dict(width=1.5, color="#0b0f1a")),
                yaxis=yax,
            ))
        fig2.update_layout(
            yaxis2=dict(overlaying="y", side="right", gridcolor="rgba(0,0,0,0)",
                        tickfont=dict(color="#fb923c", size=10))
        )
        st.plotly_chart(apply_theme(fig2), use_container_width=True, config={"displayModeBar": False})
        cc_close()

    section("Composition & Distribution")
    c3, c4 = st.columns(2)

    with c3:
        cc("Répartition par Filière d'Établissement", "Inscrits 2024")
        df_cat = query("""
            SELECT i.category, SUM(e.enrolled_count) AS enrolled
            FROM enrollment_stats e JOIN institutions i ON i.id = e.institution_id
            WHERE e.academic_year = 2024
            GROUP BY i.category ORDER BY enrolled DESC
        """)
        fig3 = go.Figure(go.Pie(
            labels=df_cat["category"], values=df_cat["enrolled"], hole=0.6,
            marker_colors=PALETTE[:len(df_cat)], textinfo="percent", textfont=dict(size=11),
            hovertemplate="<b>%{label}</b><br>Inscrits: %{value:,}<br>Part: %{percent}<extra></extra>",
        ))
        fig3.update_layout(**PLOTLY_LAYOUT,
                           annotations=[dict(text="<b>Filières</b>", x=0.5, y=0.5,
                                             font_size=13, font_color="#e2e8f0", showarrow=False)])
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        cc_close()

    with c4:
        cc("Taux d'Abandon par Établissement — AY 2024", "Classés par risque décroissant")
        df_drop = query("""
            SELECT i.short_name AS institution, ROUND(AVG(e.dropout_rate),2) AS dropout
            FROM enrollment_stats e JOIN institutions i ON i.id = e.institution_id
            WHERE e.academic_year = 2024
            GROUP BY i.short_name ORDER BY dropout DESC
        """)
        bar_colors = ["#f87171" if v >= 7 else "#fb923c" if v >= 5 else "#34d399"
                      for v in df_drop["dropout"]]
        fig4 = go.Figure(go.Bar(
            x=df_drop["dropout"], y=df_drop["institution"], orientation="h",
            marker_color=bar_colors, marker_line_width=0, opacity=0.9,
        ))
        fig4.update_layout(**PLOTLY_LAYOUT)
        fig4.update_xaxes(gridcolor="#1e293b", ticksuffix="%")
        fig4.update_yaxes(gridcolor="#1e293b")
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
        cc_close()


# ══════════════════════════════════════════════════════════════════════════════
#  EXAMS
# ══════════════════════════════════════════════════════════════════════════════
elif active == "Exams":
    section("Performance aux Examens — AY 2023-2024")

    df_grade = query("""
        SELECT gb.grade_band AS grade, COUNT(er.id) AS count, gb.sort_order
        FROM exam_results er JOIN grade_bands gb ON gb.id = er.grade_band_id
        GROUP BY gb.grade_band, gb.sort_order ORDER BY gb.sort_order
    """)
    total_exams = int(df_grade["count"].sum())
    pass_count  = int(df_grade[df_grade["sort_order"] <= 4]["count"].sum())
    pass_rate   = round(pass_count / total_exams * 100, 1) if total_exams else 0
    excellent   = int(df_grade[df_grade["sort_order"] == 1]["count"].sum())
    fail        = int(df_grade[df_grade["sort_order"] == 6]["count"].sum())

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Évaluations",   f"{total_exams:,}")
    k2.metric("Taux de Réussite",    f"{pass_rate:.1f}%",  delta="+1.8 pts")
    k3.metric("Mentions Excellent",  f"{excellent:,}")
    k4.metric("Étudiants en Échec",  f"{fail:,}",
              delta=f"{round(fail/total_exams*100,1)}% du total", delta_color="inverse")

    c1, c2 = st.columns(2)
    grade_colors = ["#34d399", "#38bdf8", "#818cf8", "#e879f9", "#fb923c", "#f87171"]

    with c1:
        cc("Distribution des Notes", "Répartition par bande de résultats")
        fig5 = go.Figure(go.Pie(
            labels=df_grade["grade"], values=df_grade["count"], hole=0.6,
            marker_colors=grade_colors, textinfo="percent", textfont=dict(size=11),
            hovertemplate="<b>%{label}</b><br>Étudiants: %{value:,}<br>Part: %{percent}<extra></extra>",
        ))
        fig5.update_layout(**PLOTLY_LAYOUT,
                           annotations=[dict(text="<b>Notes</b>", x=0.5, y=0.5,
                                             font_size=13, font_color="#e2e8f0", showarrow=False)])
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
        cc_close()

    with c2:
        cc("Réussite par Établissement", "% étudiants avec note ≥ 10/20")
        df_pass_inst = query("""
            SELECT i.short_name AS institution,
                   ROUND(100.0 * SUM(CASE WHEN er.grade_band_id <= 4 THEN 1 ELSE 0 END)
                         / COUNT(er.id), 1) AS pass_rate
            FROM exam_results er JOIN institutions i ON i.id = er.institution_id
            GROUP BY i.short_name ORDER BY pass_rate DESC
        """)
        bar_colors2 = ["#34d399" if v >= 80 else "#38bdf8" if v >= 70 else "#fb923c"
                       for v in df_pass_inst["pass_rate"]]
        fig6 = go.Figure(go.Bar(
            x=df_pass_inst["pass_rate"], y=df_pass_inst["institution"],
            orientation="h", marker_color=bar_colors2, marker_line_width=0, opacity=0.9,
        ))
        fig6.update_layout(**PLOTLY_LAYOUT)
        fig6.update_xaxes(gridcolor="#1e293b", ticksuffix="%", range=[0, 100])
        fig6.update_yaxes(gridcolor="#1e293b")
        st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
        cc_close()

    section("Effectif par Bande de Note")
    c3, _ = st.columns([2, 1])
    with c3:
        cc("Histogramme des Bandes de Notes", "Toutes institutions confondues")
        fig7 = px.bar(df_grade.sort_values("sort_order"), x="grade", y="count",
                      color="grade", color_discrete_sequence=grade_colors,
                      labels={"count": "Étudiants", "grade": ""})
        fig7.update_traces(marker_line_width=0, opacity=0.9)
        st.plotly_chart(apply_theme(fig7), use_container_width=True, config={"displayModeBar": False})
        cc_close()


# ══════════════════════════════════════════════════════════════════════════════
#  FINANCE
# ══════════════════════════════════════════════════════════════════════════════
elif active == "Finance":
    section("Tableau de Bord Financier — AY 2024")

    df_fin24 = query("""
        SELECT SUM(budget_allocated) AS alloc, SUM(budget_consumed) AS consumed
        FROM finance_stats WHERE academic_year = 2024
    """)
    df_fin23 = query("""
        SELECT SUM(budget_allocated) AS alloc FROM finance_stats WHERE academic_year = 2023
    """)
    alloc24   = float(df_fin24["alloc"].iloc[0])
    cons24    = float(df_fin24["consumed"].iloc[0])
    alloc23   = float(df_fin23["alloc"].iloc[0])
    exec_rate = round(cons24 / alloc24 * 100, 1) if alloc24 else 0
    d_alloc   = round((alloc24 - alloc23) / alloc23 * 100, 1) if alloc23 else 0
    surplus   = alloc24 - cons24

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Budget Total Alloué",  f"{alloc24/1e6:.1f} M TND", delta=f"{d_alloc:+.1f}% vs 2023")
    k2.metric("Budget Consommé",      f"{cons24/1e6:.1f} M TND")
    k3.metric("Taux d'Exécution",     f"{exec_rate:.1f}%",        delta="+2.3 pts")
    k4.metric("Solde Non Consommé",   f"{surplus/1e6:.1f} M TND",
              delta_color="inverse" if surplus < 0 else "normal")

    c1, c2 = st.columns(2)

    with c1:
        cc("Budget Alloué vs Consommé par Établissement", "AY 2024 — TND")
        df_fc = query("""
            SELECT i.short_name AS institution,
                   SUM(f.budget_allocated) AS allocated,
                   SUM(f.budget_consumed)  AS consumed
            FROM finance_stats f JOIN institutions i ON i.id = f.institution_id
            WHERE f.academic_year = 2024
            GROUP BY i.short_name ORDER BY allocated DESC
        """)
        fig8 = go.Figure()
        fig8.add_trace(go.Bar(name="Alloué",   x=df_fc["institution"],
                              y=df_fc["allocated"],  marker_color="#818cf8", opacity=0.85))
        fig8.add_trace(go.Bar(name="Consommé", x=df_fc["institution"],
                              y=df_fc["consumed"],   marker_color="#38bdf8", opacity=0.85))
        fig8.update_layout(**PLOTLY_LAYOUT, barmode="group")
        fig8.update_xaxes(tickangle=-35)
        st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False})
        cc_close()

    with c2:
        cc("Évolution Budgétaire 2020-2024", "Alloué vs Consommé — toutes institutions")
        df_fyr = query("""
            SELECT academic_year AS year,
                   SUM(budget_allocated) AS allocated, SUM(budget_consumed) AS consumed
            FROM finance_stats GROUP BY academic_year ORDER BY year
        """)
        fig9 = go.Figure()
        fig9.add_trace(go.Scatter(x=df_fyr["year"], y=df_fyr["allocated"], name="Alloué",
                                   line=dict(color="#818cf8", width=2.5), mode="lines+markers",
                                   fill="tozeroy", fillcolor="rgba(129,140,248,0.08)",
                                   marker=dict(size=7)))
        fig9.add_trace(go.Scatter(x=df_fyr["year"], y=df_fyr["consumed"],  name="Consommé",
                                   line=dict(color="#38bdf8", width=2.5), mode="lines+markers",
                                   marker=dict(size=7)))
        st.plotly_chart(apply_theme(fig9), use_container_width=True, config={"displayModeBar": False})
        cc_close()

    section("Taux d'Exécution par Établissement")
    c3, _ = st.columns([2, 1])
    with c3:
        cc("Taux d'Exécution Budgétaire 2024 (%)", "Consommé / Alloué × 100")
        df_exec = query("""
            SELECT i.short_name AS institution,
                   ROUND(100.0 * SUM(f.budget_consumed) / SUM(f.budget_allocated), 1) AS exec_rate
            FROM finance_stats f JOIN institutions i ON i.id = f.institution_id
            WHERE f.academic_year = 2024
            GROUP BY i.short_name ORDER BY exec_rate DESC
        """)
        ex_colors = ["#34d399" if v >= 95 else "#38bdf8" if v >= 85 else "#fb923c"
                     for v in df_exec["exec_rate"]]
        figE = go.Figure(go.Bar(
            x=df_exec["exec_rate"], y=df_exec["institution"], orientation="h",
            marker_color=ex_colors, marker_line_width=0, opacity=0.9,
        ))
        figE.update_layout(**PLOTLY_LAYOUT)
        figE.update_xaxes(gridcolor="#1e293b", ticksuffix="%")
        figE.update_yaxes(gridcolor="#1e293b")
        st.plotly_chart(figE, use_container_width=True, config={"displayModeBar": False})
        cc_close()


# ══════════════════════════════════════════════════════════════════════════════
#  HR
# ══════════════════════════════════════════════════════════════════════════════
elif active == "HR":
    section("Tableau de Bord RH — Données Réelles du Ministère")

    df_hr_cat = query("""
        SELECT category, COUNT(*) AS headcount
        FROM hr_staff WHERE active=1
        GROUP BY category ORDER BY headcount DESC
    """)
    total_staff   = int(df_hr_cat["headcount"].sum())
    teaching      = int(df_hr_cat[df_hr_cat["category"].str.contains(
                        "Maître|Professeur|Assistant", regex=True)]["headcount"].sum())
    aats          = int(df_hr_cat[df_hr_cat["category"].str.contains("AATS")]["headcount"].sum())

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Effectif Total",          f"{total_staff:,}")
    k2.metric("Catégories Personnel",    f"{len(df_hr_cat)}")
    k3.metric("Enseignants Permanents",  f"{teaching:,}")
    k4.metric("Personnel AATS",          f"{aats:,}")

    c1, c2 = st.columns(2)

    with c1:
        cc("Effectif par Catégorie", "Données officielles du Ministère de l'Enseignement Supérieur")
        fig10 = px.bar(df_hr_cat, x="headcount", y="category", orientation="h",
                       color="headcount", color_continuous_scale=["#818cf8", "#e879f9"],
                       labels={"headcount": "Effectif", "category": ""})
        fig10.update_traces(marker_line_width=0)
        fig10.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig10, use_container_width=True, config={"displayModeBar": False})
        cc_close()

    with c2:
        cc("Composition du Corps Enseignant", "Répartition en donut")
        fig11 = go.Figure(go.Pie(
            labels=df_hr_cat["category"], values=df_hr_cat["headcount"], hole=0.6,
            marker_colors=PALETTE[:len(df_hr_cat)], textinfo="percent", textfont=dict(size=11),
        ))
        fig11.update_layout(**PLOTLY_LAYOUT,
                            annotations=[dict(text="<b>Personnel</b>", x=0.5, y=0.5,
                                              font_size=13, font_color="#e2e8f0", showarrow=False)])
        st.plotly_chart(fig11, use_container_width=True, config={"displayModeBar": False})
        cc_close()

    section("Distribution par Établissement")
    c3, c4 = st.columns(2)

    with c3:
        cc("Effectif par Établissement (actifs)", "Toutes catégories")
        df_hr_inst = query("""
            SELECT i.short_name AS institution, COUNT(h.id) AS headcount
            FROM hr_staff h JOIN institutions i ON i.id = h.institution_id
            WHERE h.active = 1
            GROUP BY i.short_name ORDER BY headcount DESC
        """)
        fig12 = px.bar(df_hr_inst, x="institution", y="headcount",
                       color="headcount", color_continuous_scale=["#38bdf8", "#818cf8"],
                       labels={"headcount": "Effectif", "institution": ""})
        fig12.update_traces(marker_line_width=0, opacity=0.9)
        fig12.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        fig12.update_xaxes(tickangle=-30)
        st.plotly_chart(fig12, use_container_width=True, config={"displayModeBar": False})
        cc_close()

    with c4:
        cc("Ratio Enseignants / Étudiants 2024", "Par établissement")
        df_ratio = query("""
            SELECT i.short_name AS institution,
                   COUNT(h.id) AS staff,
                   COALESCE(SUM(e.enrolled_count), 0) AS students
            FROM hr_staff h
            JOIN institutions i ON i.id = h.institution_id
            LEFT JOIN enrollment_stats e
                ON e.institution_id = h.institution_id AND e.academic_year = 2024
            WHERE h.active = 1
              AND h.category NOT LIKE '%AATS%'
              AND h.category NOT LIKE '%Administratif%'
            GROUP BY i.short_name
        """)
        df_ratio["ratio"] = (
            df_ratio["students"] / df_ratio["staff"].replace(0, np.nan)
        ).round(1)
        df_ratio = df_ratio.dropna(subset=["ratio"]).sort_values("ratio")
        ratio_colors = ["#34d399" if v <= 20 else "#fb923c" if v <= 35 else "#f87171"
                        for v in df_ratio["ratio"]]
        fig13 = go.Figure(go.Bar(
            x=df_ratio["ratio"], y=df_ratio["institution"], orientation="h",
            marker_color=ratio_colors, marker_line_width=0, opacity=0.9,
        ))
        fig13.update_layout(**PLOTLY_LAYOUT)
        fig13.update_xaxes(gridcolor="#1e293b", title_text="Étudiants / Enseignant")
        fig13.update_yaxes(gridcolor="#1e293b")
        st.plotly_chart(fig13, use_container_width=True, config={"displayModeBar": False})
        cc_close()


# ══════════════════════════════════════════════════════════════════════════════
#  INFRASTRUCTURE
# ══════════════════════════════════════════════════════════════════════════════
elif active == "Infrastructure":
    section("Infrastructure des Campus — AY 2024")

    df_infra_kpi = query("""
        SELECT SUM(campus_surface_m2) AS surface,
               SUM(amphitheater_seats) AS seats,
               SUM(lab_workstations)  AS labs
        FROM infrastructure WHERE academic_year = 2024
    """)
    surface = int(df_infra_kpi["surface"].iloc[0])
    seats   = int(df_infra_kpi["seats"].iloc[0])
    labs    = int(df_infra_kpi["labs"].iloc[0])

    n_stu_row = query("SELECT SUM(enrolled_count) AS n FROM enrollment_stats WHERE academic_year=2024")
    n_stu = int(n_stu_row["n"].iloc[0]) if not n_stu_row.empty else 1
    occ   = round(n_stu / seats, 1) if seats else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Surface Totale",        f"{surface/1e6:.2f} M m²")
    k2.metric("Sièges Amphithéâtres",  f"{seats:,}")
    k3.metric("Postes de Laboratoire", f"{labs:,}")
    k4.metric("Étudiants / Siège",     f"{occ:.1f}",
              delta="Pression haute" if occ > 2 else "Capacité OK",
              delta_color="inverse" if occ > 2 else "normal")

    c1, c2 = st.columns(2)
    df_inf_inst = query("""
        SELECT i.short_name AS institution,
               SUM(f.campus_surface_m2)  AS surface,
               SUM(f.amphitheater_seats) AS seats,
               SUM(f.lab_workstations)   AS labs
        FROM infrastructure f JOIN institutions i ON i.id = f.institution_id
        WHERE f.academic_year = 2024
        GROUP BY i.short_name ORDER BY surface DESC
    """)

    with c1:
        cc("Surface de Campus par Établissement (m²)", "AY 2024")
        fig14 = px.bar(df_inf_inst, x="institution", y="surface",
                       color="surface", color_continuous_scale=["#38bdf8", "#818cf8"],
                       labels={"surface": "Surface m²", "institution": ""})
        fig14.update_traces(marker_line_width=0, opacity=0.9)
        fig14.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        fig14.update_xaxes(tickangle=-30)
        st.plotly_chart(fig14, use_container_width=True, config={"displayModeBar": False})
        cc_close()

    with c2:
        cc("Évolution de la Capacité 2020-2024", "Sièges & Postes Labo — toutes institutions")
        df_inf_yr = query("""
            SELECT academic_year AS year,
                   SUM(amphitheater_seats) AS seats, SUM(lab_workstations) AS labs
            FROM infrastructure GROUP BY academic_year ORDER BY year
        """)
        fig15 = go.Figure()
        fig15.add_trace(go.Scatter(x=df_inf_yr["year"], y=df_inf_yr["seats"], name="Sièges Amphi",
                                    line=dict(color="#38bdf8", width=2.5), mode="lines+markers",
                                    marker=dict(size=7)))
        fig15.add_trace(go.Scatter(x=df_inf_yr["year"], y=df_inf_yr["labs"],  name="Postes Labo",
                                    line=dict(color="#e879f9", width=2.5), mode="lines+markers",
                                    marker=dict(size=7)))
        st.plotly_chart(apply_theme(fig15), use_container_width=True, config={"displayModeBar": False})
        cc_close()

    section("Détail Capacités par Établissement")
    c3, _ = st.columns([2, 1])
    with c3:
        cc("Sièges Amphi vs Postes Labo par Établissement", "AY 2024")
        fig16 = go.Figure()
        fig16.add_trace(go.Bar(name="Sièges Amphi", x=df_inf_inst["institution"],
                               y=df_inf_inst["seats"], marker_color="#38bdf8", opacity=0.85))
        fig16.add_trace(go.Bar(name="Postes Labo",  x=df_inf_inst["institution"],
                               y=df_inf_inst["labs"],  marker_color="#e879f9", opacity=0.85))
        fig16.update_layout(**PLOTLY_LAYOUT, barmode="group")
        fig16.update_xaxes(tickangle=-35)
        st.plotly_chart(fig16, use_container_width=True, config={"displayModeBar": False})
        cc_close()


# ══════════════════════════════════════════════════════════════════════════════
#  ESG / CSR
# ══════════════════════════════════════════════════════════════════════════════
elif active == "ESG/CSR":
    section("Environnement, Social & Gouvernance — AY 2024")

    df_esg24 = query("""
        SELECT SUM(carbon_footprint_tons) AS carbon, SUM(energy_consumption_kwh) AS energy
        FROM esg_metrics WHERE academic_year = 2024
    """)
    df_esg23 = query("""
        SELECT SUM(carbon_footprint_tons) AS carbon FROM esg_metrics WHERE academic_year = 2023
    """)
    carbon24 = float(df_esg24["carbon"].iloc[0])
    energy24 = float(df_esg24["energy"].iloc[0])
    carbon23 = float(df_esg23["carbon"].iloc[0])
    d_carbon  = round((carbon24 - carbon23) / carbon23 * 100, 1) if carbon23 else 0

    n_stu2 = query("SELECT SUM(enrolled_count) AS n FROM enrollment_stats WHERE academic_year=2024")
    n_stu2 = int(n_stu2["n"].iloc[0]) if not n_stu2.empty else 1

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Empreinte Carbone",   f"{carbon24:,.0f} tCO₂",
              delta=f"{d_carbon:+.1f}% vs 2023", delta_color="inverse")
    k2.metric("Énergie Consommée",   f"{energy24/1e6:.1f} GWh")
    k3.metric("Intensité Carbone",   f"{carbon24/n_stu2:.3f} tCO₂/étudiant")
    k4.metric("Intensité Énergie",   f"{energy24/n_stu2:.0f} kWh/étudiant")

    c1, c2 = st.columns(2)
    df_esg_inst = query("""
        SELECT i.short_name AS institution,
               ROUND(SUM(e.carbon_footprint_tons),1)    AS carbon,
               ROUND(SUM(e.energy_consumption_kwh)/1000,1) AS energy_mwh
        FROM esg_metrics e JOIN institutions i ON i.id = e.institution_id
        WHERE e.academic_year = 2024
        GROUP BY i.short_name ORDER BY carbon DESC
    """)

    with c1:
        cc("Émissions CO₂ par Établissement", "AY 2024 — tCO₂ estimées")
        q33 = df_esg_inst["carbon"].quantile(0.33)
        q66 = df_esg_inst["carbon"].quantile(0.66)
        carbon_colors = ["#f87171" if v > q66 else "#fb923c" if v > q33 else "#34d399"
                         for v in df_esg_inst["carbon"]]
        fig17 = go.Figure(go.Bar(
            x=df_esg_inst["carbon"], y=df_esg_inst["institution"], orientation="h",
            marker_color=carbon_colors, marker_line_width=0, opacity=0.9,
        ))
        fig17.update_layout(**PLOTLY_LAYOUT)
        fig17.update_xaxes(gridcolor="#1e293b", ticksuffix=" t")
        fig17.update_yaxes(gridcolor="#1e293b")
        st.plotly_chart(fig17, use_container_width=True, config={"displayModeBar": False})
        cc_close()

    with c2:
        cc("Tendance CO₂ & Énergie 2020-2024", "Double axe — évolution multi-indicateurs")
        df_esg_yr = query("""
            SELECT academic_year AS year,
                   ROUND(SUM(carbon_footprint_tons),1)     AS carbon,
                   ROUND(SUM(energy_consumption_kwh)/1000,1) AS energy_mwh
            FROM esg_metrics GROUP BY academic_year ORDER BY year
        """)
        fig18 = go.Figure()
        fig18.add_trace(go.Scatter(x=df_esg_yr["year"], y=df_esg_yr["carbon"],
                                    name="CO₂ (t)", line=dict(color="#f87171", width=2.5),
                                    mode="lines+markers", marker=dict(size=7)))
        fig18.add_trace(go.Scatter(x=df_esg_yr["year"], y=df_esg_yr["energy_mwh"],
                                    name="Énergie (MWh)", line=dict(color="#34d399", width=2.5),
                                    mode="lines+markers", marker=dict(size=7), yaxis="y2"))
        fig18.update_layout(
            **PLOTLY_LAYOUT,
            yaxis2=dict(overlaying="y", side="right", gridcolor="rgba(0,0,0,0)",
                        tickfont=dict(color="#34d399", size=10)),
        )
        st.plotly_chart(fig18, use_container_width=True, config={"displayModeBar": False})
        cc_close()

    section("Consommation Énergétique par Établissement")
    c3, _ = st.columns([2, 1])
    with c3:
        cc("Énergie Consommée par Établissement (MWh)", "AY 2024 — triée par volume")
        fig19 = px.bar(df_esg_inst.sort_values("energy_mwh", ascending=True),
                       x="energy_mwh", y="institution", orientation="h",
                       color="energy_mwh", color_continuous_scale=["#34d399", "#fb923c", "#f87171"],
                       labels={"energy_mwh": "Énergie (MWh)", "institution": ""})
        fig19.update_traces(marker_line_width=0, opacity=0.9)
        fig19.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig19, use_container_width=True, config={"displayModeBar": False})
        cc_close()


# ══════════════════════════════════════════════════════════════════════════════
#  PEDAGOGY  (stub)
# ══════════════════════════════════════════════════════════════════════════════
elif active == "Pedagogy":
    section("Pédagogie & Qualité Académique")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Programmes Accrédités", "412",      delta="+18")
    k2.metric("Modules en Ligne",      "2,840",    delta="+310")
    k3.metric("Taille Moyenne Groupe", "34.2",     delta="-2.1", delta_color="inverse")
    k4.metric("Satisfaction Étudiante","3.82 / 5", delta="+0.12 pts")
    st.info("🔬  Module pédagogie complet disponible dans la prochaine release. "
            "Sélectionnez un autre module pour explorer les données en direct.")


# ══════════════════════════════════════════════════════════════════════════════
#  STRATEGY  (stub)
# ══════════════════════════════════════════════════════════════════════════════
elif active == "Strategy":
    section("Plan Stratégique — Exécution 2020-2025")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Objectifs Stratégiques", "48 / 60",   delta="80% réalisés")
    k2.metric("Atteinte des KPIs",      "76.4%",     delta="+4.2 pts")
    k3.metric("Registre des Risques",   "12 Ouverts",delta="-3 clôturés", delta_color="inverse")
    k4.metric("Alignement Budgétaire",  "94.1%",     delta="+1.7 pts")
    st.info("📋  Suivi OKR et roadmap des initiatives disponibles dans l'édition entreprise.")


# ══════════════════════════════════════════════════════════════════════════════
#  PARTNERSHIPS  (stub)
# ══════════════════════════════════════════════════════════════════════════════
elif active == "Partnerships":
    section("Partenariats Nationaux & Internationaux")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Conventions Actives",     "348",   delta="+42")
    k2.metric("Pays Couverts",           "67",    delta="+8")
    k3.metric("Publications Conjointes", "1,240", delta="+185")
    k4.metric("Étudiants en Mobilité",  "3,820", delta="+620")
    st.info("🌐  Carte mondiale interactive des établissements partenaires — bientôt disponible.")


# ──────────────────────────────────────────────────────────────────────────────
#  AI ALERT BANNERS — driven by live DB data
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Alertes & Insights IA Automatisés</div>',
            unsafe_allow_html=True)

# Highest dropout institution
df_alert1 = query("""
    SELECT i.short_name, ROUND(AVG(e.dropout_rate),1) AS dr
    FROM enrollment_stats e JOIN institutions i ON i.id = e.institution_id
    WHERE e.academic_year = 2024 GROUP BY i.short_name ORDER BY dr DESC LIMIT 1
""")
worst_inst = df_alert1["short_name"].iloc[0] if not df_alert1.empty else "N/A"
worst_dr   = float(df_alert1["dr"].iloc[0])  if not df_alert1.empty else 0

# Top energy consumers
df_alert2 = query("""
    SELECT i.short_name
    FROM esg_metrics e JOIN institutions i ON i.id = e.institution_id
    WHERE e.academic_year = 2024
    GROUP BY i.short_name ORDER BY SUM(e.energy_consumption_kwh) DESC LIMIT 3
""")
top_energy = ", ".join(df_alert2["short_name"].tolist()) if not df_alert2.empty else "N/A"

# Total graduates 2024
df_alert3 = query("SELECT SUM(graduates) AS g FROM enrollment_stats WHERE academic_year=2024")
g24 = int(df_alert3["g"].iloc[0]) if not df_alert3.empty else 0

st.error(
    f"🔴  **Critique — Pic d'Abandon Détecté :** **{worst_inst}** enregistre le taux "
    f"d'abandon le plus élevé à **{worst_dr:.1f}%** en AY 2024. Une intervention immédiate "
    f"est recommandée. Analyse des causes disponible dans le module Pédagogie.",
    icon=None,
)

st.warning(
    f"🟡  **Avertissement — Pression Énergétique :** Les établissements "
    f"**{top_energy}** figurent parmi les plus grands consommateurs d'énergie en 2024. "
    f"Un audit d'efficacité énergétique est conseillé pour réduire l'empreinte carbone.",
    icon=None,
)

st.success(
    f"🟢  **Jalon Atteint — Record de Diplômés :** La promotion 2023-2024 compte "
    f"**{g24:,} diplômés** — un record pour le réseau UCAR Tunisie, dépassant l'objectif "
    f"stratégique national de 8.2%.",
    icon=None,
)

# ──────────────────────────────────────────────────────────────────────────────
#  FOOTER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 0.5rem;color:#334155;font-size:0.70rem;letter-spacing:0.06em;">
    UCAR-INSIGHT 360 &nbsp;·&nbsp; Powered by Streamlit &amp; Plotly
    &nbsp;·&nbsp; Source : ucar_360_real_fr.db &nbsp;·&nbsp;
    © 2024 UCAR Analytics Division — Tunisie
</div>
""", unsafe_allow_html=True)