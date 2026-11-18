# import os
# import streamlit as st
# import pandas as pd
# import numpy as np
# import plotly.express as px
# import plotly.graph_objects as go
# import networkx as nx

# # --- Page Configuration ---
# st.set_page_config(
#     page_title="Open 360 & RCA Workbench | Distributed Log RCA",
#     page_icon="🛡️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # --- Enterprise Observability & RCA Workbench Dark CSS ---
# st.markdown("""
# <style>
#     .stApp {
#         background-color: #0B0F17;
#         color: #E2E8F0;
#     }
#     section[data-testid="stSidebar"] {
#         background-color: #111622;
#         border-right: 1px solid #1F2937;
#     }
#     .top-navbar {
#         background-color: #111622;
#         border: 1px solid #1F2937;
#         border-radius: 6px;
#         padding: 10px 18px;
#         margin-bottom: 12px;
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#     }
#     .nav-breadcrumb { font-size: 13px; color: #9CA3AF; }
#     .nav-breadcrumb b { color: #38BDF8; }
#     .prod-pill {
#         background-color: #7F1D1D; color: #FCA5A5; border: 1px solid #EF4444;
#         padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;
#     }
#     .time-pill {
#         background-color: #1E293B; color: #CBD5E1; border: 1px solid #334155;
#         padding: 3px 10px; border-radius: 4px; font-size: 11px; margin-right: 8px;
#     }
#     .section-strip {
#         background-color: #151C2C; border: 1px solid #1E293B; border-radius: 5px;
#         padding: 7px 14px; margin: 10px 0px; font-size: 13px; font-weight: 600; color: #CBD5E1;
#     }
#     .g-panel {
#         background-color: #131926; border: 1px solid #1F2937; border-radius: 6px;
#         padding: 12px; height: 100%;
#     }
#     .g-panel-title {
#         font-size: 12px; font-weight: 600; color: #9CA3AF; margin-bottom: 6px;
#         display: flex; justify-content: space-between;
#     }
#     .big-stat-val {
#         font-size: 32px; font-weight: 700; color: #F8FAFC; text-align: center; padding: 38px 0px;
#     }
#     .big-stat-sub { font-size: 13px; color: #94A3B8; font-weight: 500; }
#     .stacked-stat {
#         background-color: #131926; border: 1px solid #1F2937; border-radius: 6px;
#         padding: 10px 12px; margin-bottom: 8px;
#     }
#     .stacked-val-red { font-size: 22px; font-weight: 700; color: #F87171; text-align: center; padding-top: 4px; }
#     .stacked-val-amber { font-size: 22px; font-weight: 700; color: #FBBF24; text-align: center; padding-top: 4px; }
#     /* RCA Workbench Inspector Card */
#     .wb-inspector {
#         background-color: #161B26;
#         border: 1px solid #2D3748;
#         border-radius: 8px;
#         padding: 16px;
#         box-shadow: 0 10px 25px rgba(0,0,0,0.5);
#     }
#     .wb-tag-svc {
#         background-color: #365314; color: #BEF264; border: 1px solid #65A30D;
#         padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;
#     }
#     .wb-tag-crit {
#         background-color: #7F1D1D; color: #FCA5A5; border: 1px solid #EF4444;
#         padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;
#     }
#     .wb-query-bar {
#         background-color: #111622; border: 1px solid #2D3748; border-radius: 5px;
#         padding: 8px 14px; font-family: monospace; font-size: 13px; color: #E2E8F0;
#         margin-bottom: 10px;
#     }
#     .rem-card-crit {
#         background-color: #1C1117; border: 1px solid #374151; border-left: 5px solid #EF4444;
#         border-radius: 6px; padding: 14px; margin-bottom: 10px;
#     }
#     .rem-card-warn {
#         background-color: #1C1912; border: 1px solid #374151; border-left: 5px solid #F59E0B;
#         border-radius: 6px; padding: 14px; margin-bottom: 10px;
#     }
#     .badge-crit { background-color: #DC2626; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
#     .badge-warn { background-color: #D97706; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
# </style>
# """, unsafe_allow_html=True)

# ANOMALY_FILE = "data/processed_logs/anomaly_results.csv"
# RCA_FILE = "data/processed_logs/rca_reports.csv"

# if not os.path.exists(ANOMALY_FILE) or not os.path.exists(RCA_FILE):
#     st.error("Data files not found! Please run scripts 1 to 4 first.")
#     st.stop()

# logs_df = pd.read_csv(ANOMALY_FILE)
# rca_df = pd.read_csv(RCA_FILE)
# logs_df["timestamp"] = pd.to_datetime(logs_df["timestamp"])

# # --- Sidebar Navigation ---
# with st.sidebar:
#     st.markdown("### 🌐 **Open 360** `LogRCA`")
#     st.caption("Distributed Observability & RCA")
#     st.divider()
#     nav = st.radio(
#         "NAVIGATION",
#         [
#             "1. Executive Health Dashboard",
#             "2. Distributed Service Topology",
#             "3. Root Cause Analysis Graph",
#             "4. Anomaly Detection",
#             "5. Request Trace Waterfall",
#             "6. Live Log Observer",
#             "7. AI Remediation Suggestions"
#         ],
#         label_visibility="collapsed"
#     )
#     st.divider()
#     svc_filter = st.multiselect(
#         "Host / Service Filter",
#         options=list(logs_df["service"].unique()),
#         default=list(logs_df["service"].unique())
#     )
#     st.divider()
#     st.caption("Cluster: `prod-k8s-cluster-01`")
#     st.caption("Engine: `Drain3 + IsolationForest`")

# df = logs_df[logs_df["service"].isin(svc_filter)].copy()

