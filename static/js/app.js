const form = document.querySelector("#prediction-form");
const predictButton = document.querySelector("#predict-button");
const formStatus = document.querySelector("#form-status");
const resultsPanel = document.querySelector(".results-panel");
const resultsContent = document.querySelector("#results-content");
const emptyState = document.querySelector("#empty-state");
const resultState = document.querySelector("#result-state");
const gridInput = document.querySelector("#grid");
const gridValue = document.querySelector("#grid-value");
const driverSearch = document.querySelector("#driver-search");
const driverValue = document.querySelector("#driver");

function updateDriverValue() {
    const searchValue = driverSearch.value.trim();
    const matchingOption = [...document.querySelectorAll("#driver-options option")]
        .find((option) => option.value.toLocaleLowerCase() === searchValue.toLocaleLowerCase());

    driverValue.value = matchingOption?.dataset.driverRef || "";
    driverSearch.setCustomValidity(
        searchValue && !matchingOption ? "Choose a driver from the suggestions." : ""
    );
}

driverSearch.addEventListener("input", updateDriverValue);
driverSearch.addEventListener("change", updateDriverValue);

function updateGridValue() {
    const min = Number(gridInput.min);
    const max = Number(gridInput.max);
    const value = Number(gridInput.value);
    const progress = ((value - min) / (max - min)) * 100;

    gridValue.value = String(value);
    gridInput.setAttribute("aria-valuetext", `Position ${value}`);
    gridInput.style.setProperty("--range-progress", `${progress}%`);
}

gridInput.addEventListener("input", updateGridValue);
updateGridValue();

form.addEventListener("input", () => {
    if (!resultsContent.hidden) {
        resultsPanel.classList.add("is-stale");
        resultState.textContent = "Inputs changed";
        resultState.parentElement.classList.remove("is-ready");
        formStatus.textContent = "Configuration changed. Run the prediction again to refresh these results.";
        formStatus.classList.remove("is-error");
    }
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!form.reportValidity()) {
        return;
    }

    predictButton.disabled = true;
    predictButton.querySelector(".button-label").textContent = "Calculating…";
    formStatus.textContent = "Running the prediction models…";
    formStatus.classList.remove("is-error");

    try {
        const response = await fetch(form.action, {
            method: "POST",
            body: new FormData(form),
            headers: { Accept: "application/json" }
        });
        let payload;
        try {
            payload = await response.json();
        } catch {
            throw new Error(`The server returned an unreadable response (${response.status}). Please try again.`);
        }

        if (!response.ok) {
            throw new Error(payload.error || `Prediction failed (${response.status}). Please check the selections and try again.`);
        }

        const position = Number(payload.position);
        const probability = Number(payload.podium_prob);
        if (!Number.isFinite(position) || !Number.isFinite(probability) || !payload.chart) {
            throw new Error("The prediction response was incomplete. Please try again.");
        }

        document.querySelector("#position-value").textContent = position.toFixed(2);
        document.querySelector("#probability-value").textContent = `${probability.toFixed(2)}%`;
        document.querySelector("#probability-fill").style.width = `${Math.max(0, Math.min(100, probability))}%`;
        const probabilityTrack = document.querySelector("#probability-track");
        probabilityTrack.setAttribute("aria-valuenow", String(Math.max(0, Math.min(100, probability))));
        document.querySelector("#summary-driver").textContent = driverSearch.value;
        document.querySelector("#summary-constructor").textContent = document.querySelector("#constructor").value;
        document.querySelector("#summary-circuit").textContent = document.querySelector("#circuit").value;
        document.querySelector("#summary-grid").textContent = `P${gridInput.value}`;
        document.querySelector("#prediction-chart").src = `data:image/png;base64,${payload.chart}`;
        document.querySelector("#prediction-chart").alt =
            `Prediction chart for ${driverSearch.value}: finishing position ${position.toFixed(2)} and podium probability ${probability.toFixed(2)} percent.`;

        emptyState.hidden = true;
        resultsContent.hidden = false;
        resultsPanel.classList.remove("is-stale");
        resultState.textContent = "Estimate ready";
        resultState.parentElement.classList.add("is-ready");
        formStatus.textContent = "Prediction complete.";
    } catch (error) {
        formStatus.textContent = error instanceof Error ? error.message : "The prediction could not be completed. Please try again.";
        formStatus.classList.add("is-error");
    } finally {
        predictButton.disabled = false;
        predictButton.querySelector(".button-label").textContent = "Predict race";
    }
});

const metricsError = document.querySelector("#metrics-error");
const metricFormatters = {
    rmse: (value) => value.toFixed(2),
    r2: (value) => value.toFixed(2),
    accuracy: (value) => `${(value * 100).toFixed(0)}%`,
    precision: (value) => `${(value * 100).toFixed(0)}%`,
    recall: (value) => `${(value * 100).toFixed(0)}%`
};

async function loadMetrics() {
    try {
        const response = await fetch("/metrics", { headers: { Accept: "application/json" } });
        let metrics;
        try {
            metrics = await response.json();
        } catch {
            throw new Error(`The server returned an unreadable response (${response.status}).`);
        }
        if (!response.ok) {
            throw new Error(metrics.error || `Metrics could not be loaded (${response.status}).`);
        }

        for (const [key, format] of Object.entries(metricFormatters)) {
            const value = Number(metrics[key]);
            const element = document.querySelector(`[data-metric="${key}"]`);
            if (!Number.isFinite(value)) {
                element.textContent = "Unavailable";
                element.classList.add("unavailable");
            } else {
                element.textContent = format(value);
            }
        }
    } catch (error) {
        for (const element of document.querySelectorAll("[data-metric]")) {
            element.textContent = "Unavailable";
            element.classList.add("unavailable");
        }
        metricsError.textContent = error instanceof Error
            ? `Unable to load model metrics: ${error.message}`
            : "Unable to load model metrics. Please refresh to try again.";
        metricsError.hidden = false;
    }
}

loadMetrics();

const navToggle = document.querySelector(".nav-toggle");
const primaryNav = document.querySelector("#primary-nav");

navToggle.addEventListener("click", () => {
    const isExpanded = navToggle.getAttribute("aria-expanded") === "true";
    navToggle.setAttribute("aria-expanded", String(!isExpanded));
    primaryNav.classList.toggle("is-open", !isExpanded);
});

primaryNav.addEventListener("click", (event) => {
    if (event.target instanceof HTMLAnchorElement) {
        navToggle.setAttribute("aria-expanded", "false");
        primaryNav.classList.remove("is-open");
    }
});

if ("IntersectionObserver" in window) {
    const navigationLinks = [...primaryNav.querySelectorAll("a")];
    const linkBySection = new Map(
        navigationLinks.map((link) => [link.hash.slice(1), link])
    );
    const sectionObserver = new IntersectionObserver((entries) => {
        for (const entry of entries) {
            if (entry.isIntersecting) {
                for (const link of navigationLinks) {
                    link.removeAttribute("aria-current");
                }
                linkBySection.get(entry.target.id)?.setAttribute("aria-current", "location");
            }
        }
    }, { rootMargin: "-20% 0px -70% 0px" });

    for (const id of linkBySection.keys()) {
        const section = document.getElementById(id);
        if (section) {
            sectionObserver.observe(section);
        }
    }
}
