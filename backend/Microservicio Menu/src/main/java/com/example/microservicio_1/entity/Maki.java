package com.example.microservicio_1.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.ToString;
import java.util.Set;

@Entity
@Data
public class Maki {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nombre;
    private String descripcion;
    private Double precio;

    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
            name = "maki_ingrediente",
            joinColumns = @JoinColumn(name = "maki_id"),
            inverseJoinColumns = @JoinColumn(name = "ingrediente_id")
    )
    @JsonIgnore
    @ToString.Exclude
    @EqualsAndHashCode.Exclude
    private Set<Ingrediente> ingredientes;
}
