
import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Intelligent Distributed Log Analysis & Root-Cause Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. CLEAN LIGHT THEME
# ============================================================

st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF;
        color: #1F2937;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    section[data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E5E7EB;
    }

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }

    h1, h2, h3 {
        color: #111827;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. DATA FILE PATHS AND SERVICE NAMES
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
# 4. LOAD DASHBOARD DATA
# ============================================================

@st.cache_data(ttl=10)
def load_dashboard_data():

    if os.path.exists(ANOMALY_PATH) and os.path.exists(RCA_PATH):

        logs_df = pd.read_csv(ANOMALY_PATH)
        rca_df = pd.read_csv(RCA_PATH)

        # Find root-cause service column
        root_cause_column = next(
            (
                col for col in [
                    "root_cause_service",
                    "probable_root_cause",
                    "root_cause",
                    "service"
                ]
                if col in rca_df.columns
            ),
            None
        )

        if root_cause_column:
            rca_df["rc_svc"] = rca_df[root_cause_column].astype(str).apply(
                lambda value: next(
                    (service for service in ALL_SERVICES if service in value),
                    "Database-Service"
                )
            )
        else:
            rca_df["rc_svc"] = "Database-Service"

        # Find root-cause message column
        message_column = next(
            (
                col for col in [
                    "root_cause_message",
                    "root_cause_reason",
                    "message",
                    "summary"
                ]
                if col in rca_df.columns
            ),
            None
        )

        if message_column:
            rca_df["rc_msg"] = rca_df[message_column].fillna(
                "Root cause details are not available."
            )
        else:
            rca_df["rc_msg"] = (
                "Cascading failure isolated at root service node."
            )

        # Find remediation column
        remediation_column = next(
            (
                col for col in [
                    "remediation",
                    "suggested_fix",
                    "action"
                ]
                if col in rca_df.columns
            ),
            None
        )

        if remediation_column:
            rca_df["rc_fix"] = rca_df[remediation_column].fillna(
                "No remediation suggestion is available."
            )
        else:
            rca_df["rc_fix"] = (
                "Review the affected service and its dependencies."
            )

        return logs_df, rca_df, "CSV files"

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
            "message": "FATAL: PostgreSQL connection pool exhausted (100/100) on db-primary",
            "event_template": "FATAL: PostgreSQL connection pool exhausted (<*>) on <*>",
            "anomaly_score": -0.21,
            "status": "Anomaly"
        },
        {
            "timestamp": "2026-11-18 10:03:42",
            "level": "ERROR",
            "service": "K8s-Infra-Node",
            "request_id": "REQ-1025",
            "message": "OOMKilled: Container auth-pod crashed due to memory limit on worker-node",
            "event_template": "OOMKilled: Container <*> crashed due to memory limit on <*>",
            "anomaly_score": -0.19,
            "status": "Anomaly"
        }
    ])

    sample_rca = pd.DataFrame([
        {
            "request_id": "REQ-1012",
            "rc_svc": "Database-Service",
            "rc_msg": "FATAL: PostgreSQL connection pool exhausted (100/100) on db-primary",
            "rc_fix": "Increase PostgreSQL max_connections and enable PgBouncer pooling."
        },
        {
            "request_id": "REQ-1025",
            "rc_svc": "K8s-Infra-Node",
            "rc_msg": "OOMKilled: Container auth-pod crashed due to memory limit on worker-node",
            "rc_fix": "Review and increase Kubernetes pod memory limits."
        }
    ])

    return sample_logs, sample_rca, "Sample fallback data"


logs_df, rca_df, data_source = load_dashboard_data()

# ============================================================
# 5. DATA VALIDATION AND PREPARATION
# ============================================================

required_columns = ["service", "status"]

missing_columns = [
    col for col in required_columns
    if col not in logs_df.columns
]

if missing_columns:
    st.error(
        "Missing required columns in anomaly_results.csv: "
        + ", ".join(missing_columns)
    )
    st.stop()

if "timestamp" in logs_df.columns:
    logs_df["timestamp"] = pd.to_datetime(
        logs_df["timestamp"],
        errors="coerce"
    )
else:
    logs_df["timestamp"] = pd.NaT

