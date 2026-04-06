import streamlit as st
import pandas as pd
import altair as alt


def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _normalize_text(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def _prepare_operation(df: pd.DataFrame, system_name: str) -> pd.DataFrame:
    df = _clean_columns(df)

    expected_cols = [
        "Ажлын төрөл",
        "Төслийн нэр",
        "Эхлэх огноо",
        "Дуусах огноо",
        "Хугацаа",
        "Хариуцагч",
        "Дэмжлэг",
        "Явц",
        "Явцын тайлбар",
    ]

    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""

    df["Ажлын төрөл"] = _normalize_text(df["Ажлын төрөл"])
    df["Төслийн нэр"] = _normalize_text(df["Төслийн нэр"])
    df["Хариуцагч"] = _normalize_text(df["Хариуцагч"])
    df["Дэмжлэг"] = _normalize_text(df["Дэмжлэг"])
    df["Явц"] = _normalize_text(df["Явц"])
    df["Явцын тайлбар"] = _normalize_text(df["Явцын тайлбар"])

    df["Эхлэх огноо"] = pd.to_datetime(df["Эхлэх огноо"], errors="coerce")
    df["Дуусах огноо"] = pd.to_datetime(df["Дуусах огноо"], errors="coerce")
    df["Хугацаа"] = pd.to_numeric(df["Хугацаа"], errors="coerce").fillna(0).astype(int)
    df["Систем"] = system_name

    df = df[
        (df["Ажлын төрөл"] != "") |
        (df["Төслийн нэр"] != "") |
        (df["Хариуцагч"] != "")
    ].copy()

    today = pd.Timestamp.today().normalize()

    def calc_state(row):
        progress = str(row.get("Явц", "")).strip().lower()
        due = row.get("Дуусах огноо", pd.NaT)

        if "хийгдсэн" in progress or "дууссан" in progress or "шийдсэн" in progress:
            return "Дууссан"

        if pd.notna(due):
            if due < today:
                return "Хугацаа хэтэрсэн"
            if due == today:
                return "Өнөөдөр дуусна"

        if "хийгдэж" in progress:
            return "Хийгдэж байна"
        if "төлөвлөсөн" in progress:
            return "Төлөвлөсөн"
        if "хүлээгдэж" in progress:
            return "Хүлээгдэж байна"

        return "Тодорхойгүй"

    df["Төлөв_тооцоолсон"] = df.apply(calc_state, axis=1)

    return df


def _render_metrics(df: pd.DataFrame):
    total = len(df)
    done = len(df[df["Төлөв_тооцоолсон"] == "Дууссан"])
    overdue = len(df[df["Төлөв_тооцоолсон"] == "Хугацаа хэтэрсэн"])
    planning = len(df[df["Төлөв_тооцоолсон"] == "Төлөвлөсөн"])
    in_progress = len(df[df["Төлөв_тооцоолсон"] == "Хийгдэж байна"])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Нийт ажил", f"{total:,}")
    c2.metric("Дууссан", f"{done:,}")
    c3.metric("Хугацаа хэтэрсэн", f"{overdue:,}")
    c4.metric("Төлөвлөсөн", f"{planning:,}")
    c5.metric("Хийгдэж байна", f"{in_progress:,}")


def _render_operation_table(df: pd.DataFrame, key_prefix: str):
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        types = ["Бүгд"] + sorted([x for x in df["Ажлын төрөл"].dropna().astype(str).unique().tolist() if x.strip()])
        selected_type = st.selectbox("Ажлын төрөл", types, key=f"{key_prefix}_type")

    with c2:
        owners = ["Бүгд"] + sorted([x for x in df["Хариуцагч"].dropna().astype(str).unique().tolist() if x.strip()])
        selected_owner = st.selectbox("Хариуцагч", owners, key=f"{key_prefix}_owner")

    with c3:
        states = ["Бүгд"] + sorted([x for x in df["Төлөв_тооцоолсон"].dropna().astype(str).unique().tolist() if x.strip()])
        selected_state = st.selectbox("Төлөв", states, key=f"{key_prefix}_state")

    with c4:
        search_text = st.text_input("Төслийн нэр хайх", key=f"{key_prefix}_search").strip().lower()

    fdf = df.copy()

    if selected_type != "Бүгд":
        fdf = fdf[fdf["Ажлын төрөл"] == selected_type]
    if selected_owner != "Бүгд":
        fdf = fdf[fdf["Хариуцагч"] == selected_owner]
    if selected_state != "Бүгд":
        fdf = fdf[fdf["Төлөв_тооцоолсон"] == selected_state]
    if search_text:
        fdf = fdf[fdf["Төслийн нэр"].str.lower().str.contains(search_text, na=False)]

    show_df = fdf.copy()
    for col in ["Эхлэх огноо", "Дуусах огноо"]:
        show_df[col] = pd.to_datetime(show_df[col], errors="coerce").dt.strftime("%Y-%m-%d")

    cols = [
        "Ажлын төрөл",
        "Төслийн нэр",
        "Эхлэх огноо",
        "Дуусах огноо",
        "Хугацаа",
        "Хариуцагч",
        "Дэмжлэг",
        "Явц",
        "Төлөв_тооцоолсон",
        "Явцын тайлбар",
    ]
    cols = [c for c in cols if c in show_df.columns]

    st.dataframe(show_df[cols], use_container_width=True, hide_index=True)

    return fdf


def _render_operation_charts(df: pd.DataFrame):
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Төлөвийн тархалт")
        state_df = (
            df.groupby("Төлөв_тооцоолсон", dropna=False)
            .size()
            .reset_index(name="Тоо")
            .sort_values("Тоо", ascending=False)
        )
        if len(state_df) > 0:
            chart = alt.Chart(state_df).mark_bar().encode(
                x=alt.X("Тоо:Q", title="Тоо"),
                y=alt.Y("Төлөв_тооцоолсон:N", sort="-x", title="Төлөв")
            ).properties(height=320)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Өгөгдөл алга.")

    with c2:
        st.markdown("### Хариуцагч тус бүр")
        owner_df = (
            df.groupby("Хариуцагч", dropna=False)
            .size()
            .reset_index(name="Тоо")
            .sort_values("Тоо", ascending=False)
        )
        if len(owner_df) > 0:
            chart = alt.Chart(owner_df).mark_bar().encode(
                x=alt.X("Тоо:Q", title="Тоо"),
                y=alt.Y("Хариуцагч:N", sort="-x", title="Хариуцагч")
            ).properties(height=320)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Өгөгдөл алга.")


def render_operation_dashboard(excel_path: str):
    try:
        allcall_raw = pd.read_excel(excel_path, sheet_name="AllCall operation")
        allmed_raw = pd.read_excel(excel_path, sheet_name="AllMed operation")
    except Exception as e:
        st.error(f"Operation sheet уншихад алдаа гарлаа: {e}")
        return

    allcall_df = _prepare_operation(allcall_raw, "AllCall")
    allmed_df = _prepare_operation(allmed_raw, "AllMed")
    combined_df = pd.concat([allcall_df, allmed_df], ignore_index=True)

    st.markdown("## Operation Dashboard")

    tab1, tab2, tab3 = st.tabs(["AllCall Operation", "AllMed Operation", "Нэгдсэн Operation"])

    with tab1:
        _render_metrics(allcall_df)
        filtered_df = _render_operation_table(allcall_df, "allcall_op")
        _render_operation_charts(filtered_df)

    with tab2:
        _render_metrics(allmed_df)
        filtered_df = _render_operation_table(allmed_df, "allmed_op")
        _render_operation_charts(filtered_df)

    with tab3:
        _render_metrics(combined_df)

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            selected_system = st.selectbox("Систем", ["Бүгд", "AllCall", "AllMed"], key="op_system")
        with c2:
            types = ["Бүгд"] + sorted([x for x in combined_df["Ажлын төрөл"].dropna().astype(str).unique().tolist() if x.strip()])
            selected_type = st.selectbox("Ажлын төрөл", types, key="op_type_all")
        with c3:
            states = ["Бүгд"] + sorted([x for x in combined_df["Төлөв_тооцоолсон"].dropna().astype(str).unique().tolist() if x.strip()])
            selected_state = st.selectbox("Төлөв", states, key="op_state_all")
        with c4:
            search_text = st.text_input("Төслийн нэр хайх", key="op_search_all").strip().lower()

        fdf = combined_df.copy()

        if selected_system != "Бүгд":
            fdf = fdf[fdf["Систем"] == selected_system]
        if selected_type != "Бүгд":
            fdf = fdf[fdf["Ажлын төрөл"] == selected_type]
        if selected_state != "Бүгд":
            fdf = fdf[fdf["Төлөв_тооцоолсон"] == selected_state]
        if search_text:
            fdf = fdf[fdf["Төслийн нэр"].str.lower().str.contains(search_text, na=False)]

        show_df = fdf.copy()
        for col in ["Эхлэх огноо", "Дуусах огноо"]:
            show_df[col] = pd.to_datetime(show_df[col], errors="coerce").dt.strftime("%Y-%m-%d")

        cols = [
            "Систем",
            "Ажлын төрөл",
            "Төслийн нэр",
            "Эхлэх огноо",
            "Дуусах огноо",
            "Хугацаа",
            "Хариуцагч",
            "Дэмжлэг",
            "Явц",
            "Төлөв_тооцоолсон",
            "Явцын тайлбар",
        ]
        cols = [c for c in cols if c in show_df.columns]

        st.dataframe(show_df[cols], use_container_width=True, hide_index=True)

        _render_operation_charts(fdf)