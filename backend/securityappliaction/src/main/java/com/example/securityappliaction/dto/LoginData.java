package com.example.securityappliaction.dto;

import lombok.Data;

@Data
public class LoginData {
    private String username;
    private double keystrokeSpeed;
    private double mouseMovement;
    private double geoLocation;
}
