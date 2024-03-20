import React, { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";
import "./dark-mode.css";
import DevicesList from "./DevicesList";
import AddDeviceForm from "./AddDeviceForm";

function App() {
  const [devices, setDevices] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(false);

  const fetchDevices = () => {
    axios
      .get("/api/devices")
      .then((response) => setDevices(response.data))
      .catch((error) =>
        console.error("There was an error fetching the devices:", error)
      );
  };

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);

    if (!isDarkMode) {
      document.body.classList.add("dark-mode");
    } else {
      document.body.classList.remove("dark-mode");
    }
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  useEffect(() => {
    const isDarkModeEnabled = localStorage.getItem("isDarkMode") === "true";
    setIsDarkMode(isDarkModeEnabled);
  }, []);

  useEffect(() => {
    localStorage.setItem("isDarkMode", isDarkMode.toString());
  }, [isDarkMode]);

  return (
    <div className={`App`}>
      <h1>doorLock</h1>
      <AddDeviceForm fetchDevices={fetchDevices} />
      <DevicesList devices={devices} fetchDevices={fetchDevices} />
      <button onClick={toggleDarkMode} className="dark-mode-btn">
        Toggle Dark Mode
      </button>
    </div>
  );
}

export default App;
