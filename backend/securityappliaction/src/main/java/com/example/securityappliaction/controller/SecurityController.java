package com.example.securityappliaction.controller;

import com.example.securityappliaction.dto.LoginData;
import com.example.securityappliaction.entity.LoginActivity;
import com.example.securityappliaction.repository.LoginActivityRepository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/security")
public class SecurityController {

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private LoginActivityRepository loginActivityRepository;

    @PostMapping("/validate-login")
    public ResponseEntity<String> validateLogin(@RequestBody LoginData loginData) {
        // Call the external XGBoost scoring service (Flask app on port 5002)
        ResponseEntity<String> response = restTemplate.postForEntity(
            "http://localhost:5002/xgboost-score", loginData, String.class);

        LoginActivity activity = new LoginActivity();
        activity.setUsername(loginData.getUsername());
        activity.setKeystrokeSpeed(loginData.getKeystrokeSpeed());
        activity.setMouseMovement(loginData.getMouseMovement());
        activity.setGeoLocation(loginData.getGeoLocation());

        if (response.getBody().contains("HIGH")) {
            activity.setRisk("HIGH");
            activity.setScore(0.9);
            loginActivityRepository.save(activity);
            return ResponseEntity.status(401).body("Suspicious login detected!");
        } else {
            activity.setRisk("LOW");
            activity.setScore(0.3);
            loginActivityRepository.save(activity);
            return ResponseEntity.ok("Login successful.");
        }
    }
}
