package com.example.microservicio_1.controller;

import com.example.microservicio_1.entity.Ingrediente;
import com.example.microservicio_1.service.IngredienteService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/ingredientes")
public class IngredienteController {

    private final IngredienteService ingredienteService;

    public IngredienteController(IngredienteService ingredienteService) {
        this.ingredienteService = ingredienteService;
    }

    @GetMapping
    public List<Ingrediente> getAllIngredientes() {
        return ingredienteService.getAllIngredientes();
    }

    @GetMapping("/{id}")
    public Ingrediente getIngredienteById(@PathVariable Long id) {
        return ingredienteService.getIngredienteById(id)
                .orElseThrow(() -> new RuntimeException("Ingrediente no encontrado con id: " + id));
    }

    @PostMapping
    public Ingrediente createIngrediente(@RequestBody Ingrediente ingrediente) {
        return ingredienteService.createIngrediente(ingrediente);
    }

    @PutMapping("/{id}")
    public Ingrediente updateIngrediente(@PathVariable Long id, @RequestBody Ingrediente ingrediente) {
        return ingredienteService.updateIngrediente(id, ingrediente);
    }

    @DeleteMapping("/{id}")
    public void deleteIngrediente(@PathVariable Long id) {
        ingredienteService.deleteIngrediente(id);
    }
}
