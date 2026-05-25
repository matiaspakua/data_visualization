import pandas as pd
import plotly.graph_objects as go
import json
from pathlib import Path

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

FONT = "Inter, Arial, sans-serif"
COLORS = {
    "Cursor CLI": "#20808D",
    "Gemini": "#E85D26",
    "Copilot CLI": "#7C5CBF",
}

# Canonical benchmark values validated from the report inputs.
# These regenerate the same charts without the Perplexity watermark.
canonical = pd.DataFrame({
    "Provider": ["Cursor CLI", "Gemini", "Copilot CLI"],
    "Model": ["Composer 2 Fast", "Gemini 3.1 Pro Preview", "GPT-5.4"],
    "n_runs": [25, 4, 28],
    "mean_score": [8.83, 8.15, 8.38],
    "mean_conf": [0.92, 0.94, 0.89],
    "mean_outcome": [8.15, 7.67, 7.52],
    "mean_task_tok_k": [659.77, 496.18, 3260.00],
    "mean_input_tok_k": [115.99, 370.45, 1630.00],
    "mean_output_tok_k": [20.51, 0.90, 13.08],
    "mean_cache_tok_k": [568.77, 124.83, 1610.00],
    "cost_input": [0.1740, 0.7409, 4.0871],
    "cost_output": [0.1538, 0.0108, 0.1962],
    "cost_cache": [0.1991, 0.0250, 0.4030],
    "premium_req": [6.5, 0.0, 1.0],
    "prem_cost": [0.26, 0.0, 0.04],
    "outcome_per_m_tok": [13.15, 16.38, 3.19],
    "outcome_per_dollar": [15.94, 9.87, 1.60],
})

canonical["cost_token"] = canonical["cost_input"] + canonical["cost_output"] + canonical["cost_cache"]
canonical["cost_total"] = canonical["cost_token"] + canonical["prem_cost"]
canonical["cost_per_m_tok"] = canonical["cost_token"] / (canonical["mean_task_tok_k"] / 1000)

BASE_LAYOUT = dict(
    width=960,
    height=540,
    font=dict(family=FONT, size=14, color="#1a1a1a"),
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=70, r=40, t=110, b=70),
)


def save_meta(name: str, caption: str, description: str):
    with open(OUTPUT_DIR / f"{name}.meta.json", "w") as f:
        json.dump({"caption": caption, "description": description}, f)


# Chart 1: estimated cost per run
fig1 = go.Figure()
fig1.add_trace(go.Bar(
    name="Token cost",
    x=canonical["Provider"],
    y=canonical["cost_token"],
    marker_color=[COLORS[p] for p in canonical["Provider"]],
    text=[f"${v:.2f}" for v in canonical["cost_token"]],
    textposition="inside",
    textfont=dict(color="white", size=13),
))
fig1.add_trace(go.Bar(
    name="Premium req cost",
    x=canonical["Provider"],
    y=canonical["prem_cost"],
    marker_color="rgba(120,120,120,0.75)",
    text=[f"+${v:.2f}" if v > 0 else "" for v in canonical["prem_cost"]],
    textposition="outside",
))
for _, row in canonical.iterrows():
    fig1.add_annotation(
        x=row["Provider"],
        y=row["cost_total"] + 0.15,
        text=f"<b>${row['cost_total']:.2f}</b>",
        showarrow=False,
        font=dict(size=13),
    )
fig1.update_layout(
    **BASE_LAYOUT,
    barmode="stack",
    title=dict(text="Estimated Cost per Run: Token Billing + Premium Requests<br><span style='font-size:15px;font-weight:normal;'>Source: pricing summary × mean token usage per run</span>"),
    legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="center", x=0.5),
)
fig1.update_xaxes(title_text="AI Provider")
fig1.update_yaxes(title_text="Cost per run ($)", tickprefix="$", gridcolor="#e8e8e8")
fig1.write_image(OUTPUT_DIR / "chart1_cost_per_run.png")
save_meta("chart1_cost_per_run.png", "Estimated cost per run by provider", "Stacked bar chart of token billing and premium request cost per run.")


