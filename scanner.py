import os


class ProjectScanner:

    def __init__(self, project_path):
        self.project_path = os.path.abspath(project_path)

        self.ignore_directories = {
            "venv",
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".idea",
            ".vscode"
        }

        self.allowed_extensions = {
            ".py",
            ".js",
            ".html",
            ".css",
            ".json",
            ".yaml",
            ".yml",
            ".xml",
            ".txt",
            ".md",
            ".sql",
            ".ini",
            ".cfg",
            ".conf",
            ".env"
        }

    # ==========================================
    # VALIDATE PROJECT PATH
    # ==========================================

    def validate_path(self):

        if not os.path.exists(self.project_path):
            raise FileNotFoundError(
                f"Project path does not exist: {self.project_path}"
            )

        if not os.path.isdir(self.project_path):
            raise NotADirectoryError(
                f"Project path is not a directory: {self.project_path}"
            )

        return True

    # ==========================================
    # SCAN PROJECT FILES
    # ==========================================

    def scan_files(self):

        self.validate_path()

        files = []

        for root, directories, filenames in os.walk(
            self.project_path
        ):

            # Ignore unnecessary directories
            directories[:] = [
                directory
                for directory in directories
                if directory not in self.ignore_directories
            ]

            for filename in filenames:

                extension = os.path.splitext(
                    filename
                )[1].lower()

                if extension in self.allowed_extensions:

                    full_path = os.path.join(
                        root,
                        filename
                    )

                    relative_path = os.path.relpath(
                        full_path,
                        self.project_path
                    )

                    files.append({
                        "name": filename,
                        "path": full_path,
                        "relative_path": relative_path,
                        "extension": extension
                    })

        return files

    # ==========================================
    # READ FILE
    # ==========================================

    def read_file(self, file_path):

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                return file.read()

        except UnicodeDecodeError:

            return ""

        except PermissionError:

            return ""

        except OSError:

            return ""

    # ==========================================
    # READ FILE AS LINES
    # ==========================================

    def read_file_lines(self, file_path):

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                return file.readlines()

        except UnicodeDecodeError:

            return []

        except PermissionError:

            return []

        except OSError:

            return []

    # ==========================================
    # GET SPECIFIC LINE
    # ==========================================

    def get_line(self, file_path, line_number):

        if not line_number:
            return ""

        try:

            line_number = int(line_number)

        except (TypeError, ValueError):

            return ""

        if line_number < 1:
            return ""

        lines = self.read_file_lines(file_path)

        if line_number > len(lines):
            return ""

        return lines[line_number - 1].rstrip("\n\r")

    # ==========================================
    # FIND TEXT IN FILE
    # ==========================================

    def find_text(
        self,
        file_path,
        search_text
    ):

        if not search_text:
            return None

        lines = self.read_file_lines(file_path)

        search_text = str(search_text).lower()

        for line_number, line in enumerate(
            lines,
            start=1
        ):

            if search_text in line.lower():

                return {
                    "line_number": line_number,
                    "evidence": line.strip()
                }

        return None

    # ==========================================
    # SCAN COMPLETE PROJECT
    # ==========================================

    def scan_project(self):

        files = self.scan_files()

        scanned_files = []

        for file_info in files:

            content = self.read_file(
                file_info["path"]
            )

            file_info["content"] = content

            scanned_files.append(file_info)

        return scanned_files