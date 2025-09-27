package com.example.microservicio_1.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.util.Set;

@Entity
@Data
public class Ingrediente {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nombre;
    private Integer stock;

    @ManyToMany(mappedBy = "ingredientes")
    private Set<Maki> makis;
}