# # --- Top Breadcrumb & Control Bar ---
# top_rc = rca_df["probable_root_cause"].mode()[0] if not rca_df.empty else "None"
# total_logs = len(df)
# anom_count = len(df[df["status"] == "Anomaly"])
# err_rate = round((anom_count / total_logs) * 100, 1) if total_logs > 0 else 0.0
# incidents = len(rca_df)

# st.markdown(f"""
# <div class="top-navbar">
#     <div>
#         <div style="font-size:17px;font-weight:700;color:#F8FAFC;letter-spacing:0.01em;">
#             🛡️ Intelligent Distributed Log Analysis &amp; Root-Cause Detection
#         </div>
#         <div class="nav-breadcrumb" style="margin-top:3px;">
#             Dashboards &nbsp;&gt;&nbsp; <b>{nav}</b> &nbsp;|&nbsp; env: <code>prod</code> &nbsp;|&nbsp; namespace: <code>distributed-core</code>
#         </div>
#     </div>
#     <div>
#         <span class="time-pill">🕒 Last 30 Mins</span>
#         <span class="prod-pill">● Root Cause: {top_rc}</span>
#     </div>
# </div>
# """, unsafe_allow_html=True)

# # ==============================================================================
# # 1. EXECUTIVE HEALTH DASHBOARD (OPEN 360 6-COL + 3-COL GRID)
# # ==============================================================================
# if nav == "1. Executive Health Dashboard":
#     st.markdown('<div class="section-strip">⌄ &nbsp; System &amp; Infrastructure Health</div>', unsafe_allow_html=True)

#     c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1, 1, 0.95, 0.95])
#     gauge_services = ["Database-Service", "K8s-Infra-Node", "Auth-Service"]
#     gauge_cols = [c1, c2, c3]

#     for idx, svc in enumerate(gauge_services):
#         s_df = logs_df[logs_df["service"] == svc]
#         anom = len(s_df[s_df["status"] == "Anomaly"])
#         err_pct = round((anom / len(s_df)) * 100, 1)

#         fig_g = go.Figure(go.Indicator(
#             mode="gauge+number", value=err_pct,
#             number={"suffix": "%", "font": {"size": 22, "color": "#F8FAFC"}},
#             gauge={
#                 "axis": {"range": [0, 15], "visible": False},
#                 "bar": {"color": "rgba(0,0,0,0)"},
#                 "bgcolor": "#1E293B",
#                 "steps": [
#                     {"range": [0, 4], "color": "#10B981"},
#                     {"range": [4, 7], "color": "#F59E0B"},
#                     {"range": [7, 15], "color": "#EF4444"}
#                 ],
#                 "threshold": {"line": {"color": "#FFFFFF", "width": 3}, "thickness": 0.85, "value": err_pct}
#             }
#         ))
#         fig_g.update_layout(paper_bgcolor="#131926", margin=dict(l=12, r=12, t=12, b=8), height=135)
#         with gauge_cols[idx]:
#             st.markdown(f'<div class="g-panel"><div class="g-panel-title"><span>{svc}</span><span>↗ ⋯</span></div>', unsafe_allow_html=True)
#             st.plotly_chart(fig_g, use_container_width=True, key=f"gauge_{svc}")
#             st.markdown('<div style="text-align:center;font-size:11px;color:#64748B;margin-top:-10px;">Error Threshold</div></div>', unsafe_allow_html=True)

#     with c4:
#         st.markdown('<div class="g-panel"><div class="g-panel-title"><span>Root Cause Share</span><span>↗ ⋯</span></div>', unsafe_allow_html=True)
#         rc_counts = rca_df["probable_root_cause"].value_counts().reset_index()
#         rc_counts.columns = ["Service", "Count"]
#         fig_pie = px.pie(rc_counts, values="Count", names="Service", color_discrete_sequence=["#2563EB", "#34D399", "#F59E0B"])
#         fig_pie.update_traces(textinfo="none")
#         fig_pie.update_layout(paper_bgcolor="#131926", showlegend=False, margin=dict(l=8, r=8, t=8, b=8), height=148)
#         st.plotly_chart(fig_pie, use_container_width=True)
#         st.markdown('</div>', unsafe_allow_html=True)

#     with c5:
#         st.markdown(f"""
#         <div class="g-panel">
#             <div class="g-panel-title"><span>Ingested Volume</span><span>↗ ⋯</span></div>
#             <div class="big-stat-val">{total_logs:,} <span class="big-stat-sub">Logs</span></div>
#         </div>
#         """, unsafe_allow_html=True)

#     with c6:
#         st.markdown("""
#         <div class="stacked-stat">
#             <div class="g-panel-title"><span>DB Pool Load</span><span>↗ ⋯</span></div>
#             <div class="stacked-val-red">100% <span style="font-size:12px;color:#9CA3AF;">MAX</span></div>
#         </div>
#         <div class="stacked-stat">
#             <div class="g-panel-title"><span>K8s Pod Mem</span><span>↗ ⋯</span></div>
#             <div class="stacked-val-amber">94% <span style="font-size:12px;color:#9CA3AF;">OOM</span></div>
#         </div>
#         """, unsafe_allow_html=True)

#     st.markdown('<div class="section-strip">⌄ &nbsp; Operations &amp; Telemetry Stream</div>', unsafe_allow_html=True)
#     op1, op2, op3 = st.columns([2.2, 1, 1])

