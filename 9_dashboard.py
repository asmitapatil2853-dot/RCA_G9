
import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Open 360 LogRCA",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. FILE PATHS AND SERVICES
# ============================================================

ANOMALY_PATH = "data/processed_logs/anomaly_results.csv"
RCA_PATH = "data/processed_logs/rca_reports.csv"

ALL_SERVICES = [
    "API-Gateway",
    "Auth-Service",
    "Order-Service",
    "Database-Service",
    "K8s-Infra-Node"
]

# ============================================================
# 3. LOAD DATA
# ============================================================

@st.cache_data(ttl=10)
def load_dashboard_data():

    if os.path.exists(ANOMALY_PATH) and os.path.exists(RCA_PATH):

        logs = pd.read_csv(ANOMALY_PATH)
        rca = pd.read_csv(RCA_PATH)

        service_col = next(
            (c for c in [
                "root_cause_service",
                "probable_root_cause",
                "root_cause",
                "service"
            ] if c in rca.columns),
            None
        )

        if service_col:
            rca["rc_svc"] = rca[service_col].astype(str).apply(
                lambda value: next(
                    (s for s in ALL_SERVICES if s in value),
                    value
                )
            )
        else:
            rca["rc_svc"] = "Database-Service"

        message_col = next(
            (c for c in [
                "root_cause_message",
                "root_cause_reason",
                "message",
                "summary"
            ] if c in rca.columns),
            None
        )

        rca["rc_msg"] = (
            rca[message_col].fillna("Details unavailable.").astype(str)
            if message_col else
            "Root cause isolated at service node."
        )

        fix_col = next(
            (c for c in [
                "remediation",
                "suggested_fix",
                "action"
            ] if c in rca.columns),
            None
        )

        rca["rc_fix"] = (
            rca[fix_col].fillna("Review the affected service.").astype(str)
            if fix_col else
            "Review the affected service and its dependencies."
        )

        return logs, rca, "CSV Files"

    # ========================================================
    # SAMPLE FALLBACK DATA
    # ========================================================

    sample_logs = pd.DataFrame([
        {
            "timestamp": "2026-11-18 10:01:01",
            "level": "INFO",
            "service": "API-Gateway",
            "request_id": "REQ-1001",
            "message": "POST /api/v1/orders routed successfully",
            "event_template": "POST <*> routed successfully",
            "anomaly_score": 0.15,
            "status": "Normal"
        },
        {
            "timestamp": "2026-11-18 10:01:02",
            "level": "INFO",
            "service": "Auth-Service",
            "request_id": "REQ-1001",
            "message": "JWT token validated",
            "event_template": "JWT token validated",
            "anomaly_score": 0.14,
            "status": "Normal"
        },
        {
            "timestamp": "2026-11-18 10:01:03",
            "level": "INFO",
            "service": "Order-Service",
            "request_id": "REQ-1001",
            "message": "Order payload verified",
            "event_template": "Order payload verified",
            "anomaly_score": 0.14,
            "status": "Normal"
        },
        {
            "timestamp": "2026-11-18 10:01:05",
            "level": "INFO",
            "service": "Database-Service",
            "request_id": "REQ-1001",
            "message": "COMMIT transaction completed in 12ms",
            "event_template": "COMMIT transaction completed in <*>ms",
            "anomaly_score": 0.14,
            "status": "Normal"
        },
        {
            "timestamp": "2026-11-18 10:01:10",
            "level": "INFO",
            "service": "K8s-Infra-Node",
            "request_id": "REQ-1001",
            "message": "Pod cpu_util=34% mem_util=48%",
            "event_template": "Pod cpu_util=<*>% mem_util=<*>%",
            "anomaly_score": 0.16,
            "status": "Normal"
        },
        {
            "timestamp": "2026-11-18 10:02:18",
            "level": "ERROR",
            "service": "Database-Service",
            "request_id": "REQ-1012",
            "message": "PostgreSQL connection pool exhausted",
            "event_template": "PostgreSQL connection pool exhausted",
            "anomaly_score": -0.21,
            "status": "Anomaly"
        },
        {
            "timestamp": "2026-11-18 10:03:42",
            "level": "ERROR",
            "service": "K8s-Infra-Node",
            "request_id": "REQ-1025",
            "message": "OOMKilled: Container auth-pod crashed",
            "event_template": "OOMKilled: Container <*> crashed",
            "anomaly_score": -0.19,
            "status": "Anomaly"
        }
    ])

    sample_rca = pd.DataFrame([
        {
            "request_id": "REQ-1012",
            "rc_svc": "Database-Service",
            "rc_msg": "PostgreSQL connection pool exhausted",
            "rc_fix": "Increase PostgreSQL max_connections and enable PgBouncer."
        },
        {
            "request_id": "REQ-1025",
            "rc_svc": "K8s-Infra-Node",
            "rc_msg": "OOMKilled: Container auth-pod crashed",
            "rc_fix": "Review and increase Kubernetes pod memory limits."
        }
    ])

    return sample_logs, sample_rca, "Sample Fallback Data"


