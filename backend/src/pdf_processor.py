"""
Procesador de archivos PDF para extracción de texto
"""
from pypdf import PdfReader
from io import BytesIO
import re


class PDFProcessor:
    """Clase para procesar y extraer texto de archivos PDF"""
    
    def extract_text(self, pdf_content: bytes) -> str:
        """Extraer y limpiar texto de un archivo PDF"""
        try:
            # Crear lector de PDF desde bytes
            pdf_file = BytesIO(pdf_content)
            reader = PdfReader(pdf_file)
            
            # Extraer texto de todas las páginas
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n\n"
            
            # Limpiar y normalizar el texto
            cleaned_text = self.clean_text(full_text)
            
            return cleaned_text
            
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Limpiar y normalizar texto extraído"""
        
        # Eliminar múltiples saltos de línea
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Eliminar espacios múltiples
        text = re.sub(r' {2,}', ' ', text)
        
        # Eliminar caracteres de control extraños
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text)
        
        # Normalizar espacios alrededor de puntuación
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        
        return text.strip()
    
    def segment_content(self, text: str, max_chars: int = 5000) -> list[str]:
        """Segmentar contenido largo en fragmentos manejables"""
        
        # Dividir por párrafos
        paragraphs = text.split('\n\n')
        
        segments = []
        current_segment = ""
        
        for paragraph in paragraphs:
            # Si agregar este párrafo excede el límite, guardar segmento actual
            if len(current_segment) + len(paragraph) > max_chars and current_segment:
                segments.append(current_segment.strip())
                current_segment = paragraph
            else:
                current_segment += paragraph + "\n\n"
        
        # Agregar último segmento
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments
