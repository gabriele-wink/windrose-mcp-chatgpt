// Ask GPT about the WindRose weather network through the OpenAI Responses API.
//
//   npm install openai
//   export OPENAI_API_KEY=sk-...
//   export WINDROSE_API_KEY=wr_xxxxxxxxxxxxxxxx.your_key_secret_here
//   node responses_api.mjs "Compare October rain totals across the stations of Lombardy"
import OpenAI from 'openai'

const client = new OpenAI()
const question = process.argv.slice(2).join(' ') || 'Where is it raining right now in northern Italy?'

const response = await client.responses.create({
  model: process.env.OPENAI_MODEL || 'gpt-5',
  tools: [{
    type: 'mcp',
    server_label: 'windrose',
    server_description: 'Live and historical data from the WindRose network of personal weather stations.',
    server_url: 'https://app.windroses.world/api/mcp.php',
    headers: { Authorization: `Bearer ${process.env.WINDROSE_API_KEY}` },
    // Read-only data tools: no approval round-trip. Write tools (alerts, monitors) still ask.
    require_approval: { never: { tool_names: [
      'network_now', 'network_daily', 'list_stations', 'station_info', 'station_current',
      'station_daily', 'station_climatology', 'station_records', 'station_series',
      'compute_indices', 'dispersion', 'forecast', 'climate_era5', 'sun_times',
      'search_manual', 'list_manuals', 'search', 'fetch',
    ] } },
  }],
  input: question,
})
console.log(response.output_text)
