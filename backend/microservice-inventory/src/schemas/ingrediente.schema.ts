import { Prop, Schema, SchemaFactory } from "@nestjs/mongoose";
import { Document } from "mongoose";

export type IngredienteDocument = Ingrediente & Document;

@Schema({ timestamps: true })
export class Ingrediente {
  @Prop({ required: true, trim: true })
  nombre: string;

  @Prop({ trim: true })
  categoria?: string;

  @Prop({ required: true, trim: true })
  unidad: string;

  @Prop({ required: true, min: 0 })
  stockActual: number;

  @Prop({ required: true, min: 0 })
  stockMinimo: number;

  @Prop({ min: 0 })
  precioUnitario?: number;

  @Prop({ default: true })
  activo: boolean;
}

export const IngredienteSchema = SchemaFactory.createForClass(Ingrediente);