default_columns = {
    "level": "UNKNOWN",
    "request_id": "Not available",
    "message": "",
    "event_template": "",
    "anomaly_score": 0.0
}

for column, default_value in default_columns.items():
    if column not in logs_df.columns:
        logs_df[column] = default_value

if "request_id" not in rca_df.columns:
    rca_df["request_id"] = "Not available"

# ============================================================
# 6. SIDEBAR: NAVIGATION AND FILTERS
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
        options=available_services,
        default=available_services
    )

    severity_options = [
        "All", "INFO", "WARNING", "ERROR", "CRITICAL"
    ]

    selected_severity = st.selectbox(
        "Log Severity",
        severity_options
    )

    status_options = ["All", "Normal", "Anomaly"]

    selected_status = st.selectbox(
        "Detection Status",
        status_options
    )

    st.divider()

    st.caption(f"Data source: {data_source}")

    if st.button("Refresh Dashboard Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ============================================================
# 7. APPLY FILTERS
# ============================================================

filtered_logs = logs_df.copy()

if selected_services:
    filtered_logs = filtered_logs[
        filtered_logs["service"].isin(selected_services)
    ]
else:
    filtered_logs = filtered_logs.iloc[0:0]

if selected_severity != "All":
    filtered_logs = filtered_logs[
        filtered_logs["level"].astype(str).str.upper()
        == selected_severity
    ]

if selected_status != "All":
    filtered_logs = filtered_logs[
        filtered_logs["status"].astype(str).str.lower()
        == selected_status.lower()
    ]

total_logs = len(filtered_logs)

anomaly_logs = filtered_logs[
    filtered_logs["status"].astype(str).str.lower() == "anomaly"
]

anomaly_count = len(anomaly_logs)
normal_count = total_logs - anomaly_count

# ============================================================
# 8. DASHBOARD HEADER
# ============================================================

st.title(
    "Intelligent Distributed Log Analysis & Root-Cause Detection"
)

st.caption(
    f"Open 360 LogRCA | {nav} | Data source: {data_source}"
)

st.divider()

# ============================================================
# 9. MODULE 1: EXECUTIVE HEALTH DASHBOARD
# ============================================================

if nav == "1. Executive Health Dashboard":

    st.subheader("System & Infrastructure Health")

    # KPI CARDS

    kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)

    kpi_1.metric(
        "Active Microservices",
        len(selected_services)
    )

    kpi_2.metric(
        "Ingested Volume",
        f"{total_logs:,} Logs"
    )

    kpi_3.metric(
        "ML Anomalies (Isolation Forest)",
        anomaly_count
    )

    kpi_4.metric(
        "Correlated Incidents",
        len(rca_df)
    )

    st.divider()

    # SERVICE HEALTH OVERVIEW

    st.subheader("Service Health Overview")

    service_summary = (
        filtered_logs.groupby("service")
        .agg(
            Total_Logs=("status", "size"),
            Anomalies=(
                "status",
                lambda values: (
                    values.astype(str).str.lower() == "anomaly"
                ).sum()
            )
        )
        .reset_index()
    )

    if not service_summary.empty:

        service_summary["Anomaly_Rate_Percent"] = (
            service_summary["Anomalies"]
            / service_summary["Total_Logs"].replace(0, 1)
            * 100
        ).round(1)

        service_summary = service_summary.rename(columns={
            "service": "Microservice",
            "Total_Logs": "Total Logs",
            "Anomalies": "Anomaly Count",
            "Anomaly_Rate_Percent": "Anomaly Rate (%)"
        })

        st.dataframe(
            service_summary,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No log records match the selected filters.")

    # ========================================================
    # 10. CHARTS: 40% DISTRIBUTION + 60% ANOMALY SCORING
    # ========================================================

    chart_left, chart_right = st.columns([2, 3])

    # --------------------------------------------------------
    # LEFT: LOG STATUS DISTRIBUTION (40%)
    # --------------------------------------------------------

    with chart_left:

        st.subheader("Log Status Distribution")

        if not filtered_logs.empty:

            status_counts = (
                filtered_logs["status"]
                .astype(str)
                .str.title()
                .value_counts()
                .reset_index()
            )

            status_counts.columns = ["Status", "Count"]

            status_chart = px.pie(
                status_counts,
                names="Status",
                values="Count",
                hole=0.55,
                color="Status",
                color_discrete_map={
                    "Normal": "#22C55E",
                    "Anomaly": "#EF4444"
                },
                template="plotly_white"
            )

            status_chart.update_traces(
                textposition="inside",
                textinfo="percent",
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Logs: %{value}<br>"
                    "Percentage: %{percent}"
                    "<extra></extra>"
                )
            )

            status_chart.update_layout(
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(color="#1F2937"),
                margin=dict(l=5, r=5, t=20, b=5),
                showlegend=True,
                legend_title_text=""
            )

            st.plotly_chart(
                status_chart,
                use_container_width=True
            )

        else:
            st.info("No log distribution data available.")

    # --------------------------------------------------------
    # RIGHT: ISOLATION FOREST ANOMALY SCORING (60%)
    # --------------------------------------------------------

    with chart_right:

        st.subheader("Isolation Forest Anomaly Scoring")

        normal_df = filtered_logs[
            filtered_logs["status"].astype(str).str.lower() == "normal"
        ]

        anomaly_df = filtered_logs[
            filtered_logs["status"].astype(str).str.lower() == "anomaly"
        ]

        # GRAPH 1: NORMAL LOG SCORES

        st.markdown("**1. Normal Log Scores**")

        if not normal_df.empty:

            normal_chart = px.scatter(
                normal_df,
                x="timestamp",
                y="anomaly_score",
                hover_data=[
                    "request_id",
                    "service",
                    "message"
                ],
                color_discrete_sequence=["#16A34A"],
                template="plotly_white"
            )

            normal_chart.update_traces(
                marker=dict(size=10, symbol="circle"),
                name="Normal Logs"
            )

            normal_chart.add_hline(
                y=0,
                line_dash="dash",
                line_color="#F59E0B",
                annotation_text="Reference threshold (0.0)"
            )

            normal_chart.update_layout(
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(color="#1F2937"),
                height=250,
                margin=dict(l=10, r=10, t=20, b=10),
                showlegend=False,
                xaxis_title="Timestamp",
                yaxis_title="Anomaly Score"
            )

            st.plotly_chart(
                normal_chart,
                use_container_width=True
            )

        else:
            st.info("No normal log records available.")

        # GRAPH 2: ANOMALY LOG SCORES

        st.markdown("**2. Anomaly Log Scores**")

        if not anomaly_df.empty:

            anomaly_chart = px.scatter(
                anomaly_df,
                x="timestamp",
                y="anomaly_score",
                hover_data=[
                    "request_id",
                    "service",
                    "message"
                ],
                color_discrete_sequence=["#EF4444"],
                template="plotly_white"
            )

            anomaly_chart.update_traces(
                marker=dict(size=11, symbol="diamond"),
                name="Anomaly Logs"
            )

            anomaly_chart.add_hline(
                y=0,
                line_dash="dash",
                line_color="#F59E0B",
                annotation_text="Reference threshold (0.0)"
            )

            anomaly_chart.update_layout(
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(color="#1F2937"),
                height=250,
                margin=dict(l=10, r=10, t=20, b=10),
                showlegend=False,
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
    # 11. LOG EXPLORER
    # ========================================================

    st.divider()

    st.subheader("Log Explorer")

    search_text = st.text_input(
        "Search by Request ID, Service, or Log Message",
        placeholder="Example: REQ-1012 or connection pool"
    )

    display_logs = filtered_logs.copy()

    if search_text:

        searchable_columns = [
            "request_id",
            "service",
            "message",
            "event_template"
        ]

        search_mask = pd.Series(
            False,
            index=display_logs.index
        )

        for column in searchable_columns:

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
        col for col in [
            "timestamp",
            "level",
            "service",
            "request_id",
            "event_template",
            "status",
            "anomaly_score",
            "message"
        ]
        if col in display_logs.columns
    ]

    st.caption(
        f"Showing {len(display_logs)} matching log records"
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
            "Download Filtered Logs as CSV",
            data=csv_data,
            file_name="filtered_log_records.csv",
            mime="text/csv"
        )

