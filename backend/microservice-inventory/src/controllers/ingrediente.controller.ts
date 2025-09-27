import {
  Controller,
  Get,
  Post,
  Body,
  Patch,
  Param,
  Delete,
  Query,
} from "@nestjs/common";
import { IngredienteService } from "../services/ingrediente.service";
import {
  CreateIngredienteDto,
  UpdateIngredienteDto,
} from "../dto/ingrediente.dto";

@Controller("ingredientes")
export class IngredienteController {
  constructor(private readonly ingredienteService: IngredienteService) {}

  @Post()
  create(@Body() createIngredienteDto: CreateIngredienteDto) {
    return this.ingredienteService.create(createIngredienteDto);
  }

  @Get()
  findAll(@Query("categoria") categoria?: string) {
    if (categoria) {
      return this.ingredienteService.findByCategoria(categoria);
    }
    return this.ingredienteService.findAll();
  }

  @Get("low-stock")
  findLowStock() {
    return this.ingredienteService.findLowStock();
  }

  @Get(":id")
  findOne(@Param("id") id: string) {
    return this.ingredienteService.findOne(id);
  }

  @Patch(":id")
  update(
    @Param("id") id: string,
    @Body() updateIngredienteDto: UpdateIngredienteDto,
  ) {
    return this.ingredienteService.update(id, updateIngredienteDto);
  }

  @Delete(":id")
  remove(@Param("id") id: string) {
    return this.ingredienteService.remove(id);
  }
}
