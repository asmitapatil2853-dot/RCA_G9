
import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Log Analysis & Root-Cause Detection",
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
    "Database-Service",
    "K8s-Infra-Node",
    "Order-Service"
]

SERVICE_COLORS = {
    "Normal": "#6366F1",
    "Anomaly": "#EF4444"
}

# ============================================================
# 3. HELPER FUNCTIONS
# ============================================================

def find_column(df, possible_names):

    for name in possible_names:
        if name in df.columns:
            return name

    return None


def normalize_status(value):

    value = str(value).strip().lower()

    if value in ["anomaly", "abnormal", "1", "true"]:
        return "Anomaly"

    return "Normal"


def normalize_service(value):

    value = str(value).strip()

    for service in ALL_SERVICES:
        if service.lower() in value.lower():
            return service

    return value


# ============================================================
# 4. LOAD DATA
# ============================================================

@st.cache_data(ttl=10)
def load_dashboard_data():

    # Load anomaly results
    if not os.path.exists(ANOMALY_PATH):
        raise FileNotFoundError(
            f"Anomaly file not found: {ANOMALY_PATH}"
        )

    logs = pd.read_csv(ANOMALY_PATH)

    # Load RCA reports
    if os.path.exists(RCA_PATH):
        rca = pd.read_csv(RCA_PATH)
    else:
        rca = pd.DataFrame()

    return logs, rca


try:
    logs_df, rca_df = load_dashboard_data()

except Exception as e:

    st.error(f"Unable to load dashboard data: {e}")
    st.stop()


# ============================================================
# 5. DATA PREPROCESSING
# ============================================================

service_col = find_column(
    logs_df,
    ["service", "host", "service_name", "source"]
)

if service_col is None:
    st.error("Service column not found in anomaly_results.csv")
    st.stop()

logs_df["service"] = logs_df[service_col].apply(
    normalize_service
)

# Detect status column
status_col = find_column(
    logs_df,
    ["status", "prediction", "anomaly_label", "result", "is_anomaly"]
)

if status_col:

    logs_df["status"] = logs_df[status_col].apply(
        normalize_status
    )

else:

    # Support numeric Isolation Forest prediction:
    # -1 = anomaly, 1 = normal

    prediction_col = find_column(
        logs_df,
        ["prediction", "anomaly_prediction"]
    )

    if prediction_col:

        logs_df["status"] = logs_df[prediction_col].apply(
            lambda x: "Anomaly"
            if str(x).strip() in ["-1", "1.0"]
            else "Normal"
        )

    else:

        st.error(
            "No anomaly status or prediction column found. "
            "Check anomaly_results.csv."
        )
        st.stop()


# Timestamp
timestamp_col = find_column(
    logs_df,
    ["timestamp", "time", "datetime", "@timestamp"]
)

if timestamp_col:

    logs_df["timestamp"] = pd.to_datetime(
        logs_df[timestamp_col],
        errors="coerce"
    )

else:

    logs_df["timestamp"] = pd.NaT


# Severity
level_col = find_column(
    logs_df,
    ["level", "severity", "log_level"]
)

if level_col:
    logs_df["level"] = (
        logs_df[level_col].astype(str).str.upper()
    )
else:
    logs_df["level"] = "UNKNOWN"


# Request ID
request_col = find_column(
    logs_df,
    ["request_id", "trace_id", "correlation_id", "log_id"]
)

if request_col:
    logs_df["request_id"] = logs_df[request_col].astype(str)
else:
    logs_df["request_id"] = logs_df.index.astype(str)


# Message
message_col = find_column(
    logs_df,
    ["message", "log_message", "content", "event_template"]
)

if message_col:
    logs_df["message"] = logs_df[message_col].fillna("").astype(str)
else:
    logs_df["message"] = ""


# Event template
template_col = find_column(
    logs_df,
    ["event_template", "template", "log_template"]
)

if template_col:
    logs_df["event_template"] = (
        logs_df[template_col].fillna("").astype(str)
    )
else:
    logs_df["event_template"] = logs_df["message"]


# Anomaly score
score_col = find_column(
    logs_df,
    ["anomaly_score", "score", "decision_score"]
)

