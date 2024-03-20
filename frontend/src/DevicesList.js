import React, { useState, useEffect } from "react";
import axios from "axios";
import Modal from "react-modal";

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
    formData.append("script", selectedFile);
    formData.append("scriptName", selectedFile.name); // Include script name in the form data

    try {
      await axios.post(
        `/api/upload-script/${selectedDevice.mac_address}`, // Assuming there's a separate endpoint for uploading scripts
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      alert("Script uploaded successfully.");
      // Refetch devices after script upload
      fetchDevices();
      setModalIsOpen(false);
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
          alert("Device removed successfully");
          fetchDevices(); // Re-fetch the devices list
        })
        .catch((error) => console.error("Error removing device:", error));
    }
  };

  const openModal = (device) => {
    setSelectedDevice(device);
    setModalIsOpen(true);
  };

  const closeModal = () => {
    setSelectedDevice(null);
    setSelectedFile(null);
    setModalIsOpen(false);
  };

  return (
    <div>
      <h2>Devices</h2>
      <ul className="devices">
        {devices.map((device, index) => (
          <li key={index}>
            <div className="info">
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
                ⚙️
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
        <input type="file" onChange={handleFileChange} />
        {availableScripts.length === 0 ? (
          <p>No scripts available. Please upload a script.</p>
        ) : (
          availableScripts.map((script, index) => (
            <ScriptComponent
              key={index}
              scriptName={script.name} // Display script name
              onDelete={() => console.log("Delete script")}
              onRun={() => console.log("Run script")}
            />
          ))
        )}
        <button onClick={handleUpload}>Upload and Execute</button>
      </Modal>
    </div>
  );
}

export default DevicesList;