#     with op1:
#         st.markdown('<div class="g-panel"><div class="g-panel-title"><span>Service Event Throughput &amp; Anomaly Rate</span><span>↗ ⋯</span></div>', unsafe_allow_html=True)
#         df["bucket"] = df["timestamp"].dt.floor("1min")
#         ts_pivot = df.groupby(["bucket", "service"]).size().reset_index(name="events")
#         fig_line = px.line(
#             ts_pivot, x="bucket", y="events", color="service",
#             color_discrete_sequence=["#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]
#         )
#         fig_line.update_layout(
#             template="plotly_dark", plot_bgcolor="#131926", paper_bgcolor="#131926",
#             height=175, margin=dict(l=10, r=10, t=5, b=5), xaxis_title="", yaxis_title="", showlegend=False
#         )
#         st.plotly_chart(fig_line, use_container_width=True)

#         stats_rows = []
#         for svc in ["API-Gateway", "Order-Service", "Database-Service", "K8s-Infra-Node"]:
#             s_counts = ts_pivot[ts_pivot["service"] == svc]["events"]
#             if not s_counts.empty:
#                 stats_rows.append({
#                     "Name": svc,
#                     "Avg": f"{s_counts.mean():.1f}/m",
#                     "Min": f"{s_counts.min()}",
#                     "Max": f"{s_counts.max()}",
#                     "Last*": f"{s_counts.iloc[-1]}"
#                 })
#         st.dataframe(pd.DataFrame(stats_rows), use_container_width=True, hide_index=True, height=145)
#         st.markdown('</div>', unsafe_allow_html=True)

#     with op2:
#         st.markdown('<div class="g-panel"><div class="g-panel-title"><span>Global Anomaly %</span><span style="background:#374151;padding:1px 5px;border-radius:3px;font-size:10px;">ML</span></div>', unsafe_allow_html=True)
#         fig_mid = go.Figure(go.Indicator(
#             mode="gauge+number", value=err_rate,
#             number={"suffix": "%", "font": {"size": 28, "color": "#F8FAFC"}},
#             gauge={
#                 "axis": {"range": [0, 20], "visible": False},
#                 "bar": {"color": "#2563EB"}, "bgcolor": "#1E293B",
#                 "steps": [{"range": [0, 5], "color": "#10B981"}, {"range": [5, 20], "color": "#1E3A8A"}]
#             }
#         ))
#         fig_mid.update_layout(paper_bgcolor="#131926", margin=dict(l=15, r=15, t=30, b=10), height=250)
#         st.plotly_chart(fig_mid, use_container_width=True)
#         st.markdown('<div style="text-align:center;font-size:12px;color:#64748B;">Isolation Forest Score</div></div>', unsafe_allow_html=True)

#     with op3:
#         st.markdown('<div class="g-panel"><div class="g-panel-title"><span>Correlated Incidents</span><span>↗ ⋯</span></div>', unsafe_allow_html=True)
#         fig_ring = go.Figure(data=[go.Pie(
#             values=[incidents, max(1, 50 - incidents)], hole=0.76,
#             marker_colors=["#2563EB", "#10B981"], textinfo="none", hoverinfo="none"
#         )])
#         fig_ring.add_annotation(text=f"<b>{incidents}</b>", x=0.5, y=0.5, font_size=32, font_color="#F8FAFC", showarrow=False)
#         fig_ring.update_layout(paper_bgcolor="#131926", showlegend=False, margin=dict(l=15, r=15, t=25, b=10), height=250)
#         st.plotly_chart(fig_ring, use_container_width=True)
#         st.markdown('<div style="text-align:center;font-size:12px;color:#64748B;">Deduplicated RCA Traces</div></div>', unsafe_allow_html=True)

# # ==============================================================================
# # 2. DISTRIBUTED SERVICE TOPOLOGY
# # ==============================================================================
# elif nav == "2. Distributed Service Topology":
#     st.markdown('<div class="section-strip">⌄ &nbsp; 5-Layer Distributed Architecture &amp; Telemetry</div>', unsafe_allow_html=True)
#     t_left, t_right = st.columns([1.1, 1.9])

#     with t_left:
#         topo_rows = []
#         layer_map = {
#             "API-Gateway": "Edge / Ingress",
#             "Auth-Service": "Security / IAM",
#             "Order-Service": "Core Microservice",
#             "Database-Service": "Data Persistence",
#             "K8s-Infra-Node": "Compute / Infra"
#         }
#         for svc in logs_df["service"].unique():
#             s_df = logs_df[logs_df["service"] == svc]
#             anom = len(s_df[s_df["status"] == "Anomaly"])
#             err_p = round((anom / len(s_df)) * 100, 1)
#             topo_rows.append({"Node": svc, "Layer": layer_map.get(svc, "Service"), "Logs": len(s_df), "Error %": f"{err_p}%"})
#         st.dataframe(pd.DataFrame(topo_rows), use_container_width=True, hide_index=True)

#     with t_right:
#         pos = {
#             "API-Gateway": (0.10, 0.50),
#             "Auth-Service": (0.45, 0.78),
#             "Order-Service": (0.45, 0.22),
#             "Database-Service": (0.80, 0.22),
#             "K8s-Infra-Node": (0.88, 0.68)
#         }
#         edges = [
#             ("API-Gateway", "Auth-Service"),
#             ("API-Gateway", "Order-Service"),
#             ("Order-Service", "Database-Service"),
#             ("Auth-Service", "K8s-Infra-Node"),
#             ("Database-Service", "K8s-Infra-Node")
#         ]
#         fig_topo = go.Figure()
#         for u, v in edges:
#             x0, y0 = pos[u]
#             x1, y1 = pos[v]
#             fig_topo.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines", line=dict(width=3, color="#475569"), hoverinfo="none"))