# ============================================================
# 12. MODULE 2: ROOT CAUSE ANALYSIS GRAPH
# ============================================================

elif nav == "2. Root Cause Analysis Graph":

    st.subheader(
        "Distributed Service Topology & Root Cause Analysis Graph"
    )

    st.caption(
        "Explore service dependencies and inspect detected RCA incidents."
    )

    graph_column, inspector_column = st.columns([1.8, 1])

    # ========================================================
    # SERVICE DEPENDENCY GRAPH
    # ========================================================

    with graph_column:

        node_positions = {
            "API-Gateway": (0.0, 0.5),
            "Auth-Service": (0.5, 0.85),
            "Order-Service": (0.5, 0.15),
            "K8s-Infra-Node": (1.0, 0.85),
            "Database-Service": (1.0, 0.15)
        }

        service_dependencies = [
            ("API-Gateway", "Auth-Service"),
            ("API-Gateway", "Order-Service"),
            ("Auth-Service", "K8s-Infra-Node"),
            ("Order-Service", "Database-Service")
        ]

        graph = go.Figure()

        # DRAW CONNECTION LINES

        for source_service, target_service in service_dependencies:

            source_x, source_y = node_positions[source_service]
            target_x, target_y = node_positions[target_service]

            graph.add_trace(
                go.Scatter(
                    x=[source_x, target_x],
                    y=[source_y, target_y],
                    mode="lines",
                    line=dict(
                        color="#94A3B8",
                        width=2
                    ),
                    hoverinfo="text",
                    text=[
                        f"{source_service} → {target_service}"
                    ],
                    showlegend=False
                )
            )

        # IDENTIFY ANOMALY SERVICES

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

        for service_name in node_names:

            service_anomalies = filtered_logs[
                (filtered_logs["service"] == service_name)
                &
                (
                    filtered_logs["status"]
                    .astype(str)
                    .str.lower() == "anomaly"
                )
            ]

            node_colors.append(
                "#EF4444"
                if not service_anomalies.empty
                else "#16A34A"
            )

        # DRAW SERVICE NODES

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
                    line=dict(
                        color="white",
                        width=1.5
                    )
                ),
                hovertemplate="<b>%{customdata}</b><extra></extra>",
                showlegend=False
            )
        )

        graph.update_layout(
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="#1F2937"),
            height=430,
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
            "Graph Legend: Green = No anomaly found | "
            "Red = Anomaly detected"
        )

    # ========================================================
    # ENTITY INSPECTOR
    # ========================================================

    with inspector_column:

        st.subheader("Entity Inspector")

        root_cause_options = (
            sorted(
                rca_df["rc_svc"].dropna().unique().tolist()
            )
            if not rca_df.empty
            else ALL_SERVICES
        )

        if not root_cause_options:
            root_cause_options = ALL_SERVICES

        selected_root_cause = st.selectbox(
            "Inspect Root-Cause Node",
            options=root_cause_options
        )

        selected_incidents = rca_df[
            rca_df["rc_svc"] == selected_root_cause
        ].copy()

        st.metric(
            "Isolated Root-Cause Incidents",
            len(selected_incidents)
        )

        if not selected_incidents.empty:

            request_options = (
                selected_incidents["request_id"]
                .astype(str)
                .tolist()
            )

            selected_request = st.selectbox(
                "Select Incident / Request ID",
                request_options
            )

            incident = selected_incidents[
                selected_incidents["request_id"].astype(str)
                == selected_request
            ].iloc[0]

            st.markdown("**Root Cause Signature**")

            st.error(
                str(incident["rc_msg"])
            )

            st.markdown("**Suggested Remediation Action**")

            st.info(
                str(incident["rc_fix"])
            )

        else:

            st.success(
                "No RCA incidents found for this service."
            )

    # ========================================================
    # RCA INCIDENT REPORTS
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
            "Download RCA Reports as CSV",
            data=rca_csv,
            file_name="rca_reports.csv",
            mime="text/csv"
        )

    else:

        st.info(
            "No root-cause incident reports are available."
        )
