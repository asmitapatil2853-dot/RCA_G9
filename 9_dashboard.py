                    "<extra></extra>"
                ),
                showlegend=False
            )
        )

        graph.update_layout(
            template="plotly_white",
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
            "Normal = No anomaly found | Anomaly = Anomaly detected"
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
            "Download RCA Reports CSV",
            data=rca_csv,
            file_name="rca_reports.csv",
            mime="text/csv"
        )

    else:
        st.info("No RCA incident reports available.")