#         for node, (x, y) in pos.items():
#             s_df = logs_df[logs_df["service"] == node]
#             err_p = round((len(s_df[s_df["status"] == "Anomaly"]) / len(s_df)) * 100, 1)
#             fig_topo.add_trace(go.Scatter(
#                 x=[x], y=[y], mode="markers+text",
#                 text=[f"<b>{node}</b><br>Err: {err_p}%"], textposition="bottom center",
#                 textfont=dict(color="#F8FAFC", size=11),
#                 marker=dict(size=40, color="#2563EB", line=dict(width=3, color="#93C5FD"))
#             ))

#         fig_topo.update_layout(
#             plot_bgcolor="#131926", paper_bgcolor="#131926", showlegend=False,
#             margin=dict(l=20, r=20, t=20, b=20), height=380,
#             xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.05, 1.05]),
#             yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.0, 1.0])
#         )
#         st.plotly_chart(fig_topo, use_container_width=True)

# ==============================================================================
# 3. ROOT CAUSE ANALYSIS GRAPH (GRAFANA RCA WORKBENCH STYLE)
# ==============================================================================
# elif nav == "3. Root Cause Analysis Graph":
#     # Top Query Bar & Sub-tabs (Matching RCA Workbench Screenshot)
#     st.markdown(f"""
#     <div class="wb-query-bar">
#         🔍 &nbsp; <b>RCA workbench</b> &nbsp;|&nbsp; <span style="color:#94A3B8;">(5 Entities added)</span> &nbsp;—&nbsp;
#         <span style="color:#38BDF8;">{top_rc} connected services &amp; downstream blast radius</span>
#     </div>
#     """, unsafe_allow_html=True)

#     wb_tab1, wb_tab2, wb_tab3 = st.tabs(["🕸️ Graph Workbench", "⏱️ Incident Timeline", "📋 Correlated RCA Ledger"])

#     rc_set = set(rca_df["probable_root_cause"].unique())

#     with wb_tab1:
#         g_col, insp_col = st.columns([1.85, 1.15])

#         with g_col:
#             # Radial / Hub-and-Spoke Layout with Concentric Rings & calls/min labels
#             pos = {
#                 "API-Gateway": (0.52, 0.85),
#                 "Auth-Service": (0.22, 0.62),
#                 "Order-Service": (0.52, 0.45),
#                 "K8s-Infra-Node": (0.18, 0.20),
#                 "Database-Service": (0.82, 0.24)
#             }
#             edges_with_rates = [
#                 ("API-Gateway", "Order-Service", "238.1 calls/min", "#EF4444"),
#                 ("API-Gateway", "Auth-Service", "49.0 calls/min", "#EF4444"),
#                 ("Order-Service", "Database-Service", "144.2 calls/min", "#EF4444"),
#                 ("Auth-Service", "K8s-Infra-Node", "32.4 calls/min", "#EF4444"),
#                 ("Order-Service", "Auth-Service", "3.3 calls/min", "#64748B")
#             ]

#             fig_wb = go.Figure()

#             # Draw Edges + Edge Rate Labels (calls/min)
#             for u, v, rate_txt, e_col in edges_with_rates:
#                 x0, y0 = pos[u]
#                 x1, y1 = pos[v]
#                 fig_wb.add_trace(go.Scatter(
#                     x=[x0, x1], y=[y0, y1], mode="lines",
#                     line=dict(width=2.5 if e_col == "#EF4444" else 1.5, color=e_col),
#                     hoverinfo="none"
#                 ))
#                 # Midpoint label for calls/min
#                 mx, my = (x0 + x1) / 2, (y0 + y1) / 2
#                 fig_wb.add_trace(go.Scatter(
#                     x=[mx], y=[my + 0.03], mode="text",
#                     text=[rate_txt],
#                     textfont=dict(color="#94A3B8", size=10),
#                     hoverinfo="none"
#                 ))

#             # Draw Concentric Ring Nodes (Outer Ring + Inner Core like RCA Workbench)
#             for node, (x, y) in pos.items():
#                 is_root = node in rc_set
#                 outer_ring = "#EF4444" if is_root else "#65A30D"
#                 inner_core = "#7F1D1D" if is_root else "#4D7C0F"
#                 badge_txt = "⚙️" if "Service" in node or "Gateway" in node else ("🗄️" if "Database" in node else "☸️")

#                 # Outer halo ring
#                 fig_wb.add_trace(go.Scatter(
#                     x=[x], y=[y], mode="markers",
#                     marker=dict(size=54, color="rgba(0,0,0,0)", line=dict(width=3, color=outer_ring)),
#                     hoverinfo="none"
#                 ))
#                 # Inner filled node + label below
#                 fig_wb.add_trace(go.Scatter(
#                     x=[x], y=[y], mode="markers+text",
#                     text=[f"{badge_txt}<br><br><b>{node}</b>"],
#                     textposition="bottom center",
#                     textfont=dict(color="#E2E8F0", size=11),
#                     marker=dict(size=38, color=inner_core, line=dict(width=2, color="#F8FAFC"))
#                 ))

#             fig_wb.update_layout(
#                 plot_bgcolor="#0E131D", paper_bgcolor="#0E131D", showlegend=False,
#                 margin=dict(l=15, r=15, t=15, b=15), height=430,
#                 xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.0, 1.0]),
#                 yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.02, 1.02])
#             )
#             st.plotly_chart(fig_wb, use_container_width=True)

#         # Right Floating Entity Inspector Card (Exact match to RCA Workbench Popover)
#         with insp_col:
#             selected_entity = st.selectbox(
#                 "Inspect Entity in Workbench",
#                 ["Database-Service", "K8s-Infra-Node", "Order-Service", "Auth-Service", "API-Gateway"]
#             )
#             ent_logs = logs_df[logs_df["service"] == selected_entity]
#             ent_anom = len(ent_logs[ent_logs["status"] == "Anomaly"])
#             is_rc_ent = selected_entity in rc_set
#             status_pill = '<span class="wb-tag-crit">ROOT CAUSE ●</span>' if is_rc_ent else '<span class="wb-tag-svc">Service ●</span>'

