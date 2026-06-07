(function () {
    var canvas = document.getElementById("skillsRadar");
    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    var labels = [
        "Python",
        "MySQL",
        "Linux",
        "数据分析",
        "大模型部署",
        "低代码平台",
        "提示词工程",
    ];

    var data = [8, 6, 5, 6, 5, 5, 6];

    var accent = getComputedStyle(document.documentElement)
        .getPropertyValue("--accent")
        .trim() || "#58a6ff";

    new Chart(canvas, {
        type: "radar",
        data: {
            labels: labels,
            datasets: [{
                label: "技能熟练度",
                data: data,
                backgroundColor: "rgba(88, 166, 255, 0.15)",
                borderColor: accent,
                borderWidth: 2,
                pointBackgroundColor: accent,
                pointBorderColor: "#0d1117",
                pointHoverBackgroundColor: "#79b8ff",
                pointRadius: 4,
                pointHoverRadius: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    min: 0,
                    max: 10,
                    ticks: {
                        stepSize: 2,
                        color: "#6e7681",
                        backdropColor: "transparent",
                        font: { size: 11 },
                    },
                    grid: { color: "rgba(48, 54, 61, 0.8)" },
                    angleLines: { color: "rgba(48, 54, 61, 0.6)" },
                    pointLabels: {
                        color: "#8b949e",
                        font: { size: 12, weight: "500" },
                    },
                },
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "#1c2128",
                    titleColor: "#e6edf3",
                    bodyColor: "#8b949e",
                    borderColor: "#30363d",
                    borderWidth: 1,
                    callbacks: {
                        label: function (ctx) {
                            return "熟练度: " + ctx.raw + " / 10";
                        },
                    },
                },
            },
        },
    });
})();