# Chart 2: outcome per dollar
fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=canonical["Provider"],
    y=canonical["outcome_per_dollar"],
    marker_color=[COLORS[p] for p in canonical["Provider"]],
    text=[f"{v:.2f}" for v in canonical["outcome_per_dollar"]],
    textposition="outside",
    cliponaxis=False,
))
fig2.update_layout(
    **BASE_LAYOUT,
    title=dict(text="Outcome per Dollar by Provider<br><span style='font-size:15px;font-weight:normal;'>Higher is better value for money</span>"),
)
fig2.update_xaxes(title_text="AI Provider")
fig2.update_yaxes(title_text="Outcome per $", range=[0, 18], gridcolor="#e8e8e8")
fig2.write_image(OUTPUT_DIR / "chart2_outcome_per_dollar.png")
save_meta("chart2_outcome_per_dollar.png", "Outcome per dollar by provider", "Bar chart comparing value efficiency across providers.")


# Chart 3: outcome per million task tokens
fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=canonical["Provider"],
    y=canonical["outcome_per_m_tok"],
    marker_color=[COLORS[p] for p in canonical["Provider"]],
    text=[f"{v:.2f}" for v in canonical["outcome_per_m_tok"]],
    textposition="outside",
    cliponaxis=False,
))
fig3.update_layout(
    **BASE_LAYOUT,
    title=dict(text="Outcome per Million Task Tokens<br><span style='font-size:15px;font-weight:normal;'>Higher is better token efficiency</span>"),
)
fig3.update_xaxes(title_text="AI Provider")
fig3.update_yaxes(title_text="Outcome per 1M tokens", range=[0, 18], gridcolor="#e8e8e8")
fig3.write_image(OUTPUT_DIR / "chart3_outcome_per_m_tok.png")
save_meta("chart3_outcome_per_m_tok.png", "Outcome per million task tokens", "Bar chart comparing token efficiency across providers.")


# Chart 4: mean task tokens per run
fig4 = go.Figure()
fig4.add_trace(go.Bar(
    x=canonical["Provider"],
    y=canonical["mean_task_tok_k"],
    marker_color=[COLORS[p] for p in canonical["Provider"]],
    text=[f"{v/1000:.2f}M" if v >= 1000 else f"{v:.0f}K" for v in canonical["mean_task_tok_k"]],
    textposition="outside",
    cliponaxis=False,
))
fig4.update_layout(
    **BASE_LAYOUT,
    title=dict(text="Mean Task Tokens per Run<br><span style='font-size:15px;font-weight:normal;'>Raw token volume by provider</span>"),
)
fig4.update_xaxes(title_text="AI Provider")
fig4.update_yaxes(title_text="Task tokens (K)", gridcolor="#e8e8e8")
fig4.write_image(OUTPUT_DIR / "chart4_mean_task_tokens.png")
save_meta("chart4_mean_task_tokens.png", "Mean task tokens per run", "Bar chart showing raw token consumption per average run.")


# Chart 5: radar comparison
categories = [
    "Mean Score",
    "Confidence",
    "Mean Outcome",
    "Outcome/M tok",
    "Outcome/$",
]
series = {
    "Cursor CLI": [8.83/10, 0.92, 8.15/10, 13.15/20, 15.94/16],
    "Gemini": [8.15/10, 0.94, 7.67/10, 16.38/20, 9.87/16],
    "Copilot CLI": [8.38/10, 0.89, 7.52/10, 3.19/20, 1.60/16],
}
fig5 = go.Figure()
for name, vals in series.items():
    fig5.add_trace(go.Scatterpolar(
        r=vals + [vals[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=name,
        line=dict(color=COLORS[name], width=3),
        opacity=0.35,
    ))
fig5.update_layout(
    width=760,
    height=600,
    font=dict(family=FONT, size=13, color="#1a1a1a"),
    paper_bgcolor="white",
    margin=dict(l=80, r=80, t=110, b=90),
    title=dict(text="Quality, Confidence, Efficiency, and Value Radar<br><span style='font-size:15px;font-weight:normal;'>Normalized 0–1 scale across five dimensions</span>"),
    legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="center", x=0.5),
    polar=dict(
        bgcolor="white",
        radialaxis=dict(visible=True, range=[0, 1], gridcolor="#e8e8e8", tickfont=dict(size=11)),
        angularaxis=dict(tickfont=dict(size=12)),
    ),
)
fig5.write_image(OUTPUT_DIR / "chart5_radar.png")
save_meta("chart5_radar.png", "Radar comparison across five normalized dimensions", "Radar chart comparing providers across quality, confidence, outcome, token efficiency, and dollar efficiency.")

print("Charts regenerated in ./output without Perplexity branding.")
