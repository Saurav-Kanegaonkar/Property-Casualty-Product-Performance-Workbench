const data = window.workbenchData;

const fmtMoney = (value) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);

const fmtPct = (value) => `${Number(value).toFixed(1)}%`;

const riskClass = (value, medium = 98, high = 106) => {
  if (value >= high) return "risk-high";
  if (value >= medium) return "risk-medium";
  return "risk-low";
};

function renderSummary() {
  const items = [
    ["Earned premium", fmtMoney(data.summary.earnedPremium), "modeled book"],
    ["Loss ratio", fmtPct(data.summary.lossRatio), "portfolio average"],
    ["Combined ratio", fmtPct(data.summary.combinedRatio), "with expense load"],
    ["Retention", fmtPct(data.summary.retention), "rolling average"],
    ["Segments", data.summary.segments, "underwriting cuts"],
    ["Filing items", data.summary.filingItems, "rate, rule, form"],
  ];

  document.getElementById("summaryMetrics").innerHTML = items
    .map(
      ([label, value, detail]) => `
        <article class="metric">
          <span>${label}</span>
          <strong>${value}</strong>
          <em>${detail}</em>
        </article>
      `
    )
    .join("");
}

function renderStateFilter() {
  const select = document.getElementById("stateFilter");
  Object.keys(data.states).forEach((state) => {
    const option = document.createElement("option");
    option.value = state;
    option.textContent = state;
    select.appendChild(option);
  });
  select.addEventListener("change", () => renderPortfolio(select.value));
}

function renderPortfolio(state = "all") {
  const stateRows = Object.entries(data.states);
  document.getElementById("stateMap").innerHTML = stateRows
    .map(([code, row]) => {
      const selected = state === code ? " is-selected" : "";
      return `
        <button class="state-tile ${riskClass(row.combinedRatio)}${selected}" type="button" data-state="${code}">
          <strong>${code}</strong>
          <span>${fmtPct(row.combinedRatio)} combined</span>
          <em>${row.actionCount} action flags</em>
        </button>
      `;
    })
    .join("");

  document.querySelectorAll(".state-tile").forEach((button) => {
    button.addEventListener("click", () => {
      document.getElementById("stateFilter").value = button.dataset.state;
      renderPortfolio(button.dataset.state);
    });
  });

  const rows = data.actionQueue.filter((row) => state === "all" || row.state === state);
  document.getElementById("actionRows").innerHTML = rows
    .map(
      (row) => `
        <tr>
          <td><strong>${row.segment_id}</strong><span>${row.territory}</span></td>
          <td>${row.state}</td>
          <td>${row.product_line}</td>
          <td class="${riskClass(row.combined_ratio)}">${fmtPct(row.combined_ratio)}</td>
          <td>${fmtPct(row.retention)}</td>
          <td>${fmtPct(row.rate_indication)}</td>
          <td>${row.recommendation}</td>
        </tr>
      `
    )
    .join("");

  const maxPremium = Math.max(...data.productMix.map((row) => row.earnedPremium));
  document.getElementById("productMix").innerHTML = data.productMix
    .map((row) => {
      const width = Math.max(10, (row.earnedPremium / maxPremium) * 100);
      return `
        <div class="bar-row">
          <div>
            <strong>${row.productLine}</strong>
            <span>${fmtMoney(row.earnedPremium)} earned</span>
          </div>
          <div class="bar-track">
            <span style="width:${width}%"></span>
          </div>
          <em class="${riskClass(row.combinedRatio)}">${fmtPct(row.combinedRatio)}</em>
        </div>
      `;
    })
    .join("");
}

function renderFiling() {
  document.getElementById("filingRows").innerHTML = data.filingQueue
    .map(
      (row) => `
        <tr>
          <td>${row.state}</td>
          <td>${row.product_line}</td>
          <td>${fmtPct(row.rate_indication)}</td>
          <td>${fmtPct(row.proposed_rate_change)}</td>
          <td><span class="pill">${row.filing_complexity}</span></td>
          <td>${fmtPct(row.readiness_score)}</td>
          <td>${row.filing_status}</td>
        </tr>
      `
    )
    .join("");

  document.getElementById("filingCards").innerHTML = data.filingQueue
    .slice(0, 5)
    .map(
      (row) => `
        <article class="filing-card">
          <div>
            <strong>${row.state} ${row.product_line}</strong>
            <span>${row.filing_status}</span>
          </div>
          <p>${row.manual_sections}</p>
          <small>Owner: ${row.owner}</small>
        </article>
      `
    )
    .join("");

  document.getElementById("requirements").innerHTML = data.requirements
    .map(
      (row) => `
        <article class="requirement">
          <span>${row.requirement_id}</span>
          <strong>${row.capability}</strong>
          <p>${row.business_requirement}</p>
          <em>${row.requesting_team} to ${row.delivery_partner}</em>
        </article>
      `
    )
    .join("");
}

function renderAutomation() {
  document.getElementById("automationRows").innerHTML = data.automationQueue
    .map(
      (row) => `
        <tr>
          <td><strong>${row.segment_id}</strong><span>${row.territory}</span></td>
          <td>${row.state}</td>
          <td>${row.product_line}</td>
          <td>${Number(row.exposure_index).toFixed(1)}</td>
          <td>${fmtPct(row.inspection_completion)}</td>
          <td>${fmtPct(row.guideline_exception_rate)}</td>
          <td><span class="score">${Number(row.review_score).toFixed(1)}</span></td>
        </tr>
      `
    )
    .join("");

  document.getElementById("automationCards").innerHTML = data.automationQueue
    .slice(0, 4)
    .map(
      (row) => `
        <article class="review-card">
          <div>
            <strong>${row.segment_id}</strong>
            <span>${row.state} ${row.product_line}</span>
          </div>
          <p>${row.recommendation}</p>
          <dl>
            <div><dt>Telematics</dt><dd>${fmtPct(row.telematics_eligible)}</dd></div>
            <div><dt>Approval</dt><dd>${fmtPct(row.automation_approval_rate)}</dd></div>
            <div><dt>Review</dt><dd>${Number(row.review_score).toFixed(1)}</dd></div>
          </dl>
        </article>
      `
    )
    .join("");
}

function attachTabs() {
  const tabs = document.querySelectorAll(".tab");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((item) => item.classList.remove("is-active"));
      document.querySelectorAll(".view").forEach((view) => view.classList.remove("is-active"));
      tab.classList.add("is-active");
      document.getElementById(`${tab.dataset.view}View`).classList.add("is-active");
    });
  });
}

renderSummary();
renderStateFilter();
renderPortfolio();
renderFiling();
renderAutomation();
attachTabs();
