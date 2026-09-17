from scanner import ProjectScanner


project_path = "."

scanner = ProjectScanner(project_path)

files = scanner.scan_project()

print("Project:", scanner.project_path)
print("Files found:", len(files))

print("\nScanned files:")

for file in files:
    print(
        file["relative_path"],
        "-",
        file["extension"]
    )