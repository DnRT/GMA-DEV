import os
from markdown_pdf import MarkdownPdf, Section

DOSSIERS_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(DOSSIERS_DIR, "samples")
PDFS_DIR = os.path.join(DOSSIERS_DIR, "pdfs")

os.makedirs(PDFS_DIR, exist_ok=True)

# Clean, professional enterprise PDF CSS styling
ENTERPRISE_CSS = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #1e293b;
}
h1 {
    color: #0f172a;
    font-size: 16pt;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 6px;
    margin-top: 14pt;
}
h2 {
    color: #1e293b;
    font-size: 13pt;
    margin-top: 12pt;
    margin-bottom: 4pt;
}
h3 {
    color: #334155;
    font-size: 11pt;
    margin-top: 8pt;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 10pt 0;
    font-size: 9pt;
}
th, td {
    border: 1px solid #cbd5e1;
    padding: 5pt 7pt;
    text-align: left;
}
th {
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: bold;
}
tr:nth-child(even) {
    background-color: #f8fafc;
}
code {
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 1pt 3pt;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 8.5pt;
    border-radius: 2px;
}
pre {
    background-color: #0f172a;
    color: #f8fafc;
    padding: 6pt;
    border-radius: 4px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 8pt;
}
blockquote {
    border-left: 3px solid #0284c7;
    margin: 8pt 0;
    padding-left: 8pt;
    color: #475569;
    font-style: italic;
}
hr {
    border: 0;
    border-top: 1px solid #e2e8f0;
    margin: 10pt 0;
}
"""

def generate_pdfs():
    print("=== Generador de Dossiers Oficiales (PDFs) GMA-DEV ===\n")
    if not os.path.exists(SAMPLES_DIR):
        print(f"[ERROR] No se encontro el directorio: {SAMPLES_DIR}")
        return

    md_files = [f for f in os.listdir(SAMPLES_DIR) if f.endswith(".md")]
    if not md_files:
        print("[ERROR] No hay archivos Markdown en samples/")
        return

    for md_file in md_files:
        input_path = os.path.join(SAMPLES_DIR, md_file)
        pdf_filename = md_file.replace(".md", ".pdf")
        output_path = os.path.join(PDFS_DIR, pdf_filename)

        print(f"-> Procesando: {md_file}...")
        with open(input_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        styled_content = f"<style>{ENTERPRISE_CSS}</style>\n\n{md_content}"
        pdf = MarkdownPdf(toc_level=2)
        pdf.add_section(Section(styled_content, paper_size="A4"))
        pdf.save(output_path)
        print(f"   [OK] Generado: {output_path}")

    # Remove temporary test pdf if exists
    for temp in ["test_css.pdf", "test_output.pdf"]:
        p = os.path.join(PDFS_DIR, temp)
        if os.path.exists(p):
            os.remove(p)

    print("\n[EXITO] Todos los expedientes en PDF fueron compilados en 'dossiers/pdfs/'.")

if __name__ == "__main__":
    generate_pdfs()
