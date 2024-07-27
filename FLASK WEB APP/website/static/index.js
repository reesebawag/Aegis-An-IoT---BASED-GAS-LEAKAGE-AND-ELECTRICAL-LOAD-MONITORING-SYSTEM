$(document).ready(function () {
  const ctx = document.getElementById("myChart").getContext("2d");
  const electricalCtx = document.getElementById("electricalChart").getContext("2d");

  const myChart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [{ label: "Gas Value" }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(255, 99, 132, 1)'],
    },
  });

  const electricalChart = new Chart(electricalCtx, {
    type: "line",
    data: {
      datasets: [{ label: "Electrical Value" }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(54, 162, 235, 1)'],
    },
  });

  function addGasData(label, data) {
    myChart.data.labels.push(label);
    myChart.data.datasets.forEach((dataset) => {
      dataset.data.push(data);
    });
    myChart.update();
  }

  function addElectricalData(label, data) {
    electricalChart.data.labels.push(label);
    electricalChart.data.datasets.forEach((dataset) => {
      dataset.data.push(data);
    });
    electricalChart.update();
  }

  function removeFirstGasData() {
    myChart.data.labels.splice(0, 1);
    myChart.data.datasets.forEach((dataset) => {
      dataset.data.shift();
    });
  }

  function removeFirstElectricalData() {
    electricalChart.data.labels.splice(0, 1);
    electricalChart.data.datasets.forEach((dataset) => {
      dataset.data.shift();
    });
  }
  

  const MAX_DATA_COUNT = 10;
  var socket = io.connect();

  socket.on("updateSensorData", function (msg) {
    console.log("Received sensorData :: " + msg.date + " :: " + msg.value);


    if (myChart.data.labels.length > MAX_DATA_COUNT) {
      removeFirstGasData();
    }
    addGasData(msg.date, msg.value);


  });
  socket.on("updateElectricalData", function (msg) {
    console.log("Received electrical sensorData :: " + msg.date + " :: " + msg.value);
  
    // Check if msg.value is not null before adding data to the chart
    if (msg.value !== null && msg.value !== undefined) {
      if (electricalChart.data.labels.length > MAX_DATA_COUNT) {
        removeFirstElectricalData();
      }
      addElectricalData(msg.date, msg.value);
    } else {
      console.log("Received null or undefined value for electrical sensorData.");
      // Handle the situation where msg.value is null or undefined (e.g., display an error message, skip adding data, etc.)
    }
  });

  socket.on("gas_alert", function (msg) {
    alert("Gas Alert: " + msg.message);
});

socket.on("current_alert", function (msg) {
    alert("Current Alert: " + msg.message);
});

  socket.on('disconnect', function() {
    console.log('Disconnected from the server');
    // Attempt to reconnect here
  });
});
