package com.example.securityappliaction.repository;


import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.securityappliaction.entity.LoginActivity;

@Repository
public interface LoginActivityRepository extends JpaRepository<LoginActivity, Long> {
}
