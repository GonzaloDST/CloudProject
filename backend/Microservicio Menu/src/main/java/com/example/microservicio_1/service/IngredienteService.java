package com.example.microservicio_1.service;

import com.example.microservicio_1.entity.Ingrediente;
import com.example.microservicio_1.repository.IngredienteRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class IngredienteService {

    private final IngredienteRepository ingredienteRepository;

    public IngredienteService(IngredienteRepository ingredienteRepository) {
        this.ingredienteRepository = ingredienteRepository;
    }

    public List<Ingrediente> getAllIngredientes() {
        return ingredienteRepository.findAll();
    }

    public Optional<Ingrediente> getIngredienteById(Long id) {
        return ingredienteRepository.findById(id);
    }

    public Ingrediente createIngrediente(Ingrediente ingrediente) {
        return ingredienteRepository.save(ingrediente);
    }

    public Ingrediente updateIngrediente(Long id, Ingrediente ingredienteDetails) {
        return ingredienteRepository.findById(id).map(ingrediente -> {
            ingrediente.setNombre(ingredienteDetails.getNombre());
            ingrediente.setStock(ingredienteDetails.getStock());
            return ingredienteRepository.save(ingrediente);
        }).orElseThrow(() -> new RuntimeException("Ingrediente no encontrado con id: " + id));
    }

    public void deleteIngrediente(Long id) {
        ingredienteRepository.deleteById(id);
    }
}

