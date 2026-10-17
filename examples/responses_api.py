"""
Ask GPT about the WindRose weather network through the OpenAI Responses API,
with WindRose as a remote MCP tool.

    pip install openai
    export OPENAI_API_KEY=sk-...
    export WINDROSE_API_KEY=wr_xxxxxxxxxxxxxxxx.your_key_secret_here   # WindRose → Settings → API & MCP access
    python responses_api.py "Where is it raining right now in northern Italy?"
"""
import os
import sys

from openai import OpenAI

client = OpenAI()
question = " ".join(sys.argv[1:]) or "Which public WindRose stations near Milan recorded the strongest gust today?"

response = client.responses.create(
    model=os.environ.get("OPENAI_MODEL", "gpt-5"),
    tools=[{
        "type": "mcp",
        "server_label": "windrose",
        "server_description": "Live and historical data from the WindRose network of personal weather stations.",
        "server_url": "https://app.windroses.world/api/mcp.php",
        "headers": {"Authorization": f"Bearer {os.environ['WINDROSE_API_KEY']}"},
        # Read-only tools run without asking; keep approval for anything that writes.
        "require_approval": {"never": {"tool_names": [
            "network_now", "network_daily", "list_stations", "station_info", "station_current",
            "station_daily", "station_climatology", "station_records", "station_series",
            "compute_indices", "dispersion", "forecast", "climate_era5", "sun_times",
            "search_manual", "list_manuals", "search", "fetch",
        ]}},
    }],
    input=question,
)
print(response.output_text)
