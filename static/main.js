async function loadData(userId, year) {
  const res = await fetch(`/api/finances/${userId}/${year}`);
  const data = await res.json();

  if (!Array.isArray(data) || data.length === 0 || data.error) {
    document.getElementById("message").textContent = data.error || "No data yet for this user/year.";
    document.getElementById("displaySection").classList.add("hidden");
    return;
  }

  const userName = data[0].user_name;
  document.getElementById("userHeader").textContent = `User: ${userName} — Year: ${year}`;

  // Fill table
  const tbody = document.querySelector("#financeTable tbody");
  tbody.innerHTML = "";
  for (const row of data) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${row.month}</td><td>${row.amount}</td>`;
    tbody.appendChild(tr);
  }

  // Chart
  const ctx = document.getElementById("financeChart").getContext("2d");
  if (window._chart) window._chart.destroy();
  window._chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.map(r => r.month),
      datasets: [{
        label: "Monthly Amount",
        data: data.map(r => r.amount)
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true }
      }
    }
  });

  document.getElementById("displaySection").classList.remove("hidden");
}

document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = document.getElementById("message");
  msg.textContent = "";
  const fileInput = document.getElementById("file");
  const userId = document.getElementById("userId").value;
  const year = document.getElementById("year").value;

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const res = await fetch(`/api/finances/upload/${userId}/${year}`, {
    method: "POST",
    body: formData
  });
  const body = await res.json();
  msg.textContent = body.message || body.error || "Done";
  if (res.ok) {
    loadData(userId, year);
  }
});
