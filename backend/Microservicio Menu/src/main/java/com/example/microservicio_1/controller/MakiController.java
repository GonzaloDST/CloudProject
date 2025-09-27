package com.example.microservicio_1.controller;

import com.example.microservicio_1.entity.Maki;
import com.example.microservicio_1.service.MakiService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/makis")
public class MakiController {

    private final MakiService makiService;

    public MakiController(MakiService makiService) {
        this.makiService = makiService;
    }

    @GetMapping
    public List<Maki> getAllMakis() {
        return makiService.getAllMakis();
    }

    @GetMapping("/{id}")
    public Maki getMakiById(@PathVariable Long id) {
        return makiService.getMakiById(id)
                .orElseThrow(() -> new RuntimeException("Maki no encontrado con id: " + id));
    }

    @PostMapping
    public Maki createMaki(@RequestBody Maki maki) {
        return makiService.createMaki(maki);
    }

    @PutMapping("/{id}")
    public Maki updateMaki(@PathVariable Long id, @RequestBody Maki maki) {
        return makiService.updateMaki(id, maki);
    }

    @DeleteMapping("/{id}")
    public void deleteMaki(@PathVariable Long id) {
        makiService.deleteMaki(id);
    }
}
