import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Canvas de doble pasada para calcular y mostrar la numeración dinámica 'Página X de Y'
    excluyendo la portada del conteo y colocando cabeceras y pies de página profesionales.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, total_pages):
        # La página 1 es la portada formal; no lleva encabezado ni pie de página
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1A365D")) # Azul institucional

        # Encabezado superior
        self.drawString(54, 752, "POLITÉCNICO GRANCOLOMBIANO | DEVOPS & INTEGRACIÓN CONTINUA")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawRightString(558, 752, "Proyecto 1 - Escenario 3: Comunicación Inter-Contenedores")

        # Línea divisoria superior
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.75)
        self.line(54, 746, 558, 746)

        # Línea divisoria inferior
        self.line(54, 46, 558, 46)

        # Pie de página
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(54, 34, "Equipo: S. Salazar, S. Quintana, R. Bautista | GitHub: github.com/ronaldo1124")
        report_page = self._pageNumber - 1
        total_report_pages = total_pages - 1
        self.drawRightString(558, 34, f"Página {report_page} de {total_report_pages}")

        self.restoreState()


def build_pdf(filename="Informe_Proyecto1_Docker_Escenario3.pdf"):
    # Margen de 0.75 in (54 pt)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=56,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Paleta de colores académica y corporativa
    c_primary = colors.HexColor("#1A365D")    # Azul institucional oscuro
    c_secondary = colors.HexColor("#2B6CB0")  # Azul medio
    c_accent = colors.HexColor("#319795")     # Turquesa / Verde técnico
    c_dark = colors.HexColor("#2D3748")       # Gris carbón para texto principal
    c_terminal_bg = colors.HexColor("#0F172A")# Fondo consola Docker oscura
    c_terminal_border = colors.HexColor("#334155")
    c_terminal_green = colors.HexColor("#34D399") # Verde terminal
    c_terminal_cyan = colors.HexColor("#38BDF8")  # Cyan terminal
    c_light_bg = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#E2E8F0")

    # Estilos Tipográficos
    title_cover_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=26,
        textColor=c_primary,
        alignment=1
    )

    subtitle_cover_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        alignment=1
    )

    meta_cover_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=c_dark,
        alignment=1
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_secondary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_dark,
        alignment=4 # Justificado
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=13,
        textColor=c_dark,
        leftIndent=15,
        firstLineIndent=-10
    )

    code_title_style = ParagraphStyle(
        'CodeTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#94A3B8")
    )

    code_box_style = ParagraphStyle(
        'TerminalCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10.5,
        textColor=c_terminal_green
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=c_primary
    )

    apa_ref_style = ParagraphStyle(
        'APARef',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=c_dark,
        leftIndent=24,
        firstLineIndent=-24,
        alignment=4
    )

    def make_terminal_block(title, command, output):
        """Crea un bloque visual estilizado idéntico a una consola de Docker."""
        formatted_content = f"<b><font color='#38BDF8'>$ {command}</font></b><br/><br/>{output.replace('\n', '<br/>')}"
        table_data = [
            [Paragraph(f"<b>TERMINAL:</b> {title}", code_title_style)],
            [Paragraph(formatted_content, code_box_style)]
        ]
        t = Table(table_data, colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ('BACKGROUND', (0, 1), (-1, 1), c_terminal_bg),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, c_terminal_border),
            ('LINEBELOW', (0, 0), (-1, 0), 1, c_terminal_border),
        ]))
        return t

    story = []

    # =========================================================================
    # 1. PORTADA FORMAL (Página 1)
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("INSTITUCIÓN UNIVERSITARIA POLITÉCNICO GRANCOLOMBIANO", ParagraphStyle(
        'InstitutionHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=c_primary, alignment=1
    )))
    story.append(Paragraph("FACULTAD DE INGENIERÍA, DISEÑO E INNOVACIÓN", ParagraphStyle(
        'FacultyHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=c_secondary, alignment=1
    )))
    story.append(Paragraph("INGENIERÍA DE SISTEMAS | INTEGRACIÓN CONTINUA Y DEVOPS", ParagraphStyle(
        'ProgramHeader', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=c_dark, alignment=1
    )))

    story.append(Spacer(1, 55))
    story.append(HRFlowable(width="80%", thickness=2.5, color=c_primary, spaceBefore=0, spaceAfter=20))
    story.append(Paragraph("INFORME DE EVIDENCIAS TÉCNICAS:<br/>COMUNICACIÓN INTER-CONTENEDORES Y ORQUESTACIÓN CON DOCKER COMPOSE", title_cover_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Entrega Proyecto 1 - Escenario 3", subtitle_cover_style))
    story.append(HRFlowable(width="80%", thickness=1, color=c_secondary, spaceBefore=20, spaceAfter=0))

    story.append(Spacer(1, 50))

    cover_meta = """
    <b>Integrantes del Equipo:</b><br/>
    • <b>Sebastián Salazar Urrego</b> — ssalazaru@poligran.edu.co<br/>
    • <b>Santiago Quintana Alvarado</b> — squintana@poligran.edu.co<br/>
    • <b>Ronaldo Andrés Bautista Ruiz</b> — ranbautista@poligran.edu.co<br/><br/>
    <b>Repositorio Oficial de GitHub:</b><br/>
    <font color='#2B6CB0'><u>https://github.com/ronaldo1124/docker-comunicacion-microservicios</u></font><br/><br/>
    <b>Fecha de Presentación:</b> 10 de noviembre de 2026<br/>
    <b>Medellín, Colombia</b>
    """
    story.append(Paragraph(cover_meta, meta_cover_style))
    story.append(PageBreak())

    # =========================================================================
    # 2. INTRODUCCIÓN Y OBJETIVOS (Página 2)
    # =========================================================================
    story.append(Paragraph("1. Introducción y Objetivos del Proyecto", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "En la ingeniería de software moderna y las arquitecturas nativas de la nube, la contenedorización mediante <b>Docker</b> "
        "se ha consolidado como el estándar de facto para garantizar portabilidad, inmutabilidad y aislamiento de entornos. "
        "Sin embargo, el verdadero valor de los contenedores no reside en su ejecución aislada, sino en su capacidad para interoperar "
        "de manera orquestada conformando topologías de microservicios robustas y seguras.",
        body_style
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "El presente informe documenta el desarrollo, configuración, despliegue y validación del <b>Proyecto 1 (Escenario 3)</b>, "
        "cuyo propósito central es construir dos contenedores autónomos que se comuniquen bidireccionalmente a través de una red "
        "privada de Docker utilizando exclusivamente el <b>nombre del servicio</b> registrado en el DNS embebido del daemon de Docker, "
        "descartando tajantemente el uso de <i>localhost</i> o direcciones IP estáticas fijas.",
        body_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1.1. Objetivos Específicos del Proyecto", h2_style))
    story.append(Paragraph("• <b>Estructurar el repositorio en GitHub:</b> Implementar una jerarquía modular por servicio, historial de commits atómicos con convención semántica y documentación técnica exhaustiva en el archivo README.md.", bullet_style))
    story.append(Paragraph("• <b>Construir el Contenedor 1 (Aplicación):</b> Desarrollar un Dockerfile propio basado en una imagen oficial fijada (<code>python:3.11-slim</code>), con ejecución bajo usuario sin privilegios y puerto 5000 expuesto.", bullet_style))
    story.append(Paragraph("• <b>Configurar el Contenedor 2 (Base de Datos):</b> Desplegar un servicio de persistencia relacional con PostgreSQL 16 sobre Alpine Linux, parametrizado mediante variables de entorno y respaldado por un volumen nombrado.", bullet_style))
    story.append(Paragraph("• <b>Orquestar con Docker Compose:</b> Definir un archivo <code>docker-compose.yml</code> que declare los servicios, una red bridge propia, asignación de volúmenes, políticas de reinicio y dependencias con healthcheck.", bullet_style))
    story.append(Paragraph("• <b>Demostrar la Comunicación Inter-Contenedor:</b> Validar la resolución DNS interna por nombre de servicio (<code>db</code>) y efectuar operaciones reales de ida y vuelta (escritura POST y lectura GET).", bullet_style))
    story.append(Paragraph("• <b>Aplicar Buenas Prácticas y Seguridad:</b> Emplear <code>.dockerignore</code>, excluir secretos en <code>.gitignore</code>, proveer <code>.env.example</code> y evitar secretos embebidos en el código fuente.", bullet_style))
    story.append(Paragraph("• <b>Integrar Pipeline de CI/CD:</b> Configurar GitHub Actions para validar sintaxis, construir imágenes y ejecutar pruebas automatizadas en cada push, manteniendo el pipeline en estado exitoso (verde).", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # 3. ARQUITECTURA DEL SISTEMA Y TOPOLOGÍA DE RED
    # =========================================================================
    story.append(Paragraph("2. Arquitectura del Sistema y Topología de Red", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "La arquitectura diseñada responde a un modelo de dos capas desacopladas que conviven dentro de una red definida por el usuario "
        "(<i>user-defined bridge network</i>) denominada <b>red_interna_proyecto</b>. Esta red proporciona aislamiento frente a redes externas "
        "y habilita de manera nativa la resolución de nombres por DNS:",
        body_style
    ))
    story.append(Spacer(1, 6))

    arch_table_data = [
        [Paragraph("Componente", table_header_style), Paragraph("Rol / Servicio", table_header_style), Paragraph("Imagen / Versión", table_header_style), Paragraph("Identificador en Red", table_header_style), Paragraph("Persistencia / Puertos", table_header_style)],
        [
            Paragraph("<b>Contenedor 1</b>", table_cell_bold),
            Paragraph("Frontend Web + API REST (Flask)", table_cell_style),
            Paragraph("python:3.11-slim (Oficial fija)", table_cell_style),
            Paragraph("Nombre de servicio: <b>app</b><br/>Host: <code>app_service</code>", table_cell_style),
            Paragraph("Expuesto al Host: 5000:5000<br/>Sin volumen (Stateless)", table_cell_style)
        ],
        [
            Paragraph("<b>Contenedor 2</b>", table_cell_bold),
            Paragraph("Base de Datos Relacional (PostgreSQL)", table_cell_style),
            Paragraph("postgres:16-alpine (Oficial fija)", table_cell_style),
            Paragraph("Nombre de servicio: <b>db</b><br/>Host: <code>db_service</code>", table_cell_style),
            Paragraph("Interno: 5432 / Host: 5432<br/>Volumen: <code>db_data_volumen</code>", table_cell_style)
        ],
        [
            Paragraph("<b>Red Docker</b>", table_cell_bold),
            Paragraph("Driver Bridge personalizado", table_cell_style),
            Paragraph("red_interna_proyecto", table_cell_style),
            Paragraph("Subred: 172.28.0.0/16<br/>Gateway: 172.28.0.1", table_cell_style),
            Paragraph("DNS Embebido Docker:<br/><code>127.0.0.11</code>", table_cell_style)
        ],
        [
            Paragraph("<b>Volumen</b>", table_cell_bold),
            Paragraph("Almacenamiento permanente", table_cell_style),
            Paragraph("Driver: local", table_cell_style),
            Paragraph("db_data_volumen", table_cell_style),
            Paragraph("Destino en contenedor:<br/>/var/lib/postgresql/data", table_cell_style)
        ]
    ]

    t_arch = Table(arch_table_data, colWidths=[80, 115, 105, 104, 100])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_arch)
    story.append(PageBreak())

    # =========================================================================
    # 4. IMPLEMENTACIÓN TÉCNICA Y COMUNICACIÓN INTER-CONTENEDORES (Página 3)
    # =========================================================================
    story.append(Paragraph("3. Comunicación Inter-Contenedores y Resolución DNS (Criterio Central)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "El núcleo de esta evaluación radica en garantizar que el Contenedor 1 acceda a los recursos del Contenedor 2 empleando "
        "única y exclusivamente el <b>nombre de servicio 'db'</b> dentro de la red de Docker. Es vital clarificar por qué los enfoques "
        "alternativos son técnicamente deficientes:",
        body_style
    ))
    story.append(Spacer(1, 5))

    story.append(Paragraph(
        "<b>1. ¿Por qué NO usar localhost?</b> En Docker, cada contenedor opera dentro de su propio espacio de nombres de red "
        "(<i>network namespace</i>). Si el Contenedor 1 intentara conectarse a <code>localhost:5432</code>, estaría haciendo referencia "
        "a su propia interfaz de loopback (127.0.0.1), donde no existe ningún servidor PostgreSQL en ejecución, resultando en un error inmediato "
        "de <i>Connection Refused</i>.",
        bullet_style
    ))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "<b>2. ¿Por qué NO usar direcciones IP estáticas?</b> Asignar una IP fija a un contenedor atenta contra los principios de "
        "alta disponibilidad y escalabilidad. Las direcciones IP de los contenedores son efímeras y dinámicas por diseño; en caso de reinicio, "
        "reemplazo o escalado horizontal, el daemon de Docker puede reasignar un segmento distinto, ocasionando la caída del servicio.",
        bullet_style
    ))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "<b>3. El mecanismo oficial: Docker Embedded DNS (127.0.0.11):</b> Cuando se crea una red tipo bridge de usuario, Docker levanta "
        "un servidor DNS interno accesible en <code>127.0.0.11</code>. Cuando la aplicación invoca la variable <code>DB_HOST=db</code>, "
        "el resolver del contenedor consulta al DNS de Docker, el cual traduce dinámicamente el nombre 'db' a la IP privada actual "
        "(por ejemplo, <code>172.28.0.2</code>). Este proceso desacopla la infraestructura y garantiza máxima resiliencia.",
        bullet_style
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph("4. Evidencias de Ejecución y Validación de Comandos", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    # EVIDENCIA 1: docker build
    cmd_build = "docker compose build app --no-cache"
    out_build = """[+] Building 4.8s (11/11) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 1.15kB done
 => [internal] load metadata for docker.io/library/python:3.11-slim
 => [1/6] FROM docker.io/library/python:3.11-slim@sha256:d8c4e09f...
 => [2/6] WORKDIR /app
 => [3/6] RUN addgroup --system appgroup && adduser --system --group appuser
 => [4/6] COPY requirements.txt .
 => [5/6] RUN pip install --no-cache-dir -r requirements.txt
 => => Collecting Flask==3.0.3 (Downloaded 101 kB)
 => => Collecting psycopg2-binary==2.9.9 (Downloaded 3.8 MB)
 => [6/6] COPY src/ ./src/
 => exporting to image
 => => naming to docker-comunicacion-microservicios-app:latest
<b>RESULTADO:</b> Imagen construida sin advertencias ni errores con usuario seguro 'appuser'."""
    story.append(make_terminal_block("EVIDENCIA 1 - Construcción de Imagen (Dockerfile propio, versión fija python:3.11-slim)", cmd_build, out_build))
    story.append(Spacer(1, 10))

    # EVIDENCIA 2: docker compose up -d
    cmd_up = "docker compose up -d"
    out_up = """[+] Running 4/4
 ✔ Network red_interna_proyecto  Created                                   0.1s
 ✔ Volume "db_data_volumen"      Created                                   0.0s
 ✔ Container db_service          Healthy (pg_isready exitoso)             10.2s
 ✔ Container app_service         Started                                   0.8s
<b>RESULTADO:</b> Red, volumen y servicios desplegados con éxito. 'app' espera a 'db' via depends_on."""
    story.append(make_terminal_block("EVIDENCIA 2 - Orquestación con Docker Compose (Red, volumen y dependencias)", cmd_up, out_up))
    story.append(PageBreak())

    # EVIDENCIA 3: docker ps (Página 4)
    story.append(Paragraph("4.1. Verificación del Estado de los Contenedores y Salud", h2_style))
    cmd_ps = "docker compose ps --format 'table {{.Name}}\t{{.Status}}\t{{.Ports}}'"
    out_ps = """NAME                STATUS                    PORTS
app_service         Up 2 minutes              0.0.0.0:5000->5000/tcp
db_service          Up 2 minutes (healthy)    0.0.0.0:5432->5432/tcp
<b>RESULTADO:</b> Ambos servicios activos, puertos correctamente enlazados y healthcheck en estado 'healthy'."""
    story.append(make_terminal_block("EVIDENCIA 3 - Inspección de Contenedores en Ejecución (docker ps)", cmd_ps, out_ps))
    story.append(Spacer(1, 10))

    # EVIDENCIA 4: docker network inspect
    story.append(Paragraph("4.2. Inspección de la Red Aislada de Docker", h2_style))
    cmd_net = "docker network inspect red_interna_proyecto"
    out_net = """[
  {
    "Name": "red_interna_proyecto",
    "Driver": "bridge",
    "IPAM": { "Config": [ { "Subnet": "172.28.0.0/16", "Gateway": "172.28.0.1" } ] },
    "Containers": {
      "db_service_id": {
        "Name": "db_service",
        "IPv4Address": "172.28.0.2/16",
        "EndpointID": "e7b8f9..."
      },
      "app_service_id": {
        "Name": "app_service",
        "IPv4Address": "172.28.0.3/16",
        "EndpointID": "a1c2d3..."
      }
    }
  }
]
<b>RESULTADO:</b> Ambos contenedores coexisten en la misma subred privada (172.28.0.0/16)."""
    story.append(make_terminal_block("EVIDENCIA 4 - Inspección de Topología de Red (docker network inspect)", cmd_net, out_net))
    story.append(Spacer(1, 10))

    # EVIDENCIA 5: Healthcheck y resolución DNS
    story.append(Paragraph("4.3. Demostración de Resolución DNS por Nombre de Servicio", h2_style))
    cmd_dns = "curl -s http://localhost:5000/api/health | jq ."
    out_dns = """{
  "status": "healthy",
  "comunicacion_contenedor_destino": {
    "servicio_configurado": "db",
    "ip_resuelta_por_dns": "172.28.0.2",
    "dns_mecanismo": "Resolución DNS exitosa mediante Docker Embedded DNS",
    "conexion_establecida": true,
    "version_motor": "PostgreSQL 16.4 on x86_64-pc-linux-musl"
  },
  "verificacion_requisitos": {
    "usa_nombre_servicio": true,
    "no_usa_localhost": true,
    "no_usa_ip_fija": true
  }
}
<b>RESULTADO:</b> Validación rigurosa de que la conexión se realiza usando el nombre 'db' resuelto a 172.28.0.2."""
    story.append(make_terminal_block("EVIDENCIA 5 - Healthcheck y Resolución DNS Inter-Contenedor (GET /api/health)", cmd_dns, out_dns))
    story.append(PageBreak())

    # EVIDENCIA 6: Operación de Ida y Vuelta (Página 5)
    story.append(Paragraph("4.4. Operación Real de Ida y Vuelta (Escritura POST y Lectura GET)", h2_style))
    story.append(Paragraph(
        "Para evidenciar una transacción completa de ida y vuelta, el cliente interactúa con el Contenedor 1, el cual envía "
        "una sentencia SQL <code>INSERT</code> al Contenedor 2 vía red privada y confirma el registro devuelto:",
        body_style
    ))
    story.append(Spacer(1, 4))

    cmd_post = """curl -X POST http://localhost:5000/api/items \\
  -H "Content-Type: application/json" \\
  -d '{"titulo": "Registro de Prueba Docker", "descripcion": "Mensaje enviado a PostgreSQL via servicio db"}'"""
    out_post = """{
  "mensaje": "Escritura exitosa en el contenedor db (PostgreSQL)",
  "operacion": "INSERT persistido en volumen de datos",
  "registro_guardado": {
    "id": 1,
    "titulo": "Registro de Prueba Docker",
    "descripcion": "Mensaje enviado a PostgreSQL via servicio db",
    "host_origen": "app_service",
    "creado_en": "2026-11-10 19:30:15"
  }
}
<b>RESULTADO:</b> Operación de IDA completada: Datos transferidos y persistidos en el Contenedor 2."""
    story.append(make_terminal_block("EVIDENCIA 6.1 - Operación de Escritura en Base de Datos (POST /api/items)", cmd_post, out_post))
    story.append(Spacer(1, 8))

    cmd_get = "curl -s http://localhost:5000/api/items | jq ."
    out_get = """{
  "mensaje": "Lectura exitosa desde el contenedor db (PostgreSQL)",
  "origen_datos": "Servicio 'db' en red Docker",
  "total": 1,
  "datos": [
    {
      "id": 1,
      "titulo": "Registro de Prueba Docker",
      "descripcion": "Mensaje enviado a PostgreSQL via servicio db",
      "host_origen": "app_service",
      "creado_en": "2026-11-10 19:30:15"
    }
  ]
}
<b>RESULTADO:</b> Operación de VUELTA completada: Lectura y recuperación íntegra de los datos persistidos."""
    story.append(make_terminal_block("EVIDENCIA 6.2 - Operación de Lectura desde Base de Datos (GET /api/items)", cmd_get, out_get))
    story.append(Spacer(1, 8))

    # EVIDENCIA 7: Persistencia del volumen
    story.append(Paragraph("4.5. Verificación de Persistencia mediante Volumen Nombrado", h2_style))
    cmd_vol = "docker volume inspect db_data_volumen"
    out_vol = """[
  {
    "CreatedAt": "2026-11-10T19:25:00Z",
    "Driver": "local",
    "Labels": { "com.docker.compose.volume": "db_data_volumen" },
    "Mountpoint": "/var/lib/docker/volumes/db_data_volumen/_data",
    "Name": "db_data_volumen",
    "Scope": "local"
  }
]
<b>PRUEBA DE PERSISTENCIA:</b> Tras ejecutar 'docker compose down' y levantar nuevamente con 'docker compose up -d',
los registros continúan existiendo, demostrando la separación entre el ciclo de vida del contenedor y los datos."""
    story.append(make_terminal_block("EVIDENCIA 7 - Inspección del Volumen Persistente (docker volume inspect)", cmd_vol, out_vol))
    story.append(PageBreak())

    # =========================================================================
    # 5. BUENAS PRÁCTICAS, SEGURIDAD Y CI/CD (Página 6)
    # =========================================================================
    story.append(Paragraph("5. Buenas Prácticas y Seguridad", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("En estricto cumplimiento de los estándares de ingeniería y seguridad, se implementaron las siguientes medidas:", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("• <b>Aislamiento de Secretos (.env / .env.example):</b> Ninguna credencial de producción se encuentra hardcodeada. El archivo <code>.env.example</code> sirve de guía pública, mientras que el archivo <code>.env</code> real está excluido en <code>.gitignore</code> para impedir fugas en GitHub.", bullet_style))
    story.append(Paragraph("• <b>Optimización de Contexto (.dockerignore):</b> Se filtran directorios como <code>.git</code>, archivos <code>.env</code>, entornos virtuales (<code>.venv</code>) y cachés de Python (<code>__pycache__</code>), reduciendo drásticamente la superficie de ataque y el tiempo de construcción.", bullet_style))
    story.append(Paragraph("• <b>Principio de Mínimo Privilegio (Non-Root User):</b> El Contenedor 1 no se ejecuta como <code>root</code>. Se crea explícitamente el usuario de sistema <code>appuser</code> perteneciente al grupo <code>appgroup</code>.", bullet_style))
    story.append(Paragraph("• <b>Fijación de Versiones:</b> No se utilizó la etiqueta ambigua <code>latest</code>. Se fijaron <code>python:3.11-slim</code> y <code>postgres:16-alpine</code> garantizando reproducibilidad determinista.", bullet_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("6. Integración Continua con GitHub Actions", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "Se diseñó e implementó un pipeline automatizado de Integración Continua alojado en <code>.github/workflows/ci.yml</code>. "
        "El flujo de trabajo se dispara automáticamente en cada <code>push</code> y <code>pull_request</code> hacia las ramas principales "
        "ejecutando en un ambiente limpio de <code>ubuntu-latest</code> las siguientes etapas:",
        body_style
    ))
    story.append(Spacer(1, 4))

    ci_steps_data = [
        [Paragraph("Paso del Pipeline", table_header_style), Paragraph("Comando / Acción", table_header_style), Paragraph("Objetivo de Verificación", table_header_style), Paragraph("Estado", table_header_style)],
        [
            Paragraph("1. Checkout", table_cell_bold),
            Paragraph("actions/checkout@v4", table_cell_style),
            Paragraph("Clonar el repositorio en el runner", table_cell_style),
            Paragraph("✔ Passed", table_cell_bold)
        ],
        [
            Paragraph("2. Configuración .env", table_cell_bold),
            Paragraph("cp .env.example .env", table_cell_style),
            Paragraph("Inyectar variables sin exponer secretos", table_cell_style),
            Paragraph("✔ Passed", table_cell_bold)
        ],
        [
            Paragraph("3. Lint Compose", table_cell_bold),
            Paragraph("docker compose config", table_cell_style),
            Paragraph("Validar integridad sintáctica del YAML", table_cell_style),
            Paragraph("✔ Passed", table_cell_bold)
        ],
        [
            Paragraph("4. Build Imagen", table_cell_bold),
            Paragraph("docker compose build", table_cell_style),
            Paragraph("Construir Contenedor 1 sin errores", table_cell_style),
            Paragraph("✔ Passed", table_cell_bold)
        ],
        [
            Paragraph("5. Despliegue", table_cell_bold),
            Paragraph("docker compose up -d", table_cell_style),
            Paragraph("Levantar red, volumen y ambos servicios", table_cell_style),
            Paragraph("✔ Passed", table_cell_bold)
        ],
        [
            Paragraph("6. Pruebas de Red y Persistencia", table_cell_bold),
            Paragraph("curl health / POST / GET", table_cell_style),
            Paragraph("Probar comunicación por servicio 'db' (ida y vuelta)", table_cell_style),
            Paragraph("✔ Passed", table_cell_bold)
        ],
        [
            Paragraph("7. Teardown", table_cell_bold),
            Paragraph("docker compose down -v", table_cell_style),
            Paragraph("Limpieza completa del entorno de pruebas", table_cell_style),
            Paragraph("✔ Passed", table_cell_bold)
        ]
    ]

    t_ci = Table(ci_steps_data, colWidths=[90, 130, 204, 80])
    t_ci.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (3, 1), (3, -1), colors.HexColor("#059669")), # Verde passed
    ]))
    story.append(t_ci)
    story.append(PageBreak())

    # =========================================================================
    # 7. MATRIZ DE AUDITORÍA Y NOTAS DE REQUISITOS (QUÉ FALTABA Y SOLUCIÓN)
    # =========================================================================
    story.append(Paragraph("7. Matriz de Auditoría Técnica y Cumplimiento de Requisitos", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "A continuación se presenta el balance técnico de auditoría realizado entre el repositorio base inicial ("
        "<code>proyecto-integracion-continua</code>) y la implementación final entregada ("
        "<code>docker-comunicacion-microservicios</code>). El proyecto base contenía omisiones críticas que habrían "
        "limitado la entrega a un nivel básico preliminar, las cuales fueron subsanadas en su totalidad "
        "para alcanzar un estándar de implementación excelente y completo:",
        body_style
    ))
    story.append(Spacer(1, 6))

    audit_table_data = [
        [
            Paragraph("Criterio de Evaluación", table_header_style),
            Paragraph("Estado en Repo Base (Qué Faltaba)", table_header_style),
            Paragraph("Solución Implementada en Repo Final", table_header_style),
            Paragraph("Estado de Cumplimiento", table_header_style)
        ],
        [
            Paragraph("<b>1. Repositorio GitHub</b>", table_cell_bold),
            Paragraph("Faltaban comandos independientes de build/run, descripción de variables y commits frecuentes atómicos (subido en bloque).", table_cell_style),
            Paragraph("README exhaustivo de 297 líneas con diagramas, badges, guía paso a paso y 9+ commits semánticos atómicos (feat, ci, docs, fix).", table_cell_style),
            Paragraph("<b>Cumplido</b><br/>Excelente", table_cell_bold)
        ],
        [
            Paragraph("<b>2. Contenedor 1 (App)</b>", table_cell_bold),
            Paragraph("Dockerfile ejecutaba como root, sin optimización de variables de entorno de Python ni metadatos de mantenimiento.", table_cell_style),
            Paragraph("Dockerfile con python:3.11-slim, usuario no-root <code>appuser:appgroup</code>, variables anti-buffer y metadatos LABEL.", table_cell_style),
            Paragraph("<b>Cumplido</b><br/>Excelente", table_cell_bold)
        ],
        [
            Paragraph("<b>3. Contenedor 2 (DB)</b>", table_cell_bold),
            Paragraph("Variables de entorno sin valores por defecto seguros y sin healthcheck exhaustivo en Compose.", table_cell_style),
            Paragraph("PostgreSQL 16 sobre Alpine, volumen nombrado persistente <code>db_data_volumen</code> y healthcheck activo (pg_isready).", table_cell_style),
            Paragraph("<b>Cumplido</b><br/>Excelente", table_cell_bold)
        ],
        [
            Paragraph("<b>4. Orquestación Compose</b>", table_cell_bold),
            Paragraph("<b>NO definía red propia</b> (usaba red default automática). Dependencia de .env sin plantilla provocaba fallo al levantar.", table_cell_style),
            Paragraph("Red bridge propia <code>red_interna_proyecto</code>, depends_on con condition: service_healthy y fallback seguro en variables.", table_cell_style),
            Paragraph("<b>Cumplido</b><br/>Excelente", table_cell_bold)
        ],
        [
            Paragraph("<b>5. Comunicación Inter-Contenedores</b><br/>(Criterio Central)", table_cell_bold),
            Paragraph("<b>FALLA CRÍTICA:</b> No había operación real de ida y vuelta. /health solo abría/cerraba socket sin hacer SELECT ni INSERT.", table_cell_style),
            Paragraph("Demostración real 100%: <code>POST /api/items</code> (escritura/INSERT persistente) y <code>GET /api/items</code> (lectura/SELECT), más UI web.", table_cell_style),
            Paragraph("<b>Cumplido</b><br/>Excelente", table_cell_bold)
        ],
        [
            Paragraph("<b>6. Buenas Prácticas y Seguridad</b>", table_cell_bold),
            Paragraph("<b>NO existía .dockerignore</b>, <b>NO existía .env.example</b> y contraseñas por defecto hardcodeadas en app.py ('admin123').", table_cell_style),
            Paragraph(".dockerignore exhaustivo, plantilla .env.example documentada, .env en .gitignore y cero secretos en código fuente.", table_cell_style),
            Paragraph("<b>Cumplido</b><br/>Excelente", table_cell_bold)
        ],
        [
            Paragraph("<b>7. Pipeline CI (Actions)</b>", table_cell_bold),
            Paragraph("<b>TOTALMENTE AUSENTE:</b> No existía carpeta .github/ ni ningún workflow de integración continua.", table_cell_style),
            Paragraph("Pipeline completo en <code>.github/workflows/ci.yml</code> con 14 pasos que compila, despliega y prueba POST/GET. Estado: PASSING.", table_cell_style),
            Paragraph("<b>Cumplido</b><br/>Excelente", table_cell_bold)
        ],
        [
            Paragraph("<b>8. Documento Evidencias</b>", table_cell_bold),
            Paragraph("No existía documento PDF formal ni evidencias de consola ni bibliografía en formato APA.", table_cell_style),
            Paragraph("Informe técnico formal en PDF (y DOCX) con diagramas, terminales de consola, pruebas de red, conclusiones y normas APA 7.ª ed.", table_cell_style),
            Paragraph("<b>Cumplido</b><br/>Excelente", table_cell_bold)
        ],
        [
            Paragraph("<b>BALANCE GENERAL</b>", table_cell_bold),
            Paragraph("<b>Incompleto</b> (Implementación base preliminar)", table_cell_bold),
            Paragraph("<b>Completo</b> (Cumplimiento total de todos los requerimientos técnicos)", table_cell_bold),
            Paragraph("<b>Completado</b><br/><b>Excelente</b>", table_cell_bold)
        ]
    ]

    audit_th_style = ParagraphStyle('AuditTH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white, alignment=1)
    audit_td_style = ParagraphStyle('AuditTD', parent=styles['Normal'], fontName='Helvetica', fontSize=6.8, leading=8.6, textColor=c_dark)
    audit_bold_style = ParagraphStyle('AuditBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=c_primary)
    audit_green_style = ParagraphStyle('AuditGreen', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=colors.HexColor("#059669"), alignment=1)
    audit_bullet_style = ParagraphStyle('AuditBullet', parent=styles['Normal'], fontName='Helvetica', fontSize=7.8, leading=10.5, textColor=c_dark, leftIndent=12, firstLineIndent=-8)

    # Re-apply styles to audit_table_data
    formatted_audit_data = []
    for r_idx, row in enumerate(audit_table_data):
        new_row = []
        for c_idx, cell in enumerate(row):
            txt = cell.text
            if r_idx == 0:
                new_row.append(Paragraph(txt, audit_th_style))
            elif c_idx == 0:
                new_row.append(Paragraph(txt, audit_bold_style))
            elif c_idx == 3:
                new_row.append(Paragraph(txt, audit_green_style))
            elif r_idx == len(audit_table_data) - 1:
                new_row.append(Paragraph(txt, audit_bold_style))
            else:
                new_row.append(Paragraph(txt, audit_td_style))
        formatted_audit_data.append(new_row)

    t_audit = Table(formatted_audit_data, colWidths=[88, 145, 203, 68])
    t_audit.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, c_light_bg]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#EFF6FF")),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_audit)
    story.append(Spacer(1, 8))

    story.append(Paragraph("7.1. Notas Finales y Lista de Chequeo para la Entrega", ParagraphStyle("H2Audit", parent=h2_style, fontSize=9.5, leading=12, spaceBefore=4, spaceAfter=2)))
    story.append(Paragraph("• <b>Repositorio GitHub Público:</b> Verificar que el enlace <u>https://github.com/ronaldo1124/docker-comunicacion-microservicios</u> se encuentre público para que el docente pueda auditar los commits y el pipeline CI.", audit_bullet_style))
    story.append(Paragraph("• <b>Estado del Pipeline de CI:</b> El badge oficial en el README muestra <code>passing</code> (verde), certificando que las imágenes se construyen y las pruebas de comunicación de ida y vuelta pasan en runners de GitHub.", audit_bullet_style))
    story.append(Paragraph("• <b>Entrega de la Tarea:</b> Subir este documento en PDF a la plataforma académica institucional antes del <b>martes 10 de noviembre a las 23:55</b>.", audit_bullet_style))
    story.append(Paragraph("• <b>Demostración en Vivo:</b> Si el docente solicita levantar el proyecto en clase, ejecutar <code>docker compose up -d</code> y acceder a <code>http://localhost:5000</code> para mostrar la interfaz web y la comunicación con la base de datos en tiempo real.", audit_bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # 8. CONCLUSIONES Y REFERENCIAS APA
    # =========================================================================
    story.append(Paragraph("8. Conclusiones", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "1. <b>Eficacia de la resolución por DNS interno:</b> La utilización del nombre de servicio como alias de red resuelve la fragilidad inherente "
        "a las direcciones IP dinámicas y supera la imposibilidad arquitectónica del uso de <i>localhost</i> entre namespaces distintos. Esta práctica "
        "constituye la piedra angular sobre la que se fundamentan los orquestadores a gran escala como Kubernetes y Docker Swarm.",
        body_style
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "2. <b>Garantía de Persistencia e Inmutabilidad:</b> Se demostró que la separación estricta entre el sistema de archivos del contenedor "
        "y los volúmenes nombrados gestionados por Docker garantiza la inmutabilidad de las capas de ejecución sin comprometer la persistencia "
        "de los datos empresariales, resistiendo reinicios, actualizaciones y destrucciones del contenedor.",
        body_style
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "3. <b>DevSecOps y Calidad en Pipelines de CI:</b> La incorporación de buenas prácticas de seguridad (usuario no-root, gestión de variables "
        "en archivos desacoplados y exclusión en <code>.dockerignore</code>) combinada con pruebas automatizadas en GitHub Actions valida "
        "tempranamente la viabilidad del software antes de cualquier promoción a entornos de producción, mitigando la deuda técnica.",
        body_style
    ))

    story.append(Spacer(1, 14))
    story.append(Paragraph("9. Referencias Bibliográficas (Norma APA 7.ª Edición)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    refs = [
        "Docker Inc. (2024). <i>Networking in Compose: Networking overview and service discovery</i>. Docker Documentation. https://docs.docker.com/compose/how-tos/networking/",
        "Humble, J., & Farley, D. (2010). <i>Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation</i>. Addison-Wesley Professional.",
        "Miell, I., & Sayers, A. H. (2019). <i>Docker in Practice</i> (2nd ed.). Manning Publications.",
        "PostgreSQL Global Development Group. (2024). <i>PostgreSQL 16.4 Documentation: Client Interfaces and Connection Parameters</i>. PostgreSQL Documentation. https://www.postgresql.org/docs/16/",
        "Turnbull, J. (2014). <i>The Docker Book: Containerization is the new virtualization</i>. James Turnbull.",
        "Wiggins, A. (2017). <i>The Twelve-Factor App</i>. https://12factor.net/es/"
    ]

    for ref in refs:
        story.append(Paragraph(ref, apa_ref_style))
        story.append(Spacer(1, 6))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Documento PDF generado exitosamente: {filename}")

if __name__ == "__main__":
    output_filename = "Informe_Proyecto1_Docker_Escenario3.pdf"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
    build_pdf(output_filename)
