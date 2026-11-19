
# ============================================================
# SERVICE-WISE VERTICAL BAR GRAPH
# ============================================================

st.subheader("Service-wise Log Analysis")

if not filtered_logs.empty:

    # Count Normal and Anomaly logs for each service
    service_chart_data = (
        filtered_logs
        .groupby(["service", "status"])
        .size()
        .reset_index(name="Log Count")
    )

    # Vertical grouped bar chart
    service_chart = px.bar(
        service_chart_data,
        x="service",
        y="Log Count",
        color="status",
        barmode="group",
        color_discrete_map={
            "Normal": "#6366F1",
            "Anomaly": "#EF4444"
        },
        text="Log Count",
        template="plotly_dark",
        labels={
            "service": "Microservices",
            "Log Count": "Number of Logs",
            "status": "Log Status"
        },
        title="Normal vs Anomaly Logs by Microservice"
    )

    service_chart.update_traces(
        textposition="outside"
    )

    service_chart.update_layout(
        height=500,
        xaxis_title="Microservices",
        yaxis_title="Number of Logs",
        xaxis_tickangle=-20,
        bargap=0.25,
        legend_title="Log Status",
        margin=dict(l=40, r=30, t=70, b=80)
    )

    service_chart.update_yaxes(
        rangemode="tozero"
    )

    st.plotly_chart(
        service_chart,
        use_container_width=True
    )

else:
    st.info("No service data available.")
