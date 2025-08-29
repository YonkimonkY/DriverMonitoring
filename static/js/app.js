// Conexión Socket.IO
const socket = io();

// Configurar gráficos
const yawnsCtx = document.getElementById("yawnsChart").getContext("2d");
const eyesCtx  = document.getElementById("eyesChart").getContext("2d");
const alertsCtx= document.getElementById("alertsChart").getContext("2d");

const makeDoughnut = (ctx, label) =>
  new Chart(ctx, {
    type: "doughnut",
    data: { labels: [label], datasets: [{ data: [0], backgroundColor: ["#00E5A8"] }] },
    options: {
      plugins: {
        legend: { display: false }
      },
      cutout: "70%"
    }
  });

const yawnsChart  = makeDoughnut(yawnsCtx, "Bostezos");
const eyesChart   = makeDoughnut(eyesCtx,  "Cierres de ojos");
const alertsChart = makeDoughnut(alertsCtx,"Alertas");

const yawnsTotalEl  = document.getElementById("yawnsTotal");
const eyesTotalEl   = document.getElementById("eyesTotal");
const alertsTotalEl = document.getElementById("alertsTotal");
const eventsList    = document.getElementById("eventsList");

function updateDoughnut(chart, value) {
  chart.data.datasets[0].data = [value];
  chart.update();
}

// Recibe estadísticas periódicas
socket.on("stats", (data) => {
  const { yawns_total, eye_closures_total, alerts_total } = data;

  yawnsTotalEl.textContent  = yawns_total;
  eyesTotalEl.textContent   = eye_closures_total;
  alertsTotalEl.textContent = alerts_total;

  updateDoughnut(yawnsChart,  yawns_total);
  updateDoughnut(eyesChart,   eye_closures_total);
  updateDoughnut(alertsChart, alerts_total);
});

// Recibe lista de eventos recientes
socket.on("events", (items) => {
  eventsList.innerHTML = "";
  items.slice().reverse().forEach((txt) => {
    const li = document.createElement("li");
    li.textContent = txt;
    eventsList.appendChild(li);
  });
});
