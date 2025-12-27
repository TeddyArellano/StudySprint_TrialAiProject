"""
Servicio de integración con OpenAI API para generación de contenido
"""
import os
from typing import List, Dict, Any
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from src.models import QuizQuestion


class LLMService:
    """Servicio para interactuar con la API de OpenAI"""
    
    def __init__(self):
        """Inicializar el cliente de OpenAI"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate_session_content(
        self,
        topic_name: str,
        topic_description: str,
        duration: int,
        reference_material: str = None
    ) -> Dict[str, Any]:
        """Generar contenido estructurado para una sesión de estudio
        
        IMPORTANTE: Esta función tiene retry automático en caso de errores de API.
        Solo reintenta si hay excepciones, NO duplica llamadas exitosas.
        """
        
        print(f"\n🚀 Iniciando generación de contenido para: {topic_name}")
        print(f"⏱️  Duración solicitada: {duration} minutos")
        
        # Calcular palabras aproximadas según duración
        words_per_minute = 200
        target_words = words_per_minute * duration
        
        # Construir prompt
        prompt = self.build_content_prompt(
            topic_name, 
            topic_description,
            target_words,
            reference_material
        )
        
        # Calcular max_tokens según duración
        # Regla: ~1.3 tokens por palabra en español + 20% buffer
        max_tokens_needed = int(target_words * 1.3 * 1.2)
        # Limitar a 16,000 tokens (máximo de gpt-4o-mini output)
        max_tokens_to_use = min(max_tokens_needed, 16000)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """Eres un asistente educativo experto en crear contenido de aprendizaje conciso y efectivo.

Para CONTENIDO MATEMÁTICO Y TÉCNICO:
- USA LaTeX libremente para fórmulas, ecuaciones y notación matemática
- Usa delimitadores: $...$ para inline, $$...$$ para display
- Ejemplos: $f(x) = x^2 + 2x + 1$, $\\sum_{i=1}^{n} i$, $\\forall x \\in \\mathbb{R}$
- Para símbolos de conjuntos: $\\subseteq$, $\\in$, $\\cup$, $\\cap$
- Para lógica: $\\forall$, $\\exists$, $\\rightarrow$

Para TEXTO NARRATIVO:
- Usa español claro y directo
- Explica conceptos con ejemplos prácticos
- Mantén estructura clara con párrafos bien definidos

