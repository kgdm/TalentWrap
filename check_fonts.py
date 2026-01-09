import zipfile
import re

def get_docx_fonts(path):
    try:
        with zipfile.ZipFile(path) as z:
            xml_content = z.read('word/fontTable.xml').decode('utf-8')
            # Extract font names
            fonts = re.findall(r'w:name="([^"]+)"', xml_content)
            return set(fonts)
    except Exception as e:
        return f"Error: {e}"

print("Fonts in Inputresume.docx:")
print(get_docx_fonts('sample/Inputresume.docx'))
