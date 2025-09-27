package com.example.microservicio_1.service;

import com.example.microservicio_1.entity.Maki;
import com.example.microservicio_1.repository.MakiRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class MakiService {

    private final MakiRepository makiRepository;

    public MakiService(MakiRepository makiRepository) {
        this.makiRepository = makiRepository;
    }

    public List<Maki> getAllMakis() {
        return makiRepository.findAll();
    }

    public Optional<Maki> getMakiById(Long id) {
        return makiRepository.findById(id);
    }

    public Maki createMaki(Maki maki) {
        return makiRepository.save(maki);
    }

    public Maki updateMaki(Long id, Maki makiDetails) {
        return makiRepository.findById(id).map(maki -> {
            maki.setNombre(makiDetails.getNombre());
            maki.setDescripcion(makiDetails.getDescripcion());
            maki.setPrecio(makiDetails.getPrecio());
            maki.setIngredientes(makiDetails.getIngredientes());
            return makiRepository.save(maki);
        }).orElseThrow(() -> new RuntimeException("Maki no encontrado con id: " + id));
    }

    public void deleteMaki(Long id) {
        makiRepository.deleteById(id);
    }
}
