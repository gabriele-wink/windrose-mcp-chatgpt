# WindRose MCP for ChatGPT

Connect **ChatGPT** — or your own app built on the **OpenAI API** — to [WindRose](https://windroses.world): live readings, history, climatology and records from the public WindRose network of personal weather stations and from **your own stations**, plus heat-stress indices, pollutant dispersion, forecasts, the official hardware manuals, and your alerts and monitoring.

The MCP server is hosted by WindRose at `https://app.windroses.world/api/mcp.php` (Streamable HTTP, OAuth 2.1). This repo is the setup guide and ready-to-run API examples.

## Requirements

- A WindRose account on the **Pro** plan (read-only tools) or **Business** (all tools, including creating and deleting alerts and monitoring windows).
- For ChatGPT: a ChatGPT plan that allows custom connectors / developer mode (availability depends on your ChatGPT plan and, for workspaces, on your admin).

## ChatGPT — custom connector

1. In ChatGPT open **Settings → Apps & Connectors** (called *Connectors* on some plans) → **Advanced settings** and enable **Developer mode** if your plan requires it.
2. **Create** a connector:
   - Name: `WindRose`
   - Description: *Live and historical data from the WindRose weather station network*
   - MCP server URL: `https://app.windroses.world/api/mcp.php`
   - Authentication: **OAuth**
3. ChatGPT registers itself and opens a WindRose page: sign in and **Allow**.
4. In a chat, enable the WindRose connector and ask away.

Menu names in ChatGPT change from time to time; what matters is a custom MCP connector with the URL above and OAuth. ChatGPT finds the authorization server on its own (RFC 9728 metadata + dynamic client registration). Disconnect from ChatGPT, or from **WindRose → Settings → API & MCP access → Connected AI apps**.

For deep research and company-knowledge style use, the server provides the `search` and `fetch` tools ChatGPT looks for: `search` finds stations and manual pages, `fetch` returns a station's metadata and live reading or a manual page.

## OpenAI API (Responses API)

Use WindRose as a remote MCP tool from your own code, authenticated with a WindRose API key (WindRose → Settings → API & MCP access → Generate key; the token is `<key_id>.<key_secret>`):

```python
response = client.responses.create(
    model="gpt-5",
    tools=[{
        "type": "mcp",
        "server_label": "windrose",
        "server_url": "https://app.windroses.world/api/mcp.php",
        "headers": {"Authorization": f"Bearer {os.environ['WINDROSE_API_KEY']}"},
        "require_approval": "never",
    }],
    input="Where is it raining right now in northern Italy?",
)
```

Complete examples: [`examples/responses_api.py`](examples/responses_api.py) and [`examples/responses_api.mjs`](examples/responses_api.mjs). They auto-approve only the read tools; tools that change your account still go through approval. Set `OPENAI_MODEL` to the model you use.

## Example questions

- *Where is it raining right now in northern Italy?*
- *Which stations within 50 km of Verona had the strongest gusts this week?*
- *Rank the stations of Lombardy by total rain in October and show coverage.*
- *What is the record low at station 3, and how does this month compare with its normals?*
- *What does the Ecowitt GW2000 manual say about Wi-Fi provisioning?*
- *Estimate the dispersion footprint at my station with the current wind.*

## Tools

All values are metric, with the unit in the key name (`temp_c`, `gust_kmh`, `pressure_hpa`, `rain_mm`, `rain_rate_mm_h`…); unix times are `ts`.

| Tool | Access | What it answers |
|---|---|---|
| `network_now` | public | Latest reading of every station the user can see (all PUBLIC stations of the WindRose network + the user's own), filtered and sorted. |
| `network_daily` | public | One number per station over a date range, from daily summaries (kept forever): sector studies across the network. |
| `list_stations` | public | Find stations (public network + the user's own) by name/place text, area or source, with ids, position, source and last reading time. |
| `station_info` | public | Metadata of one station: place, coordinates, elevation, timezone, data source, what it measures now, how much history exists (daily summaries and full-resolution archive) and the retention. |
| `station_current` | public | Live reading of any visible station: every outdoor quantity, derived indices (heat index, wind chill, THW, WBGT, UTCI, wet bulb) and air quality; hardware/indoor values for the owner only. |
| `station_daily` | public | Daily summaries of one station (one row per local day, up to 731 days): min/max/avg temperature with times, humidity, dew point, pressure, rain, max rain rate, mean wind, max gust with time and direction, solar, UV, evapotranspiration. |
| `station_climatology` | public | Monthly climatology of one station from its daily summaries: per month temperature means/extremes, rain total and rain days, frost/hot days, tropical nights, gusts, ET; plus normals by calendar month across years. |
| `station_records` | public | Records of one station over its history or a range: highest/lowest temperature with time, warmest/coldest day, wettest day and month, max rain rate, strongest gust, pressure extremes, max UV. |
| `station_series` | public | Time series of one station: raw archive records (max 3 days) or hourly aggregates (max 31 days): temperature, humidity, dew point, wind, gust, direction, rain, rain rate, pressure, solar, UV. |
| `compute_indices` | public | Comfort and heat-stress calculator for any conditions (real or hypothetical): dew point, heat index, wind chill, humidex, wet bulb, WBGT (Dimiceli and Liljegren) and UTCI with its stress category. |
| `dispersion` | public | Pollutant dispersion screening (the model behind the app's plume map): EPA ISC3/SCREEN3 Gaussian plume, Cirillo-Poli below 1 m/s. |
| `forecast` | public | Weather forecast (Open-Meteo model, NOT a station) at any point or at a station: daily and hourly temperature, rain and probability, wind, gusts, pressure, clouds, UV, sunrise/sunset. |
| `climate_era5` | public | Historical daily weather from the ERA5 reanalysis (Open-Meteo model, NOT a station) at any point or station, up to 3 years per call: compare a station with the model, fill gaps, climate context. |
| `sun_times` | public | Sunrise, sunset, solar noon, civil twilight and day length at a point or station on a date. |
| `search_manual` | public | Search the official manuals of the supported hardware (Davis Vantage Pro2/Vue, WeatherLink Live/Console, AirLink; Ecowitt gateways, WS69/WS90 arrays, HP2550; Netatmo; WeatherFlow Tempest; AcuRite Atlas). |
| `list_manuals` | public | The manuals indexed for search_manual: brand, model, link, when last checked for a newer revision. |
| `search` | public | Search WindRose: stations (public network + the user's own) by name or place, and the indexed hardware manuals. |
| `fetch` | public | Full content of a search result: "station:<id>" (metadata + live reading) or "manual:<slug>:<page>" (that page of the manual). |
| `account_plan` | owner | The user's plan, its limits (stations, history, AI, exports, alerts, monitoring, API/MCP) and current usage. |
| `alert_sensors` | public | Catalog of the quantities an alert rule can watch (key, label, unit family, yes/no flags). |
| `list_alerts` | owner | The user's alert rules (all stations, or one): sensor, operator, threshold (metric), cooldown, mode, enabled, last triggered. |
| `create_alert` | write | Create a push alert rule on one of the user's stations. |
| `delete_alert` | write | Delete one of the user's alert rules by id (list_alerts gives ids). |
| `set_alert_enabled` | write | Pause or resume one of the user's alert rules. |
| `list_monitors` | owner | The user's monitoring windows (scheduled 1-minute recordings, max 4 h each): station, name, start/end, sample count. |
| `monitor_samples` | owner | Samples recorded by one of the user's monitors (metric: temp, humidity, dew point, wind, gust, pressure, rain rate, UV). |
| `create_monitor` | write | Schedule a monitoring window on one of the user's stations: the station is read every minute from starts_at to ends_at (max 4 h). |
| `delete_monitor` | write | Delete one of the user's monitors and its samples. |

*Access*: **public** = the public WindRose network plus your own stations; **owner** = your account only; **write** = changes your account, Business plan only.

## Data and privacy

- You see every **public** station and **your own** stations; other users' private stations are never reachable, and hardware, indoor and console values are visible only to the station owner.
- `forecast` and `climate_era5` are Open-Meteo model data, not station measurements.
- Derived indices and the dispersion model are estimates, not certified measurements.
- Station names are written by their owners and reach the model as text: keep approval on for tools that change your account.

## Troubleshooting

| Symptom | Fix |
|---|---|
| The connector fails at sign-in | Make sure you are on WindRose Pro or Business; sign in with the same account you use in the app. |
| 401 with the API | Check the token format `<key_id>.<key_secret>` and that the key is not revoked. |
| 429 *Rate limit exceeded* | 60 requests per minute per key or connection. |
| No write tools | Creating/deleting alerts and monitors needs Business and the `mcp:write` permission granted at sign-in. |

## Italiano

In ChatGPT crea un connettore personalizzato (**Impostazioni → App e connettori → Avanzate**, modalità sviluppatore se richiesta) con URL `https://app.windroses.world/api/mcp.php` e autenticazione **OAuth**, poi accedi con il tuo account WindRose. Serve WindRose Pro (sola lettura) o Business (anche allerte e monitoraggi). Per l'API OpenAI usa gli esempi in `examples/` con una chiave WindRose.

## License

MIT — see [LICENSE](LICENSE). The WindRose service itself is subject to the [WindRose terms](https://windroses.world).
