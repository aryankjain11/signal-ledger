import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .models import Analysis

GREEN = "#36d6a4"
RED = "#ff6b82"
BLUE = "#6ca6ff"


def price_chart(analysis: Analysis, show_bands: bool = False) -> go.Figure:
    frame = analysis.frame.iloc[-250:]
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        row_heights=[0.65, 0.18, 0.17], vertical_spacing=0.035)
    fig.add_trace(go.Candlestick(x=frame.index, open=frame.open, high=frame.high,
                                 low=frame.low, close=frame.close, name="Daily OHLC",
                                 increasing_line_color=GREEN, decreasing_line_color=RED), row=1, col=1)
    for column, color, label in (("ema_20", BLUE, "EMA20"), ("ema_50", "#f6c86a", "EMA50")):
        fig.add_trace(go.Scatter(x=frame.index, y=frame[column], name=label,
                                 line=dict(color=color, width=1.4)), row=1, col=1)
    if show_bands:
        for column in ("bb_upper", "bb_lower"):
            fig.add_trace(go.Scatter(x=frame.index, y=frame[column], name=column,
                                     line=dict(color="#738199", width=1, dash="dot"), showlegend=False), row=1, col=1)
    for kind, color in (("high", RED), ("low", GREEN)):
        pivots = [p for p in analysis.pivots if p.kind == kind and p.timestamp >= frame.index[0].date().isoformat()]
        fig.add_trace(go.Scatter(x=[p.timestamp for p in pivots], y=[p.price for p in pivots],
                                 mode="markers", name=f"Swing {kind} (delayed confirmation)",
                                 showlegend=False,
                                 customdata=[p.detected_at for p in pivots],
                                 hovertemplate="Formed %{x}<br>Price %{y:.4f}<br>Knowable %{customdata}<extra></extra>",
                                 marker=dict(color=color, size=7, symbol="circle-open")), row=1, col=1)
    for zone in analysis.zones:
        fig.add_hrect(y0=zone["low"], y1=zone["high"], fillcolor=GREEN if zone["role"] == "Support" else RED,
                      opacity=0.08, line_width=0, row=1, col=1)
    latest = {}
    for event in analysis.events:
        if "coordinates" in event:
            latest[event["id"]] = event
    for event in sorted(latest.values(), key=lambda e: e["detected_at"])[-10:]:
        if event["detected_at"] < frame.index[0].date().isoformat():
            continue
        fig.add_trace(go.Scatter(x=[c[0] for c in event["coordinates"]],
                                 y=[c[1] for c in event["coordinates"]],
                                 name=f"{event['name']} · {event['status']}", mode="lines+markers",
                                 showlegend=False,
                                 line=dict(color=BLUE, width=1, dash="dash"),
                                 text=[f"Known {event['detected_at']} · {event['status']}"] * len(event["coordinates"]),
                                 hovertemplate="%{text}<br>%{x}: %{y:.4f}<extra></extra>"), row=1, col=1)
        for boundary, points in event.get("boundary_coordinates", {}).items():
            fig.add_trace(go.Scatter(x=[c[0] for c in points], y=[c[1] for c in points], mode="lines",
                name=f"{event['name']} {boundary}", line=dict(color="#c498ff", dash="dot", width=1), showlegend=False), row=1, col=1)
    candles = [e for e in analysis.events if "coordinates" not in e and
               e["detected_at"] >= frame.index[0].date().isoformat()]
    fig.add_trace(go.Scatter(x=[e["detected_at"] for e in candles], y=[e["price"] for e in candles],
                             text=[e["name"] for e in candles], name="Candle observations", mode="markers",
                             showlegend=False,
                             marker=dict(color="#f6c86a", size=6, symbol="diamond"),
                             hovertemplate="%{text}<br>%{x}<extra></extra>"), row=1, col=1)
    colors = [GREEN if c >= o else RED for c, o in zip(frame.close, frame.open)]
    fig.add_trace(go.Bar(x=frame.index, y=frame.volume, name="Volume", marker_color=colors,
                         opacity=0.65, showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=frame.index, y=frame.rsi_14, name="RSI14",
                             line=dict(color=BLUE, width=1.5), showlegend=False), row=3, col=1)
    for level in (30, 70):
        fig.add_hline(y=level, line_dash="dot", line_color="#576579", row=3, col=1)
    fig.update_yaxes(range=[0, 100], row=3, col=1)
    fig.update_layout(height=720, template="plotly_dark", paper_bgcolor="#101a2b",
                      plot_bgcolor="#101a2b", margin=dict(l=12, r=12, t=45, b=10),
                      legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0, font=dict(size=10)),
                      hovermode="x unified", xaxis_rangeslider_visible=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#202c40")
    return fig
