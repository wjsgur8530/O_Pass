// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Generate random daily visitors data (for demonstration)
function generateDailyData(month, days) {
  var data = [];
  for (var i = 0; i < days; i++) {
    var visitors = Math.floor(Math.random() * 100) + 50; // Random number of visitors (between 50 and 150)
    data.push(visitors);
  }
  return data;
}

// Calculate labels for the days
function generateDayLabels(month, days) {
  var labels = [];
  for (var i = 1; i <= days; i++) {
    var label = month + '월 ' + i + '일';
    if (i === new Date().getDate()) { // Check if it's today's date
      label += ' (오늘)';
    }
    labels.push(label);
  }
  return labels;
}

// Get the number of days in a month
function getDaysInMonth(month, year) {
  return new Date(year, month, 0).getDate();
}

var ctx = document.getElementById("dailyVisitorAreaChart");
var currentYear = new Date().getFullYear();
var currentMonth = new Date().getMonth() + 1; // Months are 0-based in JavaScript
var daysInMonth = getDaysInMonth(currentMonth, currentYear);

var myLineChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: generateDayLabels(currentMonth, daysInMonth),
    datasets: [{
      label: "방문자 수",
      lineTension: 0.3,
      backgroundColor: "rgba(78, 115, 223, 0.05)",
      borderColor: "rgba(78, 115, 223, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(78, 115, 223, 1)",
      pointBorderColor: "rgba(78, 115, 223, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
      pointHoverBorderColor: "rgba(78, 115, 223, 1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: generateDailyData(currentMonth, daysInMonth),
    }],
  },
  options: {
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      xAxes: [{
        time: {
          unit: 'date'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 7
        }
      }],
      yAxes: [{
        ticks: {
          maxTicksLimit: 5,
          padding: 10,
          // Include a comma separator in the ticks
          callback: function(value, index, values) {
            return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
          }
        },
        gridLines: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      }],
    },
    legend: {
      display: false
    },
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      titleMarginBottom: 10,
      titleFontColor: '#6e707e',
      titleFontSize: 14,
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      intersect: false,
      mode: 'index',
      caretPadding: 10,
      callbacks: {
        label: function(tooltipItem, chart) {
          var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
          return datasetLabel + ': ' + tooltipItem.yLabel.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        }
      }
    }
  }
});
