package com.example.microservicio_1.repository;

import com.example.microservicio_1.entity.Maki;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MakiRepository extends JpaRepository<Maki, Long> {
}