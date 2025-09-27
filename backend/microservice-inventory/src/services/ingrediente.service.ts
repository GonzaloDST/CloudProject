import { Injectable, NotFoundException } from "@nestjs/common";
import { InjectModel } from "@nestjs/mongoose";
import { Model } from "mongoose";
import {
  Ingrediente,
  IngredienteDocument,
} from "../schemas/ingrediente.schema";
import {
  CreateIngredienteDto,
  UpdateIngredienteDto,
} from "../dto/ingrediente.dto";

@Injectable()
export class IngredienteService {
  constructor(
    @InjectModel(Ingrediente.name)
    private ingredienteModel: Model<IngredienteDocument>,
  ) {}

  async create(
    createIngredienteDto: CreateIngredienteDto,
  ): Promise<Ingrediente> {
    const ingrediente = new this.ingredienteModel(createIngredienteDto);
    return ingrediente.save();
  }

  async findAll(): Promise<Ingrediente[]> {
    return this.ingredienteModel.find().exec();
  }

  async findOne(id: string): Promise<Ingrediente> {
    const ingrediente = await this.ingredienteModel.findById(id).exec();
    if (!ingrediente) {
      throw new NotFoundException(`Ingrediente con ID ${id} no encontrado`);
    }
    return ingrediente;
  }

  async update(
    id: string,
    updateIngredienteDto: UpdateIngredienteDto,
  ): Promise<Ingrediente> {
    const ingrediente = await this.ingredienteModel
      .findByIdAndUpdate(id, updateIngredienteDto, { new: true })
      .exec();

    if (!ingrediente) {
      throw new NotFoundException(`Ingrediente con ID ${id} no encontrado`);
    }
    return ingrediente;
  }

  async remove(id: string): Promise<void> {
    const result = await this.ingredienteModel.findByIdAndDelete(id).exec();
    if (!result) {
      throw new NotFoundException(`Ingrediente con ID ${id} no encontrado`);
    }
  }

  async findByCategoria(categoria: string): Promise<Ingrediente[]> {
    return this.ingredienteModel.find({ categoria }).exec();
  }

  async findLowStock(): Promise<Ingrediente[]> {
    return this.ingredienteModel
      .find({
        $expr: { $lte: ["$stockActual", "$stockMinimo"] },
      })
      .exec();
  }
}
