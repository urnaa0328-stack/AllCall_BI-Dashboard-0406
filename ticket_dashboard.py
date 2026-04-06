import streamlit as st
import pandas as pd
import altair as alt


def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _safe_datetime(series: pd.Series) -> pd.Series:
    s1 = pd.to_datetime(series, errors="coerce")
    if s1.notna().sum() > 0:
        return s1
    return pd.to_datetime(series.astype(str).str.replace(".", "-", regex=False), errors="coerce")


def render_ticket_dashboard(excel_path: str):
    try:
        df = pd.read_excel(excel_path, sheet_name="Ticket")
    except Exception as e:
        st.error(f"Ticket sheet уншихад алдаа гарлаа: {e}")
        return

    df = _clean_columns(df)

    if "Unnamed: 3" in df.columns and "Дэд төрөл" not in df.columns:
        df = df.rename(columns={"Unnamed: 3": "Дэд төрөл"})

    if "Огноо" in df.columns:
        df["Огноо_dt"] = _safe_datetime(df["Огноо"])
        df["Огноо_өдөр"] = df["Огноо_dt"].dt.date
        df["Сар"] = df["Огноо_dt"].dt.strftime("%Y-%m")
    else:
        df["Огноо_dt"] = pd.NaT
        df["Огноо_өдөр"] = pd.NaT
        df["Сар"] = ""

    for c in ["Суваг", "Төрөл", "Дэд төрөл", "Төлөв", "Оператор", "Нэр", "ААН"]:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].fillna("").astype(str).str.strip()

    st.markdown("## Ticket Dashboard")

    min_date = df["Огноо_dt"].min()
    max_date = df["Огноо_dt"].max()

    c1, c2, c3 = st.columns(3)

    with c1:
        selected_channel = st.selectbox(
            "Суваг",
            ["Бүгд"] + sorted([x for x in df["Суваг"].unique().tolist() if x]),
            key="ticket_channel"
        )

    with c2:
        selected_status = st.selectbox(
            "Төлөв",
            ["Бүгд"] + sorted([x for x in df["Төлөв"].unique().tolist() if x]),
            key="ticket_status"
        )

    with c3:
        search_text = st.text_input("Хайх (Нэр / ААН / Санал)", key="ticket_search").strip().lower()

    if pd.notna(min_date) and pd.notna(max_date):
        date_range = st.date_input(
            "Огнооны шүүлтүүр",
            value=(min_date.date(), max_date.date()),
            key="ticket_date_range"
        )
    else:
        date_range = None

    fdf = df.copy()

    if selected_channel != "Бүгд":
        fdf = fdf[fdf["Суваг"] == selected_channel]

    if selected_status != "Бүгд":
        fdf = fdf[fdf["Төлөв"] == selected_status]

    if search_text:
        mask = (
            fdf.get("Нэр", pd.Series("", index=fdf.index)).astype(str).str.lower().str.contains(search_text, na=False)
            | fdf.get("ААН", pd.Series("", index=fdf.index)).astype(str).str.lower().str.contains(search_text, na=False)
            | fdf.get("Санал, гомдол", pd.Series("", index=fdf.index)).astype(str).str.lower().str.contains(search_text, na=False)
        )
        fdf = fdf[mask]

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        fdf = fdf[
            (fdf["Огноо_dt"].dt.date >= start_date) &
            (fdf["Огноо_dt"].dt.date <= end_date)
        ]

    total_count = len(fdf)
    solved_count = len(fdf[fdf["Төлөв"].str.contains("шийдвэр", case=False, na=False)])
    channel_count = fdf["Суваг"].nunique()
    operator_count = fdf["Оператор"].nunique()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Нийт ticket", f"{total_count:,}")
    m2.metric("Шийдвэрлэсэн", f"{solved_count:,}")
    m3.metric("Сувгийн тоо", f"{channel_count:,}")
    m4.metric("Операторын тоо", f"{operator_count:,}")

    c4, c5 = st.columns(2)

    with c4:
        st.markdown("### Суваг тус бүр")
        ch_df = (
            fdf.groupby("Суваг", dropna=False)
            .size()
            .reset_index(name="Тоо")
            .sort_values("Тоо", ascending=False)
        )
        if len(ch_df) > 0:
            chart = alt.Chart(ch_df).mark_bar().encode(
                x=alt.X("Тоо:Q"),
                y=alt.Y("Суваг:N", sort="-x")
            ).properties(height=350)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Өгөгдөл алга.")

    with c5:
        st.markdown("### Төлөв тус бүр")
        st_df = (
            fdf.groupby("Төлөв", dropna=False)
            .size()
            .reset_index(name="Тоо")
            .sort_values("Тоо", ascending=False)
        )
        if len(st_df) > 0:
            chart = alt.Chart(st_df).mark_bar().encode(
                x=alt.X("Тоо:Q"),
                y=alt.Y("Төлөв:N", sort="-x")
            ).properties(height=350)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Өгөгдөл алга.")

    st.markdown("### Өдөр тутмын ticket урсгал")
    daily = (
        fdf.dropna(subset=["Огноо_dt"])
        .groupby("Огноо_өдөр")
        .size()
        .reset_index(name="Тоо")
        .sort_values("Огноо_өдөр")
    )

    if len(daily) > 0:
        line = alt.Chart(daily).mark_line(point=True).encode(
            x=alt.X("Огноо_өдөр:T", title="Огноо"),
            y=alt.Y("Тоо:Q", title="Тоо")
        ).properties(height=320)
        st.altair_chart(line, use_container_width=True)
    else:
        st.info("Огнооны өгөгдөл алга.")

    st.markdown("### Дэлгэрэнгүй хүснэгт")
    show_cols = [c for c in [
        "Суваг", "Огноо", "Төрөл", "Дэд төрөл", "Утас", "И-мэйл", "ААН", "Нэр",
        "Регистр", "Санал, гомдол", "Төлөв", "Огноо.1", "Хугацаа", "Оператор"
    ] if c in fdf.columns]

    st.dataframe(
        fdf[show_cols],
        use_container_width=True,
        hide_index=True
    )