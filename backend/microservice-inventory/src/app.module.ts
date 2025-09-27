import { Module } from "@nestjs/common";
import { MongooseModule } from "@nestjs/mongoose";
import { AppController } from "./app.controller";
import { AppService } from "./app.service";
import { IngredienteController } from "./controllers/ingrediente.controller";
import { IngredienteService } from "./services/ingrediente.service";
import { Ingrediente, IngredienteSchema } from "./schemas/ingrediente.schema";

@Module({
  imports: [
    MongooseModule.forRoot(
      process.env.MONGODB_URI || "mongodb://localhost:27017/inventory",
    ),
    MongooseModule.forFeature([
      { name: Ingrediente.name, schema: IngredienteSchema },
    ]),
  ],
  controllers: [AppController, IngredienteController],
  providers: [AppService, IngredienteService],
})
export class AppModule {}
