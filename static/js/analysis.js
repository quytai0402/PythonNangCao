document.getElementById('monthSelect').addEventListener('change', function() {
    const selectedMonth = this.value;
    window.location.href = `/analysis?month=${selectedMonth}`;
});

const expenseData = JSON.parse('{{ expense_data|tojson|safe }}');
const incomeData = JSON.parse('{{ income_data|tojson|safe }}');
const ctx = document.getElementById('analysisChart').getContext('2d');

if (Object.keys(expenseData).length === 0 && Object.keys(incomeData).length === 0) {
    ctx.font = "20px Arial";
    ctx.fillText("Không có dữ liệu cho tháng đã chọn", 50, 50);
} else {
    const labels = Array.from(new Set([...Object.keys(expenseData), ...Object.keys(incomeData)])).sort();
    const expenseValues = labels.map(date => expenseData[date] || 0);
    const incomeValues = labels.map(date => incomeData[date] || 0);

    const analysisChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels.map(date => new Date(date).toLocaleDateString('vi-VN', { day: 'numeric', month: 'long', year: 'numeric' })),
            datasets: [
                {
                    label: 'Chi tiêu hàng ngày',
                    data: expenseValues,
                    borderColor: 'rgba(255, 99, 132, 1)',  // Red color for expenses
                    borderWidth: 1,
                    fill: false
                },
                {
                    label: 'Thu nhập hàng ngày',
                    data: incomeValues,
                    borderColor: 'rgba(54, 162, 235, 1)',  // Blue color for income
                    borderWidth: 1,
                    fill: false
                }
            ]
        },
        options: {
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {
                        unit: 'day',
                        tooltipFormat: 'DD MMM YYYY',
                        displayFormats: {
                            day: 'DD MMM YYYY'
                        }
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Ngày'
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        callback: function(value) {
                            return value + ' VNĐ'; // Định dạng hiển thị tiền tệ
                        }
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Số tiền'
                    }
                }]
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem) {
                        return `${tooltipItem.yLabel} VNĐ`; // Hiển thị số tiền với đơn vị
                    }
                }
            }
        }
    });
}