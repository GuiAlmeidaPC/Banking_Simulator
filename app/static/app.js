(() => {
  const form = document.getElementById("loan-form");
  const submitBtn = document.getElementById("submit-btn");
  const errorEl = document.getElementById("form-error");
  const yearsInput = document.getElementById("years");
  const yearsReadout = document.getElementById("years-readout");
  const tableBody = document.querySelector("#schedule-table tbody");
  const legendEl = document.getElementById("legend");
  const canvas = document.getElementById("chart");

  let chart = null;

  // -- Formatting --------------------------------------------------------
  const currency = new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  });
  const percent = new Intl.NumberFormat(undefined, {
    style: "percent",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  const FORMATTERS = {
    first_payment: (v) => currency.format(v),
    last_payment: (v) => currency.format(v),
    total_repayments: (v) => currency.format(v),
    interest_income: (v) => currency.format(v),
    funding_cost: (v) => currency.format(v),
    net_interest_income: (v) => currency.format(v),
    net_interest_margin: (v) => percent.format(v),
  };

  // -- UI helpers --------------------------------------------------------
  function setYearsReadout() {
    const n = Number(yearsInput.value);
    yearsReadout.textContent = `${n} ${n === 1 ? "year" : "years"}`;
  }

  function setLoading(loading) {
    submitBtn.classList.toggle("loading", loading);
    submitBtn.disabled = loading;
    submitBtn.querySelector(".btn-label").textContent = loading
      ? "Simulating…"
      : "Simulate";
  }

  function showError(message) {
    errorEl.textContent = message;
    errorEl.hidden = false;
  }

  function clearError() {
    errorEl.hidden = true;
    errorEl.textContent = "";
  }

  function flashMetrics() {
    document.querySelectorAll(".metric-value").forEach((el) => {
      el.classList.remove("flash");
      // force reflow so the animation restarts
      void el.offsetWidth;
      el.classList.add("flash");
    });
  }

  // -- Rendering ---------------------------------------------------------
  function renderMetrics(data) {
    Object.entries(FORMATTERS).forEach(([key, fmt]) => {
      const el = document.querySelector(`[data-metric="${key}"]`);
      if (el) el.textContent = fmt(data[key]);
    });

    const nii = document.querySelector('[data-metric="net_interest_income"]');
    const nim = document.querySelector('[data-metric="net_interest_margin"]');
    [nii, nim].forEach((el) => {
      el.classList.remove("positive", "negative");
      const v = key(el);
      if (data[v] > 0) el.classList.add("positive");
      else if (data[v] < 0) el.classList.add("negative");
    });

    flashMetrics();
  }

  function key(el) {
    return el.getAttribute("data-metric");
  }

  function renderSchedule(schedule) {
    tableBody.replaceChildren();
    if (!schedule) return;
    const frag = document.createDocumentFragment();
    for (const row of schedule) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.month}</td>
        <td class="num">${currency.format(row.payment)}</td>
        <td class="num">${currency.format(row.interest)}</td>
        <td class="num">${currency.format(row.principal)}</td>
        <td class="num">${currency.format(row.funding_cost)}</td>
        <td class="num">${currency.format(row.remaining_balance)}</td>
      `;
      frag.appendChild(tr);
    }
    tableBody.appendChild(frag);
  }

  // -- Chart -------------------------------------------------------------
  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function renderChart(schedule) {
    if (!schedule || schedule.length === 0) return;

    const labels = schedule.map((r) => r.month);
    const balance = schedule.map((r) => r.remaining_balance);
    const interest = schedule.map((r) => r.interest);
    const principal = schedule.map((r) => r.principal);
    const funding = schedule.map((r) => r.funding_cost);

    const colors = {
      accent: cssVar("--accent") || "#0f766e",
      positive: cssVar("--positive") || "#047857",
      negative: cssVar("--negative") || "#b45309",
      muted: cssVar("--text-muted") || "#6b6963",
      border: cssVar("--border") || "#e7e5e0",
      text: cssVar("--text") || "#1c1b1a",
    };

    const datasets = [
      {
        type: "line",
        label: "Outstanding balance",
        data: balance,
        borderColor: colors.accent,
        backgroundColor: colors.accent + "22",
        fill: true,
        tension: 0.25,
        borderWidth: 2,
        pointRadius: 0,
        yAxisID: "y",
        order: 0,
      },
      {
        type: "bar",
        label: "Principal",
        data: principal,
        backgroundColor: colors.accent + "AA",
        stack: "payment",
        yAxisID: "y1",
        order: 2,
      },
      {
        type: "bar",
        label: "Interest income",
        data: interest,
        backgroundColor: colors.positive + "AA",
        stack: "payment",
        yAxisID: "y1",
        order: 2,
      },
      {
        type: "bar",
        label: "Funding cost",
        data: funding,
        backgroundColor: colors.negative + "AA",
        stack: "funding",
        yAxisID: "y1",
        order: 2,
      },
    ];

    if (chart) chart.destroy();
    chart = new Chart(canvas, {
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: cssVar("--surface"),
            borderColor: cssVar("--border-strong"),
            borderWidth: 1,
            titleColor: colors.text,
            bodyColor: colors.text,
            padding: 12,
            callbacks: {
              title: (items) => `Month ${items[0].label}`,
              label: (item) =>
                `${item.dataset.label}: ${currency.format(item.parsed.y)}`,
            },
          },
        },
        scales: {
          x: {
            title: { display: true, text: "Month", color: colors.muted },
            grid: { color: colors.border, drawTicks: false },
            ticks: { color: colors.muted, maxTicksLimit: 12 },
          },
          y: {
            position: "left",
            title: { display: true, text: "Balance", color: colors.muted },
            grid: { color: colors.border },
            ticks: {
              color: colors.muted,
              callback: (v) => currency.format(v).replace(/\.\d+$/, ""),
            },
          },
          y1: {
            position: "right",
            title: { display: true, text: "Per month", color: colors.muted },
            grid: { drawOnChartArea: false },
            ticks: {
              color: colors.muted,
              callback: (v) => currency.format(v).replace(/\.\d+$/, ""),
            },
          },
        },
      },
    });

    legendEl.replaceChildren();
    for (const d of datasets) {
      const item = document.createElement("span");
      item.className = "legend-item";
      const swatch = document.createElement("span");
      swatch.className = "legend-swatch";
      swatch.style.background =
        typeof d.backgroundColor === "string"
          ? d.backgroundColor
          : d.borderColor;
      item.append(swatch, document.createTextNode(d.label));
      legendEl.appendChild(item);
    }
  }

  // -- Networking --------------------------------------------------------
  async function simulate(payload) {
    const res = await fetch("/calculate-loan-returns?include_schedule=true", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      const detail = body?.detail;
      const msg = Array.isArray(detail)
        ? detail.map((d) => d.msg).join("; ")
        : detail || `Request failed (${res.status})`;
      throw new Error(msg);
    }
    return res.json();
  }

  function readForm() {
    const regime = form.querySelector('input[name="amortization"]:checked');
    return {
      principal: Number(form.principal.value),
      annual_interest_rate: Number(form.annual_interest_rate.value),
      years: Number(form.years.value),
      funding_cost_rate: Number(form.funding_cost_rate.value),
      amortization: regime ? regime.value : "price",
    };
  }

  async function run() {
    clearError();
    const payload = readForm();
    setLoading(true);
    try {
      const data = await simulate(payload);
      renderMetrics(data);
      renderChart(data.schedule);
      renderSchedule(data.schedule);
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // -- Wire up -----------------------------------------------------------
  yearsInput.addEventListener("input", setYearsReadout);
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    run();
  });
  // Re-simulate when the user toggles the amortization regime.
  form.querySelectorAll('input[name="amortization"]').forEach((el) => {
    el.addEventListener("change", run);
  });

  // Initial render: populate with default values
  setYearsReadout();
  run();
})();
