import React, { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";
import DevicesList from "./DevicesList";
import AddDeviceForm from "./AddDeviceForm";

function App() {
  const [devices, setDevices] = useState([]);

  const fetchDevices = () => {
    axios
      .get("/api/devices")
      .then((response) => setDevices(response.data))
      .catch((error) =>
        console.error("There was an error fetching the devices:", error)
      );
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  return (
    <div className="App">
      <h1>doorLock</h1>
      <AddDeviceForm fetchDevices={fetchDevices} />
      <DevicesList devices={devices} fetchDevices={fetchDevices} />
    </div>
  );
}

export default App;
