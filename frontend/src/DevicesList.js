import React, { useState, useEffect } from "react";
import axios from "axios";
import Modal from "react-modal";
Modal.setAppElement("#root");
function ScriptComponent({ scriptName, onDelete, onRun }) {
  return (
    <div className="scriptContent">
      <p>{scriptName}</p>
      <button onClick={onRun}>Run</button>
      <button onClick={onDelete}>Delete</button>
    </div>
  );
}

function DevicesList({ devices, fetchDevices }) {
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [availableScripts, setAvailableScripts] = useState([]);
  // Additional state to track online status of devices
  const [onlineStatus, setOnlineStatus] = useState({});

  useEffect(() => {
    // Function to check if the device is online based on last ping time
    const isDeviceOnline = (lastPingTime) => {
      const currentTime = new Date().getTime();
      // Convert lastPingTime (python time) from seconds to milliseconds
      const lastPingTimeMs = lastPingTime * 1000;
      console.log(currentTime, lastPingTimeMs);
      return currentTime - lastPingTimeMs < 20000;
    };git

    // Update online status based on last ping time of each device
    const updatedOnlineStatus = {};
    devices.forEach((device) => {
      updatedOnlineStatus[device.mac_address] = isDeviceOnline(
        device.last_ping_time
      );
    });
    setOnlineStatus(updatedOnlineStatus);
  }, [devices]);

  useEffect(() => {
    if (selectedDevice) {
      setAvailableScripts(selectedDevice.scripts);
    }
  }, [selectedDevice]);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile || !selectedDevice) {
      alert("Please select a file and a device.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile); // Ensure backend handles "file" key

    try {
      await axios.post(`/api/scripts/${selectedDevice.mac_address}`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      // Refetch device scripts to update the modal content
      await fetchDeviceScripts(selectedDevice.mac_address);
    } catch (error) {
      console.error("Error uploading script:", error);
      alert("Failed to upload the script.");
    }
  };

  const removeDevice = (deviceId) => {
    if (window.confirm("Are you sure you want to remove this device?")) {
      axios
        .delete(`/api/devices/${deviceId}`)
        .then(() => {
          fetchDevices(); // Re-fetch the devices list
        })
        .catch((error) => console.error("Error removing device:", error));
    }
  };

  const openModal = async (device) => {
    setSelectedDevice(device);
    setModalIsOpen(true);
    await fetchDeviceScripts(device.mac_address);
  };

  const closeModal = () => {
    setSelectedDevice(null);
    setSelectedFile(null);
    setModalIsOpen(false);
  };

  const fetchDeviceScripts = async (mac_address) => {
    try {
      const response = await axios.get(`/api/fetch-scripts/${mac_address}`);
      setAvailableScripts(response.data);
    } catch (error) {
      console.error("Error fetching scripts:", error);
    }
  };

  const runScript = async (scriptName) => {
    try {
      await axios.post(`/api/enqueue-script/${selectedDevice.mac_address}`, {
        name: scriptName,
      });
      alert(`Script ${scriptName} enqueued for execution.`);
    } catch (error) {
      console.error("Error enqueuing script:", error);
      alert(`Failed to enqueue the script ${scriptName}.`);
    }
  };

  const deleteScript = async (scriptName) => {
    try {
      await axios.delete(
        `/api/scripts/${selectedDevice.mac_address}/${scriptName}`
      );
      alert(`Script ${scriptName} deleted successfully.`);
      await fetchDeviceScripts(selectedDevice.mac_address); // Refresh scripts for the current device
    } catch (error) {
      console.error("Error deleting script:", error);
      alert(`Failed to delete the script ${scriptName}.`);
    }
  };

  // Periodically fetch device data to update online status
  useEffect(() => {
    const interval = setInterval(async () => {
      await fetchDevices();
    }, 10000); // Fetch data every 10 seconds

    return () => clearInterval(interval);
  }, [fetchDevices]);

  if (devices.length === 0) {
    return (
      <div>
        <h2>Devices</h2>
        <p className="no-device-text">no devices added</p>
      </div>
    );
  }
  return (
    <div>
      <h2>Devices</h2>
      <ul className="devices">
        {devices.map((device, index) => (
          <li key={index}>
            <div className="info">
              <span
                className={`status-indicator ${
                  onlineStatus[device.mac_address] ? "online" : "offline"
                }`}
              ></span>
              <div>
                <span>{device.emoji}</span>
              </div>
              <div>
                <span className="name">{device.name}</span>
              </div>
              <div>@ {device.mac_address}</div>
            </div>
            <div>
              <button
                onClick={() => openModal(device)}
                className="code-icon-button"
              >
                &lt;/&gt;
              </button>
              <button
                onClick={() => removeDevice(device.mac_address)}
                className="remove-button"
              >
                Remove
              </button>
            </div>
          </li>
        ))}
      </ul>
      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        contentLabel="Script Upload Modal"
        className="modal-content"
        overlayClassName="modal-overlay"
      >
        <h2>Upload and Run Script on Device</h2>
        <p>Device: {selectedDevice && selectedDevice.name}</p>
        <input type="file" name="script" onChange={handleFileChange} />
        {Object.keys(availableScripts).length === 0 ? (
          <p>No scripts available. Please upload a script.</p>
        ) : (
          Object.keys(availableScripts).map((scriptName, index) => (
            <ScriptComponent
              key={index}
              scriptName={scriptName}
              onDelete={() => deleteScript(scriptName)}
              onRun={() => runScript(scriptName)}
            />
          ))
        )}
        <button onClick={handleUpload}>Upload</button>
      </Modal>
    </div>
  );
}

export default DevicesList;
