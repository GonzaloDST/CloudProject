import {
  IsString,
  IsNumber,
  IsOptional,
  IsBoolean,
  Min,
} from "class-validator";

export class CreateIngredienteDto {
  @IsString()
  nombre: string;

  @IsOptional()
  @IsString()
  categoria?: string;

  @IsString()
  unidad: string;

  @IsNumber()
  @Min(0)
  stockActual: number;

  @IsNumber()
  @Min(0)
  stockMinimo: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  precioUnitario?: number;

  @IsOptional()
  @IsBoolean()
  activo?: boolean;
}

export class UpdateIngredienteDto {
  @IsOptional()
  @IsString()
  nombre?: string;

  @IsOptional()
  @IsString()
  categoria?: string;

  @IsOptional()
  @IsString()
  unidad?: string;

  @IsOptional()
  @IsNumber()
  @Min(0)
  stockActual?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  stockMinimo?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  precioUnitario?: number;

  @IsOptional()
  @IsBoolean()
  activo?: boolean;
}