#             st.markdown(f"""
#             <div class="wb-inspector">
#                 <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
#                     <b style="font-size:16px;color:#60A5FA;">{selected_entity}</b>
#                     {status_pill}
#                 </div>
#                 <div style="font-size:11px;color:#94A3B8;margin-bottom:12px;">
#                     ● <code>prod-k8s-cluster-01 (ap-south-1)</code>
#                 </div>
#                 <div style="border-top:1px solid #2D3748;padding-top:10px;font-size:12px;color:#CBD5E1;">
#                     <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
#                         <span style="color:#94A3B8;">Discovered</span><span>25 mins ago</span>
#                     </div>
#                     <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
#                         <span style="color:#94A3B8;">Namespace</span><span><code>distributed-core-prod</code></span>
#                     </div>
#                     <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
#                         <span style="color:#94A3B8;">Anomaly Events</span><b style="color:#F87171;">{ent_anom} alerts</b>
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)

#             with st.expander(f"▸ Insights ({ent_anom})", expanded=True):
#                 if is_rc_ent:
#                     ev_txt = rca_df[rca_df["probable_root_cause"] == selected_entity].iloc[0]["evidence_log"]
#                     st.error(f"**Primary Fault:** `{ev_txt}`")
#                 else:
#                     st.warning("Upstream cascading timeout triggered by downstream dependency failure.")

#             with st.expander("▸ Connected Entities (4)"):
#                 st.caption("• `API-Gateway` (Upstream Ingress)")
#                 st.caption("• `Order-Service` (Core Caller)")
#                 st.caption("• `Database-Service` (Data Store)")
#                 st.caption("• `K8s-Infra-Node` (Compute Host)")

#     with wb_tab2:
#         fig_tl = px.scatter(
#             df, x="timestamp", y="service", color="status",
#             color_discrete_map={"Normal": "#10B981", "Anomaly": "#EF4444"},
#             hover_data=["request_id", "message"], template="plotly_dark", height=350
#         )
#         fig_tl.update_layout(plot_bgcolor="#131926", paper_bgcolor="#131926")
#         st.plotly_chart(fig_tl, use_container_width=True)

#     with wb_tab3:
#         st.dataframe(rca_df, use_container_width=True, hide_index=True)

# # ==============================================================================
# # 4. ANOMALY DETECTION
# # ==============================================================================
# elif nav == "4. Anomaly Detection":
#     st.markdown('<div class="section-strip">⌄ &nbsp; Isolation Forest ML Anomaly Scoring &amp; Drain3 Patterns</div>', unsafe_allow_html=True)
#     a1, a2 = st.columns([1.35, 1])
#     with a1:
#         fig_anom = px.scatter(
#             df, x="timestamp", y="anomaly_score", color="status", symbol="service",
#             color_discrete_map={"Normal": "#2563EB", "Anomaly": "#EF4444"},
#             hover_data=["request_id", "level", "message"], template="plotly_dark", height=310
#         )
#         fig_anom.add_hline(y=0, line_dash="dash", line_color="#F59E0B")
#         fig_anom.update_layout(plot_bgcolor="#131926", paper_bgcolor="#131926", margin=dict(l=10, r=10, t=15, b=10))
#         st.plotly_chart(fig_anom, use_container_width=True)

#     with a2:
#         anom_by_svc = df[df["status"] == "Anomaly"]["service"].value_counts().reset_index()
#         anom_by_svc.columns = ["Service", "Anomalies"]
#         fig_bar = px.bar(
#             anom_by_svc, x="Service", y="Anomalies", color="Service",
#             color_discrete_sequence=["#EF4444", "#F59E0B", "#2563EB"], template="plotly_dark", height=310
#         )
#         fig_bar.update_layout(plot_bgcolor="#131926", paper_bgcolor="#131926", showlegend=False, margin=dict(l=10, r=10, t=15, b=10))
#         st.plotly_chart(fig_bar, use_container_width=True)

#     st.dataframe(df[df["status"] == "Anomaly"][["timestamp", "request_id", "service", "level", "anomaly_score", "event_template", "message"]], use_container_width=True, hide_index=True)

# # ==============================================================================
# # 5. REQUEST TRACE WATERFALL
# # ==============================================================================
# elif nav == "5. Request Trace Waterfall":
#     st.markdown('<div class="section-strip">⌄ &nbsp; Distributed Request Trace Waterfall (APM Span Latency)</div>', unsafe_allow_html=True)
#     incident_reqs = list(rca_df["request_id"].unique())
#     all_reqs = list(df["request_id"].unique())
#     sel_trace = st.selectbox("Select Trace / Request ID", incident_reqs + [r for r in all_reqs if r not in incident_reqs])

#     trace_spans = logs_df[logs_df["request_id"] == sel_trace].sort_values("timestamp").copy()
#     t0 = trace_spans["timestamp"].min()
#     trace_spans["offset_ms"] = (trace_spans["timestamp"] - t0).dt.total_seconds() * 1000
#     trace_spans["duration_ms"] = [35 + (i * 25) for i in range(len(trace_spans))]

#     fig_wf = go.Figure()
#     for _, row in trace_spans.iterrows():
#         bar_col = "#EF4444" if row["level"] == "ERROR" else ("#F59E0B" if row["level"] == "WARNING" else "#2563EB")
#         fig_wf.add_trace(go.Bar(
#             y=[f"{row['service']} [{row['level']}]"], x=[row["duration_ms"]], base=[row["offset_ms"]],
#             orientation="h", marker_color=bar_col, text=f"{int(row['duration_ms'])}ms — {row['message']}", textposition="auto"
#         ))

