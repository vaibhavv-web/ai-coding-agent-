import os

def read_file(file_path):
    try:
        with open(file_path , "r" , encoding = "utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file:{str(e)}"   


def write_file(file_path, content):
    try:
        import os

        if not os.path.exists(file_path):
            return "File does not exist"

        with open(file_path, "a", encoding="utf-8") as f:
            f.write("\n\n" + content)

        return "File updated successfully"

    except Exception as e:
        return f"Error writing file: {str(e)}"
    
def create_file(file_path, content):
    try:
        import os

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write("\n\n" + content)

        return "Code appended successfully"

    except Exception as e:
        return f"Error creating file: {str(e)}"
    
def smart_modify_file(file_path, target, new_code):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if target not in content:
            return f"❌ Target '{target}' not found"

        # 🔥 Replace function block (basic version)
        lines = content.split("\n")
        new_lines = []
        inside = False

        for line in lines:
            if target in line:
                inside = True
                new_lines.append(new_code)
                continue

            if inside:
                # stop when next function/class starts
                if line.strip().startswith("def ") or line.strip().startswith("class "):
                    inside = False
                    new_lines.append(line)
                continue
            else:
                new_lines.append(line)

        updated_content = "\n".join(new_lines)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        return "✅ Smart modify success"

    except Exception as e:
        return f"❌ Error: {str(e)}"