REQUISITO FUNDAMENTAL:
- SIEMPRE genera el número EXACTO de palabras solicitado
- Verifica el conteo antes de finalizar tu respuesta"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=max_tokens_to_use
        )
        
        content_text = response.choices[0].message.content
        
        # Detectar si hay LaTeX en la respuesta
        import re
        has_latex = bool(re.search(r'[\$\\]', content_text))
        
        print(f"\n{'='*70}")
        print(f"🤖 LLM RESPONSE - Content Generation")
        print(f"{'='*70}")
        print(f"Model: {self.model}")
        print(f"Target words: {target_words}")
        print(f"Max tokens used: {max_tokens_to_use}")
        print(f"Raw response length: {len(content_text)} chars")
        if has_latex:
            print(f"🧮 LaTeX detected - will clean after preview")
        print(f"\nFirst 300 chars of raw response:")
        print(f"{content_text[:300]}...\n")
        
        # Limpiar cualquier LaTeX que se haya escapado
        content_text = self.clean_latex_formatting(content_text)
        
        if has_latex:
            print(f"✅ LaTeX cleaned successfully\n")
        
        # Limpiar meta-información del LLM (conteos, verificaciones)
        content_text = self.clean_llm_metadata(content_text)
        
        # Parsear la respuesta estructurada
        parsed_content = self.parse_session_content(content_text, target_words)
        
        return parsed_content
    
    def build_content_prompt(
        self,
        topic_name: str,
        topic_description: str,
        target_words: int,
        reference_material: str = None
    ) -> str:
        """Construir el prompt para generar contenido"""
        
        # Determinar el nivel de detalle basado en la duración
        duration_minutes = target_words // 200  # Aproximado
        
        if duration_minutes <= 5:
            depth_instruction = f"""IMPORTANTE: Esta es una sesión RÁPIDA de 5 minutos.
- Explicación BREVE y CONCISA, sin entrar en demasiados detalles
- Enfócate solo en los conceptos MÁS IMPORTANTES
- Usa lenguaje simple y directo
- REQUISITO OBLIGATORIO: Genera EXACTAMENTE {target_words} palabras (mínimo {int(target_words * 0.9)}, máximo {int(target_words * 1.1)})"""
        elif duration_minutes <= 10:
            depth_instruction = f"""IMPORTANTE: Esta es una sesión MEDIA de 10 minutos.
- Explicación MODERADA con los conceptos principales
- Balance entre claridad y profundidad
- REQUISITO OBLIGATORIO: Genera EXACTAMENTE {target_words} palabras (mínimo {int(target_words * 0.9)}, máximo {int(target_words * 1.1)})"""
        elif duration_minutes <= 15:
            depth_instruction = f"""IMPORTANTE: Esta es una sesión PROFUNDA de 15 minutos.
- Explicación DETALLADA con ejemplos
- Cubre los conceptos con mayor profundidad
- Incluye contexto y aplicaciones prácticas
- REQUISITO OBLIGATORIO: Genera EXACTAMENTE {target_words} palabras (mínimo {int(target_words * 0.9)}, máximo {int(target_words * 1.1)})"""
        else:
            depth_instruction = f"""IMPORTANTE: Esta es una sesión EXTENSIVA de 30 minutos.
- Explicación MUY DETALLADA y exhaustiva
- Cubre el tema en profundidad con múltiples ejemplos
- Incluye contexto histórico, casos de uso, y aplicaciones avanzadas
- REQUISITO OBLIGATORIO: Genera EXACTAMENTE {target_words} palabras (mínimo {int(target_words * 0.9)}, máximo {int(target_words * 1.1)})"""
        
        base_prompt = f"""Genera contenido de estudio para el siguiente tema:

Tema: {topic_name}
{f'Descripcion: {topic_description}' if topic_description else ''}

{depth_instruction}

ESTRUCTURA REQUERIDA:
- Divide el CONTENIDO en 3-5 subtítulos relevantes (usa ## para subtítulos)
- Cada subsección debe tener 2-3 párrafos bien estructurados
- Usa saltos de línea dobles entre párrafos
- Para matemáticas/fórmulas: usa LaTeX libremente ($...$)
- Ejemplos y casos prácticos son bienvenidos

El contenido debe seguir esta estructura:

1. OBJETIVO DE APRENDIZAJE (una oración clara)
2. CONTENIDO PRINCIPAL (con subtítulos y párrafos bien separados)
3. CONCEPTOS CLAVE (lista de 3-5 conceptos principales al FINAL)

"""
        
        if reference_material:
            # Limitar el material de referencia para no exceder límites de tokens
            material_excerpt = reference_material[:3000]
            base_prompt += f"""
Utiliza el siguiente material de referencia como base:

{material_excerpt}

Adapta el contenido del material para que sea conciso y apropiado para la duracion especificada.
"""
        else:
            base_prompt += "Genera contenido educativo preciso y bien estructurado basado en tu conocimiento.\n"
        
        base_prompt += f"""
Formato de respuesta:

OBJETIVO:
[objetivo de aprendizaje]

CONTENIDO:
[contenido principal que cumpla con {target_words} palabras]

CONCEPTOS CLAVE:
- [concepto 1]
- [concepto 2]
- [concepto 3]

NOTA: NO incluyas meta-información sobre el conteo de palabras en tu respuesta.
"""
        
        return base_prompt
    
    def clean_latex_formatting(self, text: str) -> str:
        """Limpiar notación LaTeX y convertirla a formato legible
        
        Convierte expresiones LaTeX comunes a formato Unicode o texto plano.
        El LLM puede generar LaTeX libremente, este método lo limpia para visualización.
        """
        import re
        
        # PASO 1: Remover delimitadores de math mode PRIMERO
        text = re.sub(r'\$\$(.+?)\$\$', r'\1', text, flags=re.DOTALL)  # Display math
        text = re.sub(r'\$([^\$]+?)\$', r'\1', text)  # Inline math
        text = re.sub(r'\\\\\[(.+?)\\\\\]', r'\1', text, flags=re.DOTALL)  # \\[...\\]
        text = re.sub(r'\\\\\((.+?)\\\\\)', r'\1', text, flags=re.DOTALL)  # \\(...\\)
        
        # PASO 2: Convertir comandos especiales (antes de símbolos)
        text = re.sub(r'\\text(?:bf|it|rm)?\{([^}]+)\}', r'\1', text)  # \\text{...}
        text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1/\2)', text)  # Fracciones
        text = re.sub(r'\\sqrt\{([^}]+)\}', r'√(\1)', text)  # Raíz cuadrada
        
        # PASO 3: Subscripts y superscripts
        text = re.sub(r'_\{([^}]+)\}', r'_(\1)', text)
        text = re.sub(r'\^\{([^}]+)\}', r'^(\1)', text)
        
        # PASO 4: Convertir símbolos LaTeX a Unicode
        latex_to_unicode = {
            # Operadores de conjuntos
            r'\\in\b': '∈',
            r'\\notin\b': '∉',
            r'\\subset\b': '⊂',
            r'\\subseteq\b': '⊆',
            r'\\supset\b': '⊃',
            r'\\supseteq\b': '⊇',
            r'\\cup\b': '∪',
            r'\\cap\b': '∩',
            r'\\emptyset\b': '∅',
            r'\\varnothing\b': '∅',
            
            # Cuantificadores y lógica
            r'\\forall\b': '∀',
            r'\\exists\b': '∃',
            r'\\nexists\b': '∄',
            r'\\neg\b': '¬',
            r'\\land\b': '∧',
            r'\\lor\b': '∨',
            r'\\implies\b': '⇒',
            r'\\iff\b': '⇔',
            
            # Flechas
            r'\\rightarrow\b': '→',
            r'\\leftarrow\b': '←',
            r'\\Rightarrow\b': '⇒',
            r'\\Leftarrow\b': '⇐',
            r'\\leftrightarrow\b': '↔',
            r'\\Leftrightarrow\b': '⇔',
            r'\\to\b': '→',
            r'\\mapsto\b': '↦',
            
            # Comparadores
            r'\\leq\b': '≤',
            r'\\geq\b': '≥',
            r'\\neq\b': '≠',
            r'\\approx\b': '≈',
            r'\\equiv\b': '≡',
            r'\\sim\b': '∼',
            r'\\cong\b': '≅',
            r'\\propto\b': '∝',
            
            # Matemáticas básicas
            r'\\infty\b': '∞',
            r'\\times\b': '×',
            r'\\cdot\b': '·',
            r'\\div\b': '÷',
            r'\\pm\b': '±',
            r'\\mp\b': '∓',
            
            # Operadores grandes
            r'\\sum\b': '∑',
            r'\\prod\b': '∏',
            r'\\int\b': '∫',
            r'\\oint\b': '∮',
            r'\\bigcup\b': '⋃',
            r'\\bigcap\b': '⋂',
            
            # Cálculo y análisis
            r'\\partial\b': '∂',
            r'\\nabla\b': '∇',
            r'\\Delta\b': 'Δ',
            r'\\delta\b': 'δ',
            
            # Funciones comunes
            r'\\log\b': 'log',
            r'\\ln\b': 'ln',
            r'\\sin\b': 'sin',
            r'\\cos\b': 'cos',
            r'\\tan\b': 'tan',
            r'\\exp\b': 'exp',
            r'\\min\b': 'min',
            r'\\max\b': 'max',
            r'\\lim\b': 'lim',
            
            # Conjuntos especiales
            r'\\mathbb\{N\}': 'ℕ',
            r'\\mathbb\{Z\}': 'ℤ',
            r'\\mathbb\{Q\}': 'ℚ',
            r'\\mathbb\{R\}': 'ℝ',
            r'\\mathbb\{C\}': 'ℂ',
        }
        
        # Aplicar conversiones
        for latex, unicode_char in latex_to_unicode.items():
            text = re.sub(latex, unicode_char, text)
        
        # PASO 5: Limpiar comandos restantes sin backslash
        text = re.sub(r'\\([a-zA-Z]+)\b', r'\1', text)
        
        # PASO 6: Convertir corchetes [ ] en paréntesis
        text = re.sub(r'\[\s*([^\[\]]+?)\s*\]', r'(\1)', text)
        
        # PASO 7: Limpiar espacios múltiples EN LA MISMA LÍNEA (NO saltos de línea)
        # CRÍTICO: NO destruir los \n\n que separan párrafos
        lines = text.split('\n')
        cleaned_lines = [re.sub(r'[ \t]{2,}', ' ', line) for line in lines]
        text = '\n'.join(cleaned_lines)
        
        return text
    
    def clean_llm_metadata(self, text: str) -> str:
        """Limpiar meta-información que el LLM pueda haber incluido
        
        Remueve líneas de verificación, conteos de palabras, y otras
        instrucciones que el LLM pueda haber incluido por error.
        """
        import re
        
        # Patrones de meta-información a remover
        metadata_patterns = [
            r'VERIFICACIÓN FINAL:.*',
            r'La respuesta contiene exactamente \d+ palabras\.?',
            r'Verificación:.*\d+\s+palabras.*',
            r'Conteo de palabras:.*\d+.*',
            r'Total de palabras:.*\d+.*',
            r'Número de palabras:.*\d+.*',
            r'\[.*\d+\s+palabras.*\]',
            r'NOTA:.*conteo.*palabras.*',
        ]
        
        # Remover líneas que coincidan con los patrones
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Verificar si la línea contiene meta-información
            is_metadata = False
            for pattern in metadata_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_metadata = True
                    break
            
            # Solo agregar líneas que NO sean meta-información
            if not is_metadata:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def parse_session_content(self, content_text: str, target_words: int = 0) -> Dict[str, Any]:
        """Parsear la respuesta del LLM en estructura de datos"""
        
        sections = {
            'learning_objective': '',
            'content': '',
            'key_concepts': []
        }
        
        # Normalizar el texto
        text = content_text.strip()
        
        # Estrategia mejorada: Buscar secciones con regex más específicos
        import re
        
        # Buscar OBJETIVO - hasta encontrar la palabra CONTENIDO al inicio de línea
        obj_match = re.search(r'OBJETIVO[:\s]*\n*(.+?)(?=\n\s*CONTENIDO[:\s])', text, re.DOTALL | re.IGNORECASE)
        if obj_match:
            sections['learning_objective'] = obj_match.group(1).strip()
        else:
            # Fallback: buscar hasta cualquier header
            obj_match = re.search(r'OBJETIVO[:\s]*(.+?)(?=CONTENIDO|CONCEPTOS|$)', text, re.DOTALL | re.IGNORECASE)
            if obj_match:
                sections['learning_objective'] = obj_match.group(1).strip()
        
        # Buscar CONTENIDO - estrategia mejorada para NO cortar texto
        # IMPORTANTE: NO incluir la sección de CONCEPTOS CLAVE dentro del contenido
        content_match = re.search(
            r'CONTENIDO[:\s]*\n+(.+?)(?=\n+\s*CONCEPTOS?\s*CLAVES?[:\s]|\Z)', 
            text, 
            re.DOTALL | re.IGNORECASE
        )
        
        if content_match:
            sections['content'] = content_match.group(1).strip()
        else:
            # Fallback: buscar desde CONTENIDO hasta el final
            content_match = re.search(r'CONTENIDO[:\s]*\n+(.+)', text, re.DOTALL | re.IGNORECASE)
            if content_match:
                content = content_match.group(1).strip()
                # Remover sección de CONCEPTOS si está incluida
                content = re.split(
                    r'\n+\s*CONCEPTOS?\s*CLAVES?[:\s]', 
                    content, 
                    maxsplit=1, 
                    flags=re.IGNORECASE
                )[0].strip()
                sections['content'] = content
        
        # Buscar CONCEPTOS CLAVE - desde el header hasta el final o VERIFICACIÓN
        concepts_match = re.search(r'CONCEPTOS\s*CLAVES?[:\s]*\n*(.+?)(?=\n\s*VERIFICACIÓN|\Z)', text, re.DOTALL | re.IGNORECASE)
        if concepts_match:
            concepts_text = concepts_match.group(1).strip()
            # Extraer cada concepto (líneas que empiezan con -, •, *, números, etc)
            for line in concepts_text.split('\n'):
                line = line.strip()
                # Ignorar líneas vacías o que son instrucciones
                if not line or 'verificación' in line.lower():
                    continue
                if line and (line.startswith(('-', '•', '*', '–', '◦')) or (line and line[0].isdigit() and ')' in line[:3])):
                    concept = re.sub(r'^[-•*–◦\d).\s]+', '', line).strip()
                    if concept and len(concept) > 3:  # Evitar conceptos muy cortos
                        sections['key_concepts'].append(concept)
        
        # Contar palabras en el contenido extraído
        word_count = len(sections['content'].split())
        
        # Calcular qué porcentaje del objetivo se alcanzó
        if target_words > 0:
            percentage = (word_count / target_words) * 100
            status_emoji = "✅" if percentage >= 90 else "⚠️" if percentage >= 70 else "❌"
        else:
            percentage = 0
            status_emoji = "➖"
        
        print(f"\n{'='*70}")
        print(f"📋 PARSING RESULTS")
        print(f"{'='*70}")
        print(f"Raw LLM output: {len(text)} chars")
        print(f"")
        print(f"✏️  Objective: {len(sections['learning_objective'])} chars")
        print(f"   Preview: {sections['learning_objective'][:80]}...")
        print(f"")
        print(f"📝 Content: {len(sections['content'])} chars / {word_count} words")
        if target_words > 0:
            print(f"   Target: {target_words} words")
            print(f"   Achievement: {percentage:.1f}% {status_emoji}")
        print(f"   Preview: {sections['content'][:150]}...")
        print(f"")
        print(f"🔑 Key Concepts: {len(sections['key_concepts'])} items")
        for i, concept in enumerate(sections['key_concepts'][:3], 1):
            print(f"   {i}. {concept[:60]}..." if len(concept) > 60 else f"   {i}. {concept}")
        print(f"{'='*70}\n")
        
        return sections
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_quiz(
        self,
        topic_name: str,
        content: str,
        num_questions: int = 3
    ) -> List[QuizQuestion]:
        """Generar preguntas de quiz basadas en el contenido"""
        
        prompt = f"""Genera {num_questions} preguntas de opcion multiple basadas EXCLUSIVAMENTE en el siguiente contenido educativo sobre {topic_name}.

IMPORTANTE: Las preguntas deben estar basadas SOLAMENTE en la informacion presentada en el contenido a continuacion. NO uses conocimiento externo que no este en el texto.

CONTENIDO:
{content}

REQUISITOS:
- Cada pregunta debe tener 4 opciones de respuesta
- Solo una opcion es correcta
- Las preguntas deben evaluar comprension del contenido presentado
- Las opciones incorrectas deben ser plausibles pero claramente incorrectas
- Todas las respuestas deben poder encontrarse en el CONTENIDO de arriba

FORMATO DE RESPUESTA:

PREGUNTA 1:
[texto de la pregunta]
A) [opcion 1]
B) [opcion 2]
C) [opcion 3]
D) [opcion 4]
CORRECTA: [A/B/C/D]

PREGUNTA 2:
[texto de la pregunta]
A) [opcion 1]
B) [opcion 2]
C) [opcion 3]
D) [opcion 4]
CORRECTA: [A/B/C/D]
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto en crear evaluaciones educativas efectivas."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=1500
        )
        
        quiz_text = response.choices[0].message.content
        
        # Parsear las preguntas
        return self.parse_quiz_questions(quiz_text)
    
    def parse_quiz_questions(self, quiz_text: str) -> List[QuizQuestion]:
        """Parsear las preguntas del quiz desde el texto del LLM"""
        
        questions = []
        lines = quiz_text.strip().split('\n')
        
        current_question = None
        current_options = []
        correct_answer = 0
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('PREGUNTA'):
                # Guardar pregunta anterior si existe
                if current_question and current_options:
                    questions.append(QuizQuestion(
                        question=current_question,
                        options=current_options,
                        correct_answer=correct_answer
                    ))
                current_question = None
                current_options = []
                correct_answer = 0
            elif current_question is None and line and not line.startswith(('A)', 'B)', 'C)', 'D)', 'CORRECTA:')):
                current_question = line
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                option_text = line[2:].strip()
                current_options.append(option_text)
            elif line.startswith('CORRECTA:'):
                answer_letter = line.replace('CORRECTA:', '').strip().upper()
                correct_answer = ord(answer_letter) - ord('A')
        
        # Guardar última pregunta
        if current_question and current_options:
            questions.append(QuizQuestion(
                question=current_question,
                options=current_options,
                correct_answer=correct_answer
            ))
        
        return questions
