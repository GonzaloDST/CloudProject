FROM openjdk:17-jdk-slim
WORKDIR /programas/api-menu
COPY . .
RUN chmod +x mvnw && ./mvnw -B -DskipTests clean package
EXPOSE 8080
CMD ["java","-jar","target/*.jar"]