FROM eclipse-temurin:17-jdk-slim
WORKDIR /programas/api-menu
COPY . .
RUN ./mvnw clean package -DskipTests
EXPOSE 8080
CMD ["java", "-jar", "target/menu-service-0.0.1-SNAPSHOT.jar"]
