from fastapi.responses import HTMLResponse


DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TruckTwin AI | Engineering Dashboard</title>
  <style>
    :root { color-scheme: dark; --bg: #101820; --panel: #182632; --text: #e8f0f2;
      --muted: #9bb0b8; --accent: #57d1b8; --warn: #f0b85b; --danger: #ef7777; }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--text);
      font: 15px/1.5 system-ui, -apple-system, sans-serif; }
    main { max-width: 1180px; margin: 0 auto; padding: 32px 20px 56px; }
    header { display: flex; justify-content: space-between; align-items: end; gap: 20px;
      border-bottom: 1px solid #2d414d; padding-bottom: 22px; }
    h1, h2, p { margin: 0; } h1 { font-size: clamp(1.7rem, 4vw, 2.5rem); }
    h2 { font-size: 1.05rem; margin-bottom: 16px; } .eyebrow { color: var(--accent);
      font-size: .75rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }
    .muted { color: var(--muted); } .grid { display: grid; gap: 16px; margin-top: 24px; }
    .metrics { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
    .layout { grid-template-columns: minmax(220px, .8fr) minmax(0, 2fr); }
    .panel { background: var(--panel); border: 1px solid #2d414d; border-radius: 10px; padding: 20px; }
    .metric { font-size: 2rem; font-weight: 700; } .vehicle-list { display: grid; gap: 8px; }
    button { width: 100%; cursor: pointer; border: 1px solid #395663; border-radius: 7px;
      background: #203743; color: var(--text); padding: 11px 12px; text-align: left; }
    button:hover, button.selected { border-color: var(--accent); background: #264b52; }
    .vehicle-name { font-weight: 650; } .vehicle-meta { color: var(--muted); font-size: .8rem; }
    .signals { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }
    .signal { border-left: 3px solid var(--accent); padding-left: 12px; }
    .signal-label { color: var(--muted); font-size: .8rem; } .signal-value { font-size: 1.3rem; font-weight: 650; }
    table { width: 100%; border-collapse: collapse; } th, td { padding: 10px 6px;
      border-bottom: 1px solid #2d414d; text-align: left; } th { color: var(--muted);
      font-size: .75rem; text-transform: uppercase; } .badge { border-radius: 99px;
      padding: 3px 8px; font-size: .75rem; font-weight: 700; text-transform: uppercase; }
    .high { background: #633b43; color: #ffb4b4; } .medium { background: #624d2b; color: #ffd994; }
    .low { background: #27504d; color: #9ce6d7; } .empty { color: var(--muted); padding: 14px 0; }
    @media (max-width: 720px) { header { display: block; } .layout { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
<main>
  <header>
    <div><div class="eyebrow">Software-defined vehicle engineering</div>
      <h1>TruckTwin AI</h1><p class="muted">Synthetic fleet diagnostics and telemetry</p></div>
    <div id="refresh-status" class="muted">Loading...</div>
  </header>
  <section class="grid metrics">
    <div class="panel"><div class="muted">Vehicles</div><div id="vehicle-count" class="metric">-</div></div>
    <div class="panel"><div class="muted">Selected events</div><div id="event-count" class="metric">-</div></div>
    <div class="panel"><div class="muted">Software version</div><div id="software-version" class="metric">-</div></div>
  </section>
  <section class="grid layout">
    <aside class="panel"><h2>Fleet</h2><div id="vehicle-list" class="vehicle-list"></div></aside>
    <div class="grid" style="margin-top:0">
      <section class="panel"><h2 id="vehicle-title">Select a vehicle</h2>
        <div id="telemetry" class="signals"><div class="empty">No vehicle selected.</div></div></section>
      <section class="panel"><h2>Diagnostic events</h2>
        <div id="events"><div class="empty">No vehicle selected.</div></div></section>
    </div>
  </section>
</main>
<script>
  const state = { vehicles: [], selected: null };
  const $ = (id) => document.getElementById(id);
  const formatDate = (value) => new Date(value).toLocaleString();
  function signal(label, value, unit) {
    return `<div class="signal"><div class="signal-label">${label}</div>
      <div class="signal-value">${value} ${unit}</div></div>`;
  }
  async function loadVehicles() {
    const response = await fetch('/vehicles');
    if (!response.ok) throw new Error('Unable to load vehicles');
    state.vehicles = await response.json();
    $('vehicle-count').textContent = state.vehicles.length;
    const list = $('vehicle-list');
    list.innerHTML = state.vehicles.length ? state.vehicles.map((vehicle) =>
      `<button class="${vehicle === state.selected ? 'selected' : ''}" data-vehicle="${vehicle}">
        <div class="vehicle-name">${vehicle}</div><div class="vehicle-meta">Telemetry available</div></button>`
    ).join('') : '<div class="empty">No telemetry received yet.</div>';
    list.querySelectorAll('button').forEach((button) =>
      button.addEventListener('click', () => selectVehicle(button.dataset.vehicle)));
    if (!state.selected && state.vehicles.length) await selectVehicle(state.vehicles[0]);
  }
  async function selectVehicle(vehicle) {
    state.selected = vehicle;
    await Promise.all([loadVehicles(), loadVehicleData(vehicle)]);
  }
  async function loadVehicleData(vehicle) {
    const [telemetryResponse, eventsResponse] = await Promise.all([
      fetch(`/vehicles/${encodeURIComponent(vehicle)}/telemetry`),
      fetch(`/vehicles/${encodeURIComponent(vehicle)}/events`)
    ]);
    if (!telemetryResponse.ok || !eventsResponse.ok) throw new Error('Unable to load vehicle data');
    const telemetry = await telemetryResponse.json();
    const events = await eventsResponse.json();
    const latest = telemetry[telemetry.length - 1];
    $('vehicle-title').textContent = vehicle;
    $('software-version').textContent = latest ? latest.software_version : '-';
    $('event-count').textContent = events.length;
    $('telemetry').innerHTML = latest ? [
      signal('Speed', latest.signals.speed_kmh, 'km/h'),
      signal('Engine temperature', latest.signals.engine_temperature_c, '°C'),
      signal('Battery voltage', latest.signals.battery_voltage_v, 'V'),
      signal('Brake pressure', latest.signals.brake_pressure_bar, 'bar')
    ].join('') : '<div class="empty">No telemetry available.</div>';
    $('events').innerHTML = events.length ? `<table><thead><tr><th>Time</th><th>Type</th>
      <th>Severity</th><th>Message</th></tr></thead><tbody>${events.slice().reverse().map((event) =>
      `<tr><td>${formatDate(event.timestamp)}</td><td>${event.event_type}</td>
      <td><span class="badge ${event.severity}">${event.severity}</span></td><td>${event.message}</td></tr>`
    ).join('')}</tbody></table>` : '<div class="empty">No diagnostic events.</div>';
    $('refresh-status').textContent = `Updated ${new Date().toLocaleTimeString()}`;
  }
  async function refresh() {
    try { await loadVehicles(); if (state.selected) await loadVehicleData(state.selected); }
    catch (error) { $('refresh-status').textContent = error.message; }
  }
  refresh(); setInterval(refresh, 10000);
</script>
</body>
</html>"""


def dashboard_response() -> HTMLResponse:
    return HTMLResponse(DASHBOARD_HTML)
