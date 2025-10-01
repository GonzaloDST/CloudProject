import { Injectable } from "@nestjs/common";

@Injectable()
export class AppService {
  constructor() {}

  getHello(): string {
    return "Hello World!";
  }

  getHealth(): object {
    return {
      status: "healthy",
      database: "connected",
      timestamp: new Date().toISOString(),
      service: "microservice-inventory",
    };
  }
}