if score_col:

    logs_df["anomaly_score"] = pd.to_numeric(
        logs_df[score_col],
        errors="coerce"
    ).fillna(0)

else:

    logs_df["anomaly_score"] = 0.0


# ============================================================
# 6. PREPROCESS RCA DATA
# ============================================================

if not rca_df.empty:

    root_col = find_column(
        rca_df,
        [
            "root_cause_service",
            "probable_root_cause",
            "root_cause",
            "service"
        ]
    )

    if root_col:

        rca_df["rc_svc"] = (
            rca_df[root_col].apply(normalize_service)
        )

    else:

        rca_df["rc_svc"] = "Unknown"

    msg_col = find_column(
        rca_df,
        [
            "root_cause_message",
            "root_cause_reason",
            "message",
            "summary",
            "description"
        ]
    )

    if msg_col:

        rca_df["rc_msg"] = (
            rca_df[msg_col].fillna("Details unavailable.")
        )

    else:

        rca_df["rc_msg"] = "Root cause details unavailable."

    fix_col = find_column(
        rca_df,
        [
            "remediation",
            "suggested_fix",
            "action",
            "recommendation"
        ]
    )

    if fix_col:

        rca_df["rc_fix"] = (
            rca_df[fix_col].fillna("No remediation available.")
        )

    else:

        rca_df["rc_fix"] = "Review the affected service."

    rca_request_col = find_column(
        rca_df,
        ["request_id", "trace_id", "incident_id", "log_id"]
    )

    if rca_request_col:

        rca_df["request_id"] = (
            rca_df[rca_request_col].astype(str)
        )

    else:

        rca_df["request_id"] = [
            f"Incident-{i+1}" for i in range(len(rca_df))
        ]

else:

    rca_df = pd.DataFrame(
        columns=[
            "request_id",
            "rc_svc",
            "rc_msg",
            "rc_fix"
        ]
    )