#     fig_wf.update_layout(
#         template="plotly_dark", plot_bgcolor="#131926", paper_bgcolor="#131926",
#         barmode="overlay", showlegend=False, height=280, margin=dict(l=15, r=15, t=15, b=15),
#         xaxis_title="Execution Timeline Offset (ms)", yaxis_title=""
#     )
#     st.plotly_chart(fig_wf, use_container_width=True)

#     rca_hit = rca_df[rca_df["request_id"] == sel_trace]
#     if not rca_hit.empty:
#         row_rc = rca_hit.iloc[0]
#         st.error(f"🎯 **Root Cause Verdict:** `{row_rc['probable_root_cause']}` | **Cascading:** `{row_rc['cascading_failures']}` | **Evidence:** `{row_rc['evidence_log']}`")
#     else:
#         st.success("✅ **Trace Verdict:** Healthy request execution.")

# # ==============================================================================
# # 6. LIVE LOG OBSERVER
# # ==============================================================================
# elif nav == "6. Live Log Observer":
#     st.markdown('<div class="section-strip">⌄ &nbsp; Real-Time Log Stream &amp; JSON Payload Inspector</div>', unsafe_allow_html=True)
#     l_col, r_col = st.columns([1.45, 1])
#     with l_col:
#         sev = st.radio("Severity", ["All", "ERROR", "WARNING", "INFO"], horizontal=True)
#         obs_df = df if sev == "All" else df[df["level"] == sev]
#         st.dataframe(obs_df[["timestamp", "level", "service", "request_id", "status", "message"]], use_container_width=True, hide_index=True, height=380)

#     with r_col:
#         st.markdown("**Structured JSON & Drain3 Payload**")
#         if not obs_df.empty:
#             pick_req = st.selectbox("Inspect Request ID", obs_df["request_id"].unique())
#             ev_rows = logs_df[logs_df["request_id"] == pick_req]
#             first = ev_rows.iloc[0]
#             st.json({
#                 "trace_id": pick_req,
#                 "timestamp": str(first["timestamp"]),
#                 "service": first["service"],
#                 "severity": first["level"],
#                 "ml_status": first["status"],
#                 "anomaly_score": float(first["anomaly_score"]),
#                 "drain3_template": first["event_template"],
#                 "spans": ev_rows[["service", "level", "message"]].to_dict(orient="records")
#             })

# # ==============================================================================
# # 7. AI REMEDIATION SUGGESTIONS
# # ==============================================================================
# elif nav == "7. AI Remediation Suggestions":
#     st.markdown('<div class="section-strip">⌄ &nbsp; Automated Root-Cause Remediation Playbooks</div>', unsafe_allow_html=True)
#     st.markdown("""
#     <div class="rem-card-crit">
#         <div style="display:flex;justify-content:space-between;"><b>1. Database-Service — Connection Pool Exhaustion</b><span class="badge-crit">CRITICAL ROOT CAUSE</span></div>
#         <p style="font-size:13px;color:#D1D5DB;margin-top:6px;">Increase PostgreSQL <code>max_connections</code> from 100 to 250 and deploy PgBouncer connection pooling.</p>
#     </div>
#     <div class="rem-card-crit">
#         <div style="display:flex;justify-content:space-between;"><b>2. K8s-Infra-Node — Container OOMKilled Memory Limit</b><span class="badge-crit">CRITICAL ROOT CAUSE</span></div>
#         <p style="font-size:13px;color:#D1D5DB;margin-top:6px;">Increase pod memory limits in <code>k8s-deployment.yaml</code> and enable Horizontal Pod Autoscaler (HPA).</p>
#     </div>
#     <div class="rem-card-warn">
#         <div style="display:flex;justify-content:space-between;"><b>3. API-Gateway &amp; Order-Service — Circuit Breaker Tuning</b><span class="badge-warn">CASCADING MITIGATION</span></div>
#         <p style="font-size:13px;color:#D1D5DB;margin-top:6px;">Configure exponential backoff retries and circuit breakers to isolate downstream latency spikes.</p>
#     </div>
#     """, unsafe_allow_html=True)
#     st.dataframe(rca_df[["request_id", "incident_time", "probable_root_cause", "cascading_failures", "recommended_action"]], use_container_width=True, hide_index=True)