logs_df, rca_df, data_source = load_dashboard_data()


# ============================================================
# 4. DATA VALIDATION
# ============================================================

required_columns = ["service", "status"]

missing = [
    col for col in required_columns
    if col not in logs_df.columns
]

if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

defaults = {
    "timestamp": pd.NaT,
    "level": "UNKNOWN",
    "request_id": "Not available",
    "message": "",
    "event_template": "",
    "anomaly_score": 0.0
}

for col, default in defaults.items():
    if col not in logs_df.columns:
        logs_df[col] = default

logs_df["timestamp"] = pd.to_datetime(
    logs_df["timestamp"],
    errors="coerce"
)

logs_df["anomaly_score"] = pd.to_numeric(
    logs_df["anomaly_score"],
    errors="coerce"
).fillna(0)

logs_df["status"] = (
    logs_df["status"].astype(str).str.strip().str.title()
)

if "request_id" not in rca_df.columns:
    rca_df["request_id"] = [
        f"Incident-{i+1}" for i in range(len(rca_df))
    ]


# ============================================================
# 5. SIDEBAR NAVIGATION AND FILTERS
# ============================================================

with st.sidebar:

    st.title("🛡️ Open 360 LogRCA")
    st.caption("Distributed Observability & RCA")

    st.divider()

    nav = st.radio(
        "Navigation Modules",
        [
            "1. Executive Health Dashboard",
            "2. Root Cause Analysis Graph"
        ]
    )

    st.divider()

    st.subheader("Dashboard Filters")

    available_services = sorted(
        logs_df["service"].dropna().unique().tolist()
    )

    selected_services = st.multiselect(
        "Host / Service Filter",
        available_services,
        default=available_services
    )

    selected_severity = st.selectbox(
        "Log Severity",
        ["All", "INFO", "WARNING", "ERROR", "CRITICAL"]
    )

    selected_status = st.selectbox(
        "Detection Status",
        ["All", "Normal", "Anomaly"]
    )

    st.divider()

    st.caption(f"Data Source: {data_source}")

    if st.button("Refresh Dashboard", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ============================================================
# 6. APPLY FILTERS
# ============================================================

filtered_logs = logs_df.copy()

filtered_logs = filtered_logs[
    filtered_logs["service"].isin(selected_services)
]

if selected_severity != "All":
    filtered_logs = filtered_logs[
        filtered_logs["level"].astype(str).str.upper()
        == selected_severity
    ]

if selected_status != "All":
    filtered_logs = filtered_logs[
        filtered_logs["status"] == selected_status
    ]

normal_df = filtered_logs[
    filtered_logs["status"] == "Normal"
]

anomaly_df = filtered_logs[
    filtered_logs["status"] == "Anomaly"
]

total_logs = len(filtered_logs)
normal_count = len(normal_df)
anomaly_count = len(anomaly_df)

anomaly_percentage = (
    anomaly_count / total_logs * 100
    if total_logs > 0 else 0
)


# ============================================================
# 7. DASHBOARD HEADER
# ============================================================

st.title(
    "Intelligent Distributed Log Analysis & Root-Cause Detection"
)

st.caption(
    f"Open 360 LogRCA | {nav} | Data Source: {data_source}"
)

st.divider()


# ============================================================
# 8. EXECUTIVE HEALTH DASHBOARD
# ============================================================

if nav == "1. Executive Health Dashboard":

    st.subheader("System & Infrastructure Health")

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Active Microservices",
        filtered_logs["service"].nunique()
    )

    k2.metric(
        "Ingested Volume",
        f"{total_logs:,} Logs"
    )

    k3.metric(
        "ML Anomalies (Isolation Forest)",
        anomaly_count,
        delta=f"{anomaly_percentage:.1f}% of logs",
        delta_color="inverse"
    )

    k4.metric(
        "Correlated Incidents",
        len(rca_df)
    )

    st.divider()

    # ========================================================
    # 9. SERVICE HEALTH OVERVIEW
    # ========================================================

    st.subheader("Service Health Overview")

    if not filtered_logs.empty:

        service_summary = (
            filtered_logs.groupby("service")
            .agg(
                Total_Logs=("status", "size"),
                Anomalies=(
                    "status",
                    lambda x: (x == "Anomaly").sum()
                )
            )
            .reset_index()
        )

        service_summary["Anomaly_Rate"] = (
            service_summary["Anomalies"]
            / service_summary["Total_Logs"] * 100
        ).round(2)

        service_summary = service_summary.rename(
            columns={
                "service": "Microservice",
                "Total_Logs": "Total Logs",
                "Anomalies": "Anomaly Count",
                "Anomaly_Rate": "Anomaly Rate (%)"
            }
        )

        st.dataframe(
            service_summary,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No service records available.")

    st.divider()

    # ========================================================
    # 10. LOG STATUS DISTRIBUTION (40%)
    # ========================================================

    chart_left, chart_right = st.columns([2, 3])

    with chart_left:

        st.subheader("Log Status Distribution")

        if not filtered_logs.empty:

            status_counts = (
                filtered_logs["status"]
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="Count")
            )

            status_chart = px.pie(
                status_counts,
                names="Status",
                values="Count",
                hole=0.58,
                template="plotly_white"
            )

            status_chart.update_traces(
                textposition="inside",
                textinfo="percent+label",
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Count: %{value}<br>"
                    "Percentage: %{percent}"
                    "<extra></extra>"
                )
            )

            status_chart.update_layout(
                height=430,
                margin=dict(l=5, r=5, t=20, b=5),
                legend_title_text=""
            )

            st.plotly_chart(
                status_chart,
                use_container_width=True
            )

            st.caption(
                f"Normal: {normal_count} | Anomaly: {anomaly_count}"
            )

        else:
            st.info("No log distribution data available.")

    # ========================================================
    # 11. ISOLATION FOREST ANOMALY SCORING (60%)
    # ========================================================

    with chart_right:

        st.subheader("Isolation Forest Anomaly Scoring")

        # ----------------------------------------------------
        # GRAPH 1: NORMAL LOG SCORES
        # ----------------------------------------------------

        st.markdown("**1. Normal Log Scores**")

        if not normal_df.empty:

            normal_chart = px.scatter(
                normal_df,
                x="timestamp",
                y="anomaly_score",
                color="service",
                hover_data=[
                    "request_id",
                    "message",
                    "level"
                ],
                template="plotly_white"
            )

            normal_chart.update_traces(
                marker=dict(size=10)
            )

            normal_chart.add_hline(
                y=0,
                line_dash="dash",
                annotation_text="Zero reference"
            )

            normal_chart.update_layout(
                height=260,
                margin=dict(l=10, r=10, t=20, b=10),
                legend_title_text="Service",
                xaxis_title="Timestamp",
                yaxis_title="Anomaly Score"
            )

            st.plotly_chart(
                normal_chart,
                use_container_width=True
            )

        else:
            st.info("No normal log records available.")

        # ----------------------------------------------------
        # GRAPH 2: ANOMALY LOG SCORES
        # ----------------------------------------------------

        st.markdown("**2. Anomaly Log Scores**")

        if not anomaly_df.empty:

            anomaly_chart = px.scatter(
                anomaly_df,
                x="timestamp",
                y="anomaly_score",
                color="service",
                hover_data=[
                    "request_id",
                    "message",
                    "level"
                ],
                template="plotly_white"
            )

            anomaly_chart.update_traces(
                marker=dict(size=11, symbol="diamond")
            )

            anomaly_chart.add_hline(
                y=0,
                line_dash="dash",
                annotation_text="Zero reference"
            )

            anomaly_chart.update_layout(
                height=260,
                margin=dict(l=10, r=10, t=20, b=10),
                legend_title_text="Service",
                xaxis_title="Timestamp",
                yaxis_title="Anomaly Score"
            )

            st.plotly_chart(
                anomaly_chart,
                use_container_width=True
            )

        else:
            st.info("No anomaly log records available.")

    # ========================================================
    # 12. INTERACTIVE LOG EXPLORER
    # ========================================================

    st.divider()

    st.subheader("Log Explorer")

    search_text = st.text_input(
        "Search Logs",
        placeholder="Search Request ID, Service or Log Message..."
    )

    display_logs = filtered_logs.copy()

    if search_text:

        search_columns = [
            "request_id",
            "service",
            "message",
            "event_template"
        ]

        search_mask = pd.Series(
            False,
            index=display_logs.index
        )

        for column in search_columns:

            if column in display_logs.columns:

                search_mask |= (
                    display_logs[column]
                    .astype(str)
                    .str.contains(
                        search_text,
                        case=False,
                        na=False,
                        regex=False
                    )
                )

        display_logs = display_logs[search_mask]

    display_columns = [
        c for c in [
            "timestamp",
            "level",
            "service",
            "request_id",
            "event_template",
            "status",
            "anomaly_score",
            "message"
        ]
        if c in display_logs.columns
    ]

    st.caption(
        f"Showing {len(display_logs)} matching records"
    )

    st.dataframe(
        display_logs[display_columns],
        use_container_width=True,
        hide_index=True
    )

    if not display_logs.empty:

        csv_data = (
            display_logs[display_columns]
            .to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            "Download Filtered Logs CSV",
            data=csv_data,
            file_name="filtered_log_records.csv",
            mime="text/csv"
        )


