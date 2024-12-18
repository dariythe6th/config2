import os
import argparse
import xml.etree.ElementTree as ET

class MavenDependencyGraph:
    def __init__(self, root_pom_path, max_depth):
        self.root_pom_path = root_pom_path
        self.max_depth = max_depth
        self.graph = {}

    def parse_pom(self, file_path):
        """Парсинг файла pom.xml для извлечения зависимостей."""
        ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            dependencies = []
            for dep in root.findall(".//mvn:dependency", ns):
                group_id = dep.find("mvn:groupId", ns).text
                artifact_id = dep.find("mvn:artifactId", ns).text
                dependencies.append(f"{group_id}:{artifact_id}")
            return dependencies
        except ET.ParseError:
            print(f"Ошибка парсинга файла: {file_path}")
            return []

    def build_graph(self, pom_path, current_depth):
        """Построение графа зависимостей."""
        if current_depth > self.max_depth or pom_path in self.graph:
            return
        dependencies = self.parse_pom(pom_path)
        self.graph[pom_path] = dependencies

        for dep in dependencies:
            dep_pom = self.find_pom_for_dependency(dep)
            if dep_pom:
                self.build_graph(dep_pom, current_depth + 1)

    def find_pom_for_dependency(self, dependency):
        """Имитация поиска pom.xml для указанной зависимости."""
        # Здесь можно добавить логику для поиска pom.xml в локальном репозитории.
        # Пока что возвращаем None, чтобы использовать только корневой pom.xml.
        return None

    def to_plantuml(self):
        """Генерация PlantUML графа зависимостей."""
        lines = ["@startuml"]
        for parent, dependencies in self.graph.items():
            parent_name = os.path.basename(parent)
            for dep in dependencies:
                lines.append(f'"{parent_name}" --> "{dep}"')
        lines.append("@enduml")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Визуализация графа зависимостей Maven.")
    parser.add_argument("--path", required=True, help="Путь к корневому pom.xml.")
    parser.add_argument("--output", required=True, help="Путь к файлу-результату PlantUML.")
    parser.add_argument("--depth", type=int, default=3, help="Максимальная глубина анализа зависимостей.")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Файл {args.path} не найден.")
        return

    graph = MavenDependencyGraph(root_pom_path=args.path, max_depth=args.depth)
    graph.build_graph(graph.root_pom_path, 0)
    plantuml_code = graph.to_plantuml()

    # Запись результата в файл
    with open(args.output, "w", encoding="utf-8") as output_file:
        output_file.write(plantuml_code)

    print(f"Граф зависимостей сохранён в файл: {args.output}")


if __name__ == "__main__":
    main()
