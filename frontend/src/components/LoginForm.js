import React, { useState } from "react";
import axios from "axios";

const LoginForm = () => {
  const [username, setUsername] = useState("");
  const [keystrokeTimes, setKeystrokeTimes] = useState([]);
  const [mouseMovements, setMouseMovements] = useState([]);
  const [message, setMessage] = useState("");

  // Capture key press events to compute typing speed.
  const handleKeyPress = () => {
    setKeystrokeTimes([...keystrokeTimes, new Date().getTime()]);
  };

  // Capture mouse movements.
  const handleMouseMove = (e) => {
    setMouseMovements([...mouseMovements, { x: e.clientX, y: e.clientY }]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Simple validation: ensure username is provided.
    if (!username) {
      setMessage("Username is required.");
      return;
    }
    
    // Calculate keystroke speed: time between first and last keystroke divided by count.
    let speed = 0;
    if (keystrokeTimes.length > 1) {
      speed = (keystrokeTimes[keystrokeTimes.length - 1] - keystrokeTimes[0]) / keystrokeTimes.length;
    }
    
    // For demonstration, simulate geoLocation as a random value.
    const geoLocation = Math.random() * 100;
    
    try {
      const response = await axios.post("http://localhost:8080/security/validate-login", {
        username,
        keystrokeSpeed: speed,
        mouseMovement: mouseMovements.length,
        geoLocation: geoLocation,
      });
      setMessage(response.data);
    } catch (error) {
      if (error.response) {
        setMessage(error.response.data);
      } else {
        setMessage("Error connecting to server");
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} onMouseMove={handleMouseMove}>
      <div>
        <input
          type="text"
          placeholder="Username"
          onChange={(e) => setUsername(e.target.value)}
          onKeyPress={handleKeyPress}
          style={{ marginBottom: "1rem", padding: "0.5rem", width: "200px" }}
        />
      </div>
      <div>
        <input
          type="password"
          placeholder="Password"
          onKeyPress={handleKeyPress}
          style={{ marginBottom: "1rem", padding: "0.5rem", width: "200px" }}
        />
      </div>
      <button type="submit" style={{ padding: "0.5rem 1rem" }}>
        Login
      </button>
      {message && (
        <div style={{ marginTop: "1rem", color: "blue" }}>
          {message}
        </div>
      )}
    </form>
  );
};

export default LoginForm;