# ============================================================
# 13. ROOT CAUSE ANALYSIS GRAPH
# ============================================================

elif nav == "2. Root Cause Analysis Graph":

    st.subheader(
        "Distributed Service Topology & Root Cause Analysis Graph"
    )

    st.caption(
        "Explore service dependencies and inspect detected incidents."
    )

    graph_column, inspector_column = st.columns([1.8, 1])

    # --------------------------------------------------------
    # SERVICE TOPOLOGY GRAPH
    # --------------------------------------------------------

    with graph_column:

        st.markdown("**Distributed Service Dependency Graph**")

        node_positions = {
            "API-Gateway": (0.0, 0.5),
            "Auth-Service": (0.5, 0.85),
            "Order-Service": (0.5, 0.15),
            "K8s-Infra-Node": (1.0, 0.85),
            "Database-Service": (1.0, 0.15)
        }

        dependencies = [
            ("API-Gateway", "Auth-Service"),
            ("API-Gateway", "Order-Service"),
            ("Auth-Service", "K8s-Infra-Node"),
            ("Order-Service", "Database-Service")
        ]

        graph = go.Figure()

        # Draw dependency connections

        for source, target in dependencies:

            x1, y1 = node_positions[source]
            x2, y2 = node_positions[target]

            graph.add_trace(
                go.Scatter(
                    x=[x1, x2],
                    y=[y1, y2],
                    mode="lines",
                    hoverinfo="text",
                    text=[f"{source} → {target}"],
                    showlegend=False
                )
            )

        node_names = list(node_positions.keys())

        node_x = [
            node_positions[name][0]
            for name in node_names
        ]

        node_y = [
            node_positions[name][1]
            for name in node_names
        ]

        node_colors = []

        for service in node_names:

            service_anomalies = filtered_logs[
                (filtered_logs["service"] == service)
                &
                (filtered_logs["status"] == "Anomaly")
            ]

            node_colors.append(
                "Anomaly" if not service_anomalies.empty
                else "Normal"
            )

        graph.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                text=node_names,
                textposition="top center",
                customdata=node_names,
                marker=dict(
                    size=30,
                    color=node_colors,
                    showscale=False
                ),
                hovertemplate=(
                    "<b>%{customdata}</b>"
                    "<extra></extra>"
                ),
                showlegend=False
            )
        )

        graph.update_layout(
            template="plotly_white",
            height=450,
            showlegend=False,
            margin=dict(l=20, r=20, t=50, b=20),
            xaxis=dict(
                visible=False,
                range=[-0.2, 1.2]
            ),
            yaxis=dict(
                visible=False,
                range=[-0.05, 1.1]
            )
        )

        st.plotly_chart(
            graph,
            use_container_width=True
        )

        st.caption(
            "Normal = No anomaly detected | "
            "Anomaly = Anomaly detected"
        )

        st.caption(
            "Connections represent the configured service topology."
        )

    # --------------------------------------------------------
    # ENTITY INSPECTOR
    # --------------------------------------------------------

    with inspector_column:

        st.subheader("Entity Inspector")

        root_cause_options = (
            sorted(rca_df["rc_svc"].dropna().unique().tolist())
            if not rca_df.empty
            else ALL_SERVICES
        )

        if not root_cause_options:
            root_cause_options = ALL_SERVICES

        selected_root_cause = st.selectbox(
            "Inspect Root-Cause Node",
            root_cause_options
        )

        selected_incidents = rca_df[
            rca_df["rc_svc"] == selected_root_cause
        ].copy()

        st.metric(
            "Isolated Root-Cause Incidents",
            len(selected_incidents)
        )

        if not selected_incidents.empty:

            selected_request = st.selectbox(
                "Select Incident / Request ID",
                selected_incidents["request_id"].astype(str).tolist()
            )

            incident = selected_incidents[
                selected_incidents["request_id"].astype(str)
                == selected_request
            ].iloc[0]

            st.markdown("**Root Cause Signature**")

            st.write(
                str(incident["rc_msg"])
            )

            st.markdown("**Suggested Remediation Action**")

            st.write(
                str(incident["rc_fix"])
            )

        else:

            st.success(
                "No RCA incidents found for this service."
            )

    # ========================================================
    # 14. RCA INCIDENT REPORTS
    # ========================================================

    st.divider()

    st.subheader("Correlated Root-Cause Incident Reports")

    if not rca_df.empty:

        st.dataframe(
            rca_df,
            use_container_width=True,
            hide_index=True
        )

        rca_csv = (
            rca_df.to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            "Download RCA Reports CSV",
            data=rca_csv,
            file_name="rca_reports.csv",
            mime="text/csv"
        )

    else:
        st.info("No RCA incident reports available.")