# ============================================================
# 7. SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:

    st.title("Intelligent Distributed Log Analysis & Root-Cause Detection")

    st.caption("Distributed Observability & RCA")

    st.divider()

    st.subheader("Navigation Modules")

    nav = st.radio(
        "Select Module",
        [
            "1. Executive Health Dashboard",
            "2. Root Cause Analysis Graph"
        ],
        label_visibility="collapsed"
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

    available_levels = sorted(
        logs_df["level"].dropna().unique().tolist()
    )

    selected_severity = st.selectbox(
        "Log Severity",
        ["All"] + available_levels
    )

    selected_status = st.selectbox(
        "Detection Status",
        ["All", "Normal", "Anomaly"]
    )

    st.divider()

    if st.button("🔄 Refresh Dashboard", use_container_width=True):

        st.cache_data.clear()
        st.rerun()

    st.caption("Open 360 LogRCA | Distributed Log Monitoring")


# ============================================================
# 8. APPLY FILTERS
# ============================================================

filtered_logs = logs_df.copy()

filtered_logs = filtered_logs[
    filtered_logs["service"].isin(selected_services)
]

if selected_severity != "All":

    filtered_logs = filtered_logs[
        filtered_logs["level"] == selected_severity
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
# 9. MAIN DASHBOARD HEADER
# ============================================================

st.title(
    "Intelligent Distributed Log Analysis & Root-Cause Detection"
)

st.caption(
    "Open 360 LogRCA | Distributed Observability & Root Cause Analysis"
)

st.divider()


# ============================================================
# 10. MODULE 1: EXECUTIVE HEALTH DASHBOARD
# ============================================================

if nav == "1. Executive Health Dashboard":

    st.subheader("System & Infrastructure Health")

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Active Microservices",
        filtered_logs["service"].nunique()
    )

    col2.metric(
        "Ingested Volume",
        f"{total_logs:,} Logs"
    )

    col3.metric(
        "ML Anomalies (Isolation Forest)",
        anomaly_count,
        delta=f"{anomaly_percentage:.2f}% of logs",
        delta_color="inverse"
    )

    col4.metric(
        "Correlated Incidents",
        len(rca_df)
    )

    st.divider()

    # --------------------------------------------------------
    # SERVICE HEALTH OVERVIEW
    # --------------------------------------------------------

    st.subheader("Service Health Overview")

    service_summary = (
        filtered_logs.groupby("service")
        .agg(
            Total_Logs=("status", "count"),
            Anomalies=(
                "status",
                lambda x: (x == "Anomaly").sum()
            )
        )
        .reset_index()
    )

    if not service_summary.empty:

        service_summary["Normal Logs"] = (
            service_summary["Total_Logs"]
            - service_summary["Anomalies"]
        )

        service_summary["Anomaly Rate (%)"] = (
            service_summary["Anomalies"]
            / service_summary["Total_Logs"].replace(0, 1)
            * 100
        ).round(2)

        service_summary = service_summary.rename(
            columns={
                "service": "Microservice",
                "Total_Logs": "Total Logs",
                "Anomalies": "Anomaly Count"
            }
        )

        st.dataframe(
            service_summary[
                [
                    "Microservice",
                    "Total Logs",
                    "Anomaly Count",
                    "Normal Logs",
                    "Anomaly Rate (%)"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No service records available.")

    st.divider()

    # ========================================================
    # 11. SERVICE-WISE VERTICAL GROUPED BAR GRAPH
    # ========================================================

    st.subheader("Service-wise Log Analysis")

    if not filtered_logs.empty:

        # Count Normal and Anomaly logs service-wise

        service_counts = (
            filtered_logs
            .groupby(["service", "status"])
            .size()
            .unstack(fill_value=0)
        )

        service_order = [
            service for service in ALL_SERVICES
            if service in service_counts.index
        ]

        additional_services = [
            service for service in service_counts.index
            if service not in service_order
        ]

        service_order += sorted(additional_services)

        service_counts = service_counts.reindex(
            service_order,
            fill_value=0
        )

        for status in ["Normal", "Anomaly"]:

            if status not in service_counts.columns:
                service_counts[status] = 0

        # Create graph

        fig = go.Figure()

        # Normal logs bar

        fig.add_trace(
            go.Bar(
                name="Normal Logs",
                x=service_counts.index,
                y=service_counts["Normal"],
                marker=dict(
                    color="#6366F1",
                    line=dict(
                        color="#818CF8",
                        width=1
                    )
                ),
                text=service_counts["Normal"],
                textposition="outside",
                textfont=dict(size=12),
                hovertemplate=(
                    "<b>Service:</b> %{x}<br>"
                    "<b>Normal Logs:</b> %{y}"
                    "<extra></extra>"
                )
            )
        )

        # Anomaly logs bar

        fig.add_trace(
            go.Bar(
                name="Anomaly Logs",
                x=service_counts.index,
                y=service_counts["Anomaly"],
                marker=dict(
                    color="#EF4444",
                    line=dict(
                        color="#F87171",
                        width=1
                    )
                ),
                text=service_counts["Anomaly"],
                textposition="outside",
                textfont=dict(size=12),
                hovertemplate=(
                    "<b>Service:</b> %{x}<br>"
                    "<b>Anomaly Logs:</b> %{y}"
                    "<extra></extra>"
                )
            )
        )

        # Graph layout

        max_count = int(
            service_counts[["Normal", "Anomaly"]]
            .to_numpy()
            .max()
        )

        fig.update_layout(
            title=dict(
                text="Normal vs Anomaly Logs by Microservice",
                x=0.5,
                xanchor="center"
            ),
            xaxis_title="Microservices",
            yaxis_title="Number of Logs",
            barmode="group",
            bargap=0.30,
            bargroupgap=0.10,
            template="plotly_dark",
            height=550,
            legend=dict(
                title="Log Status",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            margin=dict(
                l=50,
                r=30,
                t=110,
                b=110
            )
        )

        fig.update_xaxes(
            tickangle=-20,
            categoryorder="array",
            categoryarray=service_order
        )

        fig.update_yaxes(
            title="Number of Logs",
            rangemode="tozero",
            range=[
                0,
                max_count * 1.20 if max_count > 0 else 1
            ]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            "Purple = Normal Logs | Red = Anomaly Logs"
        )

    else:

        st.warning(
            "No log data available for the selected filters."
        )

    # ========================================================
    # 12. LOG EXPLORER
    # ========================================================

    st.divider()

    st.subheader("Log Explorer")

    search_text = st.text_input(
        "Search Logs",
        placeholder="Search Request ID, Service or Message..."
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
        "timestamp",
        "level",
        "service",
        "request_id",
        "event_template",
        "status",
        "anomaly_score",
        "message"
    ]

    st.caption(
        f"Showing {len(display_logs)} matching log records"
    )

    st.dataframe(
        display_logs[display_columns],
        use_container_width=True,
        hide_index=True
    )

    # Download logs

    if not display_logs.empty:

        csv_data = (
            display_logs[display_columns]
            .to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            label="📥 Download Filtered Logs CSV",
            data=csv_data,
            file_name="filtered_log_records.csv",
            mime="text/csv"
        )


# ============================================================
# 13. MODULE 2: ROOT CAUSE ANALYSIS GRAPH
# ============================================================

elif nav == "2. Root Cause Analysis Graph":

    st.subheader(
        "Distributed Service Topology & Root Cause Analysis"
    )

    st.caption(
        "Visualize service dependencies and inspect detected incidents."
    )

    graph_column, inspector_column = st.columns([1.8, 1])

    # --------------------------------------------------------
    # SERVICE DEPENDENCY GRAPH
    # --------------------------------------------------------

    with graph_column:

        st.markdown("### Distributed Service Dependency Graph")

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

        # Draw service connections

        for source, target in dependencies:

            x1, y1 = node_positions[source]

            x2, y2 = node_positions[target]

            graph.add_trace(
                go.Scatter(
                    x=[x1, x2],
                    y=[y1, y2],
                    mode="lines",
                    line=dict(
                        color="#94A3B8",
                        width=2
                    ),
                    hoverinfo="skip",
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

        # IMPORTANT:
        # Plotly marker colors must be valid color values.
        # Do not use "Normal" or "Anomaly" as marker colors.

        node_colors = []

        for service in node_names:

            service_anomalies = filtered_logs[
                (filtered_logs["service"] == service)
                &
                (filtered_logs["status"] == "Anomaly")
            ]

            if not service_anomalies.empty:

                node_colors.append("#EF4444")

            else:

                node_colors.append("#6366F1")

        # Draw nodes

        graph.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                text=node_names,
                textposition="top center",
                customdata=node_names,
                marker=dict(
                    size=32,
                    color=node_colors,
                    line=dict(
                        color="#FFFFFF",
                        width=1
                    )
                ),
                hovertemplate=(
                    "<b>Service:</b> %{customdata}"
                    "<extra></extra>"
                ),
                showlegend=False
            )
        )

        graph.update_layout(
            template="plotly_dark",
            height=450,
            showlegend=False,
            margin=dict(
                l=30,
                r=30,
                t=60,
                b=30
            ),
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

        st.markdown(
            "🔵 Normal Service &nbsp;&nbsp; 🔴 Anomaly Detected",
            unsafe_allow_html=True
        )

        st.caption(
            "Connections represent the configured service topology."
        )

    # --------------------------------------------------------
    # ENTITY INSPECTOR
    # --------------------------------------------------------

    with inspector_column:

        st.subheader("Entity Inspector")

        root_cause_options = sorted(
            rca_df["rc_svc"].dropna().unique().tolist()
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

            st.info(
                str(incident["rc_msg"])
            )

            st.markdown("**Suggested Remediation Action**")

            st.success(
                str(incident["rc_fix"])
            )

        else:

            st.info(
                "No RCA incidents found for this service."
            )

    # ========================================================
    # 14. RCA INCIDENT REPORTS
    # ========================================================

    st.divider()

    st.subheader("Correlated Root-Cause Incident Reports")

    if not rca_df.empty:

        st.dataframe(
            rca_df[
                [
                    "request_id",
                    "rc_svc",
                    "rc_msg",
                    "rc_fix"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        rca_csv = (
            rca_df.to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            label="📥 Download RCA Reports CSV",
            data=rca_csv,
            file_name="rca_reports.csv",
            mime="text/csv"
        )

    else:

        st.info(
            "No RCA incident reports available."
        )

# ============================================================
# 15. FOOTER
# ============================================================

st.divider()

st.caption(
    "Open 360 LogRCA | Intelligent Distributed Log Analysis "
    "& Root-Cause Detection"
)