import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Intelligent Distributed Log Analysis & Root-Cause Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------
# CUSTOM DARK ENTERPRISE CSS
# ------------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #0B1120; color: #E2E8F0; }
    section[data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1E293B; }
    .top-navbar {
        background: linear-gradient(90deg, #111827 0%, #1E293B 100%);
        padding: 14px 22px;
        border-radius: 10px;
        border: 1px solid #334155;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 18px;
    }
    .nav-breadcrumb { font-size: 13px; color: #94A3B8; }
    .time-pill {
        background-color: #1E293B;
        color: #38BDF8;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid #0284C7;
        margin-right: 8px;
    }
    .prod-pill {
        background-color: rgba(239, 68, 68, 0.15);
        color: #F87171;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid #EF4444;
    }
    .kpi-card {
        background-color: #111827;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .kpi-title { font-size: 13px; color: #94A3B8; margin-bottom: 6px; }
    .kpi-value { font-size: 26px; font-weight: 700; color: #F8FAFC; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# LOAD ALL 5 SERVICES DATA
# ------------------------------------------------------------------
ANOMALY_PATH = "data/processed_logs/anomaly_results.csv"
RCA_PATH = "data/processed_logs/rca_reports.csv"

ALL_SERVICES = [
    "API-Gateway",
    "Auth-Service",
    "Order-Service",
    "Database-Service",
    "K8s-Infra-Node"
]

@st.cache_data(ttl=10)
def load_dashboard_data():
    if os.path.exists(ANOMALY_PATH) and os.path.exists(RCA_PATH):
        logs_df = pd.read_csv(ANOMALY_PATH)
        rca_df = pd.read_csv(RCA_PATH)

        rc_col = next(
            (c for c in ["root_cause_service", "probable_root_cause", "root_cause", "service"] if c in rca_df.columns),
            None
        )
        if rc_col:
            rca_df["rc_svc"] = rca_df[rc_col].astype(str).apply(
                lambda x: next((s for s in ALL_SERVICES if s in x), "Database-Service")
            )
        else:
            rca_df["rc_svc"] = "Database-Service"

        msg_col = next(
            (c for c in ["root_cause_message", "root_cause_reason", "message", "summary"] if c in rca_df.columns),
            None
        )
        rca_df["rc_msg"] = rca_df[msg_col] if msg_col else "Cascading failure isolated at root service node."

        rem_col = next(
            (c for c in ["remediation", "suggested_fix", "action"] if c in rca_df.columns),
            None
        )
        rca_df["rc_fix"] = rca_df[rem_col] if rem_col else "Increase DB connection pool & K8s pod memory limits."

        return logs_df, rca_df

    # Fallback dataset
    sample_logs = pd.DataFrame([
        {"timestamp": "2026-11-18 10:01:01", "level": "INFO", "service": "API-Gateway", "request_id": "REQ-1001", "message": "POST /api/v1/orders routed successfully", "event_template": "POST <*> routed successfully", "anomaly_score": 0.15, "status": "Normal"},
        {"timestamp": "2026-11-18 10:01:02", "level": "INFO", "service": "Auth-Service", "request_id": "REQ-1001", "message": "JWT token validated", "event_template": "JWT token validated", "anomaly_score": 0.14, "status": "Normal"},
        {"timestamp": "2026-11-18 10:01:03", "level": "INFO", "service": "Order-Service", "request_id": "REQ-1001", "message": "Order payload verified", "event_template": "Order payload verified", "anomaly_score": 0.14, "status": "Normal"},
        {"timestamp": "2026-11-18 10:01:05", "level": "INFO", "service": "Database-Service", "request_id": "REQ-1001", "message": "COMMIT transaction completed in 12ms", "event_template": "COMMIT transaction completed in <*>ms", "anomaly_score": 0.14, "status": "Normal"},
        {"timestamp": "2026-11-18 10:01:10", "level": "INFO", "service": "K8s-Infra-Node", "request_id": "REQ-1001", "message": "Pod cpu_util=34% mem_util=48%", "event_template": "Pod cpu_util=<*>% mem_util=<*>%", "anomaly_score": 0.16, "status": "Normal"},
        {"timestamp": "2026-11-18 10:02:18", "level": "ERROR", "service": "Database-Service", "request_id": "REQ-1012", "message": "FATAL: PostgreSQL connection pool exhausted (100/100) on db-primary", "event_template": "FATAL: PostgreSQL connection pool exhausted (<*>) on <*>", "anomaly_score": -0.21, "status": "Anomaly"},
        {"timestamp": "2026-11-18 10:03:42", "level": "ERROR", "service": "K8s-Infra-Node", "request_id": "REQ-1025", "message": "OOMKilled: Container auth-pod crashed due to memory limit on worker-node", "event_template": "OOMKilled: Container <*> crashed due to memory limit on <*>", "anomaly_score": -0.19, "status": "Anomaly"},
    ])
    sample_rca = pd.DataFrame([
        {"request_id": "REQ-1012", "rc_svc": "Database-Service", "rc_msg": "FATAL: PostgreSQL connection pool exhausted (100/100) on db-primary", "rc_fix": "Increase PostgreSQL max_connections & enable PgBouncer pooling."},
        {"request_id": "REQ-1025", "rc_svc": "K8s-Infra-Node", "rc_msg": "OOMKilled: Container auth-pod crashed due to memory limit on worker-node", "rc_fix": "Increase Kubernetes pod memory limits in k8s-deployment.yaml."}
    ])
    return sample_logs, sample_rca

logs_df, rca_df = load_dashboard_data()

# ------------------------------------------------------------------
# SIDEBAR: ONLY 2 NAVIGATION MODULES + ALL 5 SERVICES FILTER
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Open 360 LogRCA")
    st.caption("Distributed Observability & RCA")
    st.markdown("---")

    nav = st.radio(
        "Navigation Modules",
        [
            "1. Executive Health Dashboard",
            "2. Root Cause Analysis Graph"
        ]
    )

    st.markdown("---")
    selected_services = st.multiselect(
        "Host / Service Filter",
        options=ALL_SERVICES,
        default=ALL_SERVICES
    )

if not selected_services:
    selected_services = ALL_SERVICES

filtered_logs = logs_df[logs_df["service"].isin(selected_services)]
total_logs = len(filtered_logs)
anom_df = filtered_logs[filtered_logs["status"] == "Anomaly"]
anom_count = len(anom_df)
top_rc = rca_df["rc_svc"].mode()[0] if not rca_df.empty else "Database-Service"

# ------------------------------------------------------------------
# TOP HEADER BAR
# ------------------------------------------------------------------
st.markdown(f"""
<div class="top-navbar">
    <div>
        <div style="font-size:17px;font-weight:700;color:#F8FAFC;letter-spacing:0.01em;">
            🛡️ Intelligent Distributed Log Analysis &amp; Root-Cause Detection
        </div>
        <div class="nav-breadcrumb" style="margin-top:3px;">
            Dashboards &nbsp;&gt;&nbsp; <b>{nav}</b> &nbsp;|&nbsp; env: <code>prod</code> &nbsp;|&nbsp; namespace: <code>distributed-core</code>
        </div>
    </div>
    <div>
        <span class="time-pill">🕒 Last 30 Mins</span>
        <span class="prod-pill">● Root Cause: {top_rc}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# MODULE 1: EXECUTIVE HEALTH DASHBOARD
# ------------------------------------------------------------------
if nav == "1. Executive Health Dashboard":
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Active Microservices</div><div class="kpi-value">{len(selected_services)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Ingested Volume</div><div class="kpi-value">{total_logs:,} Logs</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">ML Anomalies (Isolation Forest)</div><div class="kpi-value" style="color:#F87171;">{anom_count}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Correlated Incidents</div><div class="kpi-value" style="color:#38BDF8;">{len(rca_df)}</div></div>', unsafe_allow_html=True)

    st.markdown("### System & Infrastructure Health Gauges")
    g_cols = st.columns(3)
    gauge_services = ["Database-Service", "K8s-Infra-Node", "Auth-Service"]
    for idx, svc in enumerate(gauge_services):
        svc_logs = logs_df[logs_df["service"] == svc]
        svc_err = round((len(svc_logs[svc_logs["status"] == "Anomaly"]) / len(svc_logs)) * 100, 1) if len(svc_logs) > 0 else 0.0
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=svc_err,
            number={"suffix": "%", "font": {"color": "#F8FAFC"}},
            title={"text": f"{svc}", "font": {"size": 15, "color": "#CBD5E1"}},
            gauge={
                "axis": {"range": [0, 15], "tickcolor": "#64748B"},
                "bar": {"color": "#EF4444" if svc_err > 5 else "#F59E0B"},
                "bgcolor": "#1E293B",
                "steps": [
                    {"range": [0, 3], "color": "#064E3B"},
                    {"range": [3, 7], "color": "#78350F"},
                    {"range": [7, 15], "color": "#7F1D1D"}
                ]
            }
        ))
        fig_gauge.update_layout(height=230, margin=dict(l=15, r=15, t=45, b=15), paper_bgcolor="#111827", font={"color": "#E2E8F0"})
        with g_cols[idx]:
            st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("### Isolation Forest Anomaly Scoring & Live Log Stream")
    fig_scat = px.scatter(
        filtered_logs,
        x="timestamp",
        y="anomaly_score",
        color="status",
        symbol="service",
        hover_data=["request_id", "service", "message"],
        color_discrete_map={"Normal": "#38BDF8", "Anomaly": "#EF4444"}
    )
    fig_scat.add_hline(y=0.0, line_dash="dash", line_color="#F59E0B", annotation_text="Anomaly Threshold (0.0)")
    fig_scat.update_layout(height=320, paper_bgcolor="#111827", plot_bgcolor="#0F172A", font=dict(color="#E2E8F0"))
    st.plotly_chart(fig_scat, use_container_width=True)

    cols_to_show = [c for c in ["timestamp", "level", "service", "request_id", "event_template", "status", "message"] if c in filtered_logs.columns]
    st.dataframe(filtered_logs[cols_to_show].head(100), use_container_width=True, height=260)

# ------------------------------------------------------------------
# MODULE 2: ROOT CAUSE ANALYSIS GRAPH
# ------------------------------------------------------------------
elif nav == "2. Root Cause Analysis Graph":
    st.subheader("Distributed Service Topology & Root Cause Analysis Graph")
    col_graph, col_info = st.columns([2, 1])

    with col_graph:
        # 5-Node Causal Dependency Graph
        nodes_x = [0.0, 0.5, 0.5, 1.0, 1.0]
        nodes_y = [0.5, 0.8, 0.2, 0.8, 0.2]
        node_names = ["API-Gateway", "Auth-Service", "Order-Service", "K8s-Infra-Node", "Database-Service"]
        node_colors = ["#38BDF8", "#F59E0B", "#F59E0B", "#EF4444", "#EF4444"]
        node_sizes = [38, 38, 38, 48, 54]

        edges = [
            (0, 1), (0, 2), (1, 3), (2, 4)
        ]

        fig_net = go.Figure()
        for src, dst in edges:
            fig_net.add_trace(go.Scatter(
                x=[nodes_x[src], nodes_x[dst]],
                y=[nodes_y[src], nodes_y[dst]],
                mode="lines",
                line=dict(width=3, color="#EF4444" if dst in [3, 4] else "#64748B"),
                hoverinfo="none"
            ))

        fig_net.add_trace(go.Scatter(
            x=nodes_x,
            y=nodes_y,
            mode="markers+text",
            text=node_names,
            textposition="top center",
            textfont=dict(size=13, color="#F8FAFC"),
            marker=dict(size=node_sizes, color=node_colors, line=dict(width=2.5, color="#F8FAFC"))
        ))

        fig_net.update_layout(
            height=420,
            showlegend=False,
            xaxis=dict(range=[-0.2, 1.25], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[0.0, 1.05], showgrid=False, zeroline=False, showticklabels=False),
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_net, use_container_width=True)

    with col_info:
        st.markdown("#### Entity Inspector & AI Remediation")
        inspect_svc = st.selectbox("Inspect Root-Cause Node", ["Database-Service", "K8s-Infra-Node"])
        svc_incidents = rca_df[rca_df["rc_svc"] == inspect_svc]
        st.metric("Isolated Root-Cause Incidents", len(svc_incidents))
        if not svc_incidents.empty:
            st.error(f"**Root Cause Signature:**\n{svc_incidents.iloc[0]['rc_msg']}")
            st.success(f"**AI Remediation Action:**\n{svc_incidents.iloc[0]['rc_fix']}")

    st.markdown("### Correlated Root-Cause Incident Reports")
    st.dataframe(rca_df, use_container_width=True, height=250)