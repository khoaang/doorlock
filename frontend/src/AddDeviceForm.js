import React, { useState } from "react";
import axios from "axios";

function AddDeviceForm({ fetchDevices }) {
  const [macAddress, setMacAddress] = useState("");
  const [name, setName] = useState("");
  const [selectedEmoji, setSelectedEmoji] = useState("📱"); // Default emoji

  // Predefined set of emojis to choose from
  const emojiOptions = [
    "📱",
    "💻",
    "🖥",
    "🔌",
    "🖨",
    "🎮",
    "🔋",
    "💡",
    "🔦",
    "📡",
    "🕹️",
    "🌡️",
    "⌚",
    "🔒",
    "🔑",
    "🚪",
    "🏠",
    "🌐",
    "🔧",
    "🛠️",
    "⚙️",
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    axios
      .post("/api/devices", {
        mac_address: macAddress,
        name: name,
        emoji: selectedEmoji,
      })
      .then((response) => {
        if (response.data.success) {
          alert("Device added successfully");
          setMacAddress("");
          setName("");
          setSelectedEmoji("📱"); // Reset to default emoji after submission
          fetchDevices(); // Fetch the updated devices list
        } else {
          alert(response.data.error);
        }
      })
      .catch((error) =>
        console.error("There was an error adding the device:", error)
      );
  };

  return (
    <form className="device-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <select
          className="emoji-field"
          value={selectedEmoji}
          onChange={(e) => setSelectedEmoji(e.target.value)}
        >
          <option value="📱">📱</option>
          {emojiOptions.map((emoji, index) => (
            <option key={index} value={emoji}>
              {emoji}
            </option>
          ))}
        </select>
        <input
          className="input-field"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter Name"
        />
        <input
          className="input-field"
          type="text"
          value={macAddress}
          onChange={(e) => setMacAddress(e.target.value)}
          placeholder="Enter MAC Address"
          required
        />
        <button className="submit-button" type="submit">
          +
        </button>
      </div>
    </form>
  );
}

export default AddDeviceForm;
