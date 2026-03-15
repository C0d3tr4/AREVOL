import sys
import os
import json
import urllib.request
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                               QFileDialog, QComboBox, QMessageBox, QInputDialog,
                               QToolBar, QStackedWidget, QPlainTextEdit,
                               QDialog, QListWidget, QListWidgetItem, QDialogButtonBox, QLabel, QLineEdit, QColorDialog,
                               QFontComboBox, QFormLayout)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QAction, QFont, QPixmap, QIcon, QColor, QPalette
from PySide6.QtCore import Qt, QSize, QThread, Signal, QEvent, QTimer

# --- RUTA DE RECURSOS (funciona en desarrollo y como .exe) ---
def ruta_recurso(nombre):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, nombre)

# --- ESTADO GLOBAL DEL TEMA ---
THEME_MODE = "system"  # Opciones: "system", "dark", "light"

def is_dark_mode():
    if THEME_MODE == "dark": return True
    if THEME_MODE == "light": return False
    # Si es system, leemos la paleta base del sistema operativo
    paleta = QApplication.style().standardPalette()
    return paleta.color(QPalette.Window).lightness() < 128

# --- DICCIONARIO DE INTERFAZ BILINGÜE ---
UI = {
    "ES": {
        "title": "AREVOL - Editor Gráfico HTML",
        "open": "📂 Abrir HTML",
        "add_lang": "➕ Añadir Idioma",
        "img_gal": "🌍 Galería de Imágenes",
        "vid_gal": "🎥 Galería de Videos",
        "meta_edit": "📊 Datos Globales (I18N)",
        "code_mode": "💻 Modo Código",
        "vis_mode": "👁️ Modo Visual",
        "save": "💾 GUARDAR",
        "link": "Enlace",
        "color": "Color",
        "bullet": "Viñeta",
        "num": "Números",
        "quote": "Citar",
        "align_left": "Izquierda",
        "align_center": "Centrar",
        "align_right": "Derecha",
        "align_just": "Justificado",
        "toggle_btn": "🌐 ENGLISH",
        "msg_open_first": "Empieza a escribir o abre un archivo HTML.",
        "msg_success": "¡Éxito!",
        "msg_saved": "¡El archivo ha sido guardado correctamente!",
        "msg_updated": "Actualizado en {} lugares.",
        "msg_select_img": "Selecciona una imagen.",
        "msg_select_vid": "Selecciona un video.",
        "msg_no_img": "No se encontraron imágenes.",
        "msg_no_vid": "No se encontraron videos.",
        "block_normal": "Texto Normal",
        "block_h1": "Título 1 (Grande)",
        "block_h2": "Título 2 (Medio)",
        "block_h3": "Título 3 (Pequeño)",
        "about_btn": "ℹ️ Acerca de",
        "about_title": "Acerca de AREVOL",
        "about_text": "<b>AREVOL - Editor Gráfico HTML</b><br><br>Creado como una forma para editar archivos HTML multilingües de manera más sencilla.<br><br>Programado por <b>José Alexander Lovera Aquino</b>.<br><br>Software Open Source."
    },
    "EN": {
        "title": "AREVOL - HTML Graphic Editor",
        "open": "📂 Open HTML",
        "add_lang": "➕ Add Language",
        "img_gal": "🌍 Image Gallery",
        "vid_gal": "🎥 Video Gallery",
        "meta_edit": "📊 Global Data (I18N)",
        "code_mode": "💻 Code Mode",
        "vis_mode": "👁️ Visual Mode",
        "save": "💾 SAVE",
        "link": "Link",
        "color": "Color",
        "bullet": "Bullet List",
        "num": "Numbers",
        "quote": "Quote",
        "align_left": "Align Left",
        "align_center": "Center",
        "align_right": "Align Right",
        "align_just": "Justify",
        "toggle_btn": "🌐 ESPAÑOL",
        "msg_open_first": "Start typing or open an HTML file.",
        "msg_success": "Success!",
        "msg_saved": "The file has been saved successfully!",
        "msg_updated": "Updated in {} places.",
        "msg_select_img": "Select an image.",
        "msg_select_vid": "Select a video.",
        "msg_no_img": "No images found.",
        "msg_no_vid": "No videos found.",
        "block_normal": "Normal Text",
        "block_h1": "Heading 1",
        "block_h2": "Heading 2",
        "block_h3": "Heading 3",
        "about_btn": "ℹ️ About",
        "about_title": "About AREVOL",
        "about_text": "<b>AREVOL - HTML Graphic Editor</b><br><br>Created as a way to edit multilingual HTML files more easily.<br><br>Programmed by <b>José Alexander Lovera Aquino</b>.<br><br>Open Source Software."
    }
}

# --- DIÁLOGO PARA EDITAR METADATOS (I18N y EVENT_INFO) ---
class DialogoMetadata(QDialog):
    def __init__(self, lang_actual, data_i18n, data_event_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Editar Cabecera - Idioma: {lang_actual}")
        self.setMinimumWidth(500)
        layout = QFormLayout(self)

        self.lang = lang_actual
        self.data_i18n = data_i18n

        # Datos específicos del idioma
        datos_idioma = data_i18n.get(lang_actual, {})
        titulo_actual = datos_idioma.get('titulo', '')
        subtitulo_actual = datos_idioma.get('subtitulo', '')

        self.input_titulo = QLineEdit(titulo_actual)
        self.input_subtitulo = QLineEdit(subtitulo_actual)

        # Datos Globales
        self.input_fecha = QLineEdit(data_event_info.get('fecha_evento', ''))
        self.input_hora = QLineEdit(data_event_info.get('hora_evento', ''))

        layout.addRow(f"Título ({lang_actual}):", self.input_titulo)
        layout.addRow(f"Subtítulo / Categoría ({lang_actual}):", self.input_subtitulo)

        linea = QWidget()
        linea.setFixedHeight(2)
        linea.setStyleSheet("background-color: #d4af37; margin: 10px 0;")
        layout.addRow(linea)

        layout.addRow("Fecha Global (AAAA-MM-DD):", self.input_fecha)
        layout.addRow("Hora Global (HH:MM):", self.input_hora)

        self.botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.botones.accepted.connect(self.accept)
        self.botones.rejected.connect(self.reject)
        layout.addRow(self.botones)

    def obtener_datos(self):
        # Actualizamos el diccionario del idioma específico
        if self.lang not in self.data_i18n:
            self.data_i18n[self.lang] = {}

        self.data_i18n[self.lang]['titulo'] = self.input_titulo.text()
        self.data_i18n[self.lang]['subtitulo'] = self.input_subtitulo.text()

        return {
            "i18n": self.data_i18n,
            "event_info": {
                "fecha_evento": self.input_fecha.text(),
                "hora_evento": self.input_hora.text()
            }
        }

# --- HILO DE DESCARGA ASÍNCRONA ---
class WorkerDescarga(QThread):
    imagen_descargada = Signal(int, QPixmap)

    def __init__(self, url, index):
        super().__init__()
        self.url = url
        self.index = index

    def run(self):
        try:
            req = urllib.request.Request(self.url, headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=2).read()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.imagen_descargada.emit(self.index, pixmap)
        except:
            pass

# --- GESTOR DE ENLACES INTELIGENTE ---
class DialogoEnlace(QDialog):
    def __init__(self, url_actual, lang, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Link Manager" if lang == "EN" else "Gestor de Enlaces")
        self.resize(450, 180)
        layout = QVBoxLayout(self)

        oscuro = is_dark_mode()

        if url_actual:
            lbl_info = QLabel("<b>Current link:</b>" if lang == "EN" else "<b>Enlace detectado en la selección:</b>")
            lbl_info.setStyleSheet("color: #d4af37; font-size: 13px;")
            layout.addWidget(lbl_info)

            lbl_actual = QLabel(url_actual)
            bg_color = "#222" if oscuro else "#ddd"
            text_color = "#aaa" if oscuro else "#333"
            lbl_actual.setStyleSheet(f"color: {text_color}; background-color: {bg_color}; padding: 5px; border-radius: 4px;")
            lbl_actual.setWordWrap(True)
            layout.addWidget(lbl_actual)

        t_nuevo = "<b>New link:</b> (Leave blank to remove)" if lang == "EN" else "<b>Nuevo enlace:</b> (Déjalo en blanco para eliminar el enlace actual)"
        lbl_nuevo = QLabel(t_nuevo)
        lbl_nuevo.setStyleSheet(f"color: {'white' if oscuro else 'black'}; margin-top: 10px;")
        layout.addWidget(lbl_nuevo)

        self.input_url = QLineEdit()
        self.input_url.setText(url_actual)
        self.input_url.setPlaceholderText("https://...")
        self.input_url.setStyleSheet("padding: 5px; font-size: 13px;")
        layout.addWidget(self.input_url)

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def get_url(self):
        return self.input_url.text().strip()

# --- VENTANA UNIFICADA PARA IMÁGENES Y VIDEOS ---
class SelectorElementos(QDialog):
    def __init__(self, elementos, tipo, lang, parent=None):
        super().__init__(parent)
        self.tipo = tipo
        self.lang = lang
        title = f"{tipo.capitalize()} Gallery" if lang == "EN" else f"Galería de {tipo.capitalize()}s"
        self.setWindowTitle(title)
        self.resize(900, 600)
        layout = QVBoxLayout(self)

        oscuro = is_dark_mode()

        txt_info = f"Select the {tipo} you want to replace:" if lang == "EN" else f"Selecciona el {tipo} que deseas reemplazar:"
        self.info_label = QLabel(txt_info)
        self.info_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #d4af37;")
        layout.addWidget(self.info_label)

        self.lista = QListWidget()
        self.lista.setSpacing(10)

        # Colores dinámicos adaptados al tema elegido
        bg_list = "#2b2b2b" if oscuro else "#ffffff"
        text_list = "#eee" if oscuro else "#111"
        border_list = "#444" if oscuro else "#ccc"

        self.lista.setStyleSheet(f"""
            QListWidget::item {{ padding: 10px; border-bottom: 1px solid {border_list}; color: {text_list}; background-color: {bg_list};}}
            QListWidget::item:selected {{ background-color: rgba(212, 175, 55, 0.4); border: 2px solid #d4af37; border-radius: 5px; color: {text_list};}}
        """)
        self.lista.itemSelectionChanged.connect(self.actualizar_inputs)
        layout.addWidget(self.lista)

        panel_edicion = QVBoxLayout()
        box_src = QHBoxLayout()
        lbl_src = "New URL:" if lang == "EN" else "Nuevo Enlace (URL):"
        label_src = QLabel(lbl_src)
        label_src.setFixedWidth(150)
        self.input_src = QLineEdit()
        box_src.addWidget(label_src)
        box_src.addWidget(self.input_src)
        panel_edicion.addLayout(box_src)

        self.input_alt = QLineEdit()
        if self.tipo == "imagen":
            box_alt = QHBoxLayout()
            lbl_alt = "New ALT Text:" if lang == "EN" else "Nuevo Texto (ALT):"
            label_alt = QLabel(lbl_alt)
            label_alt.setFixedWidth(150)
            box_alt.addWidget(label_alt)
            box_alt.addWidget(self.input_alt)
            panel_edicion.addLayout(box_alt)

        layout.addLayout(panel_edicion)

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.intentar_aceptar)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

        self.old_src, self.old_alt = "", ""
        self.final_new_src, self.final_new_alt = "", ""
        self.descargadores = []

        txt_noname = "Unnamed" if lang == "EN" else "Sin nombre"

        for i, item in enumerate(elementos):
            src = item.get('src', '')
            alt = item.get('alt', '')

            if self.tipo == "imagen":
                recorte = src.split('/')[-1] if src else ""
                if len(recorte) > 25: recorte = "..." + recorte[-25:]
                texto = f"ALT: {alt if alt else txt_noname}\nURL: {recorte}"
            else:
                texto = f"VIDEO URL: {src}"

            li = QListWidgetItem(texto)
            li.setData(Qt.UserRole, item)
            self.lista.addItem(li)

            if self.tipo == "imagen" and src.startswith("http"):
                w = WorkerDescarga(src, i)
                w.imagen_descargada.connect(self.set_icono)
                self.descargadores.append(w)
                w.start()

    def set_icono(self, index, pixmap):
        item = self.lista.item(index)
        if item:
            item.setIcon(QIcon(pixmap))
            self.lista.setIconSize(QSize(120, 120))

    def actualizar_inputs(self):
        sel = self.lista.selectedItems()
        if sel:
            data = sel[0].data(Qt.UserRole)
            self.old_src, self.old_alt = data.get('src', ''), data.get('alt', '')
            self.input_src.setText(self.old_src)
            if self.tipo == "imagen": self.input_alt.setText(self.old_alt)

    def intentar_aceptar(self):
        if not self.lista.selectedItems():
            msg = UI[self.lang]['msg_select_img'] if self.tipo == "imagen" else UI[self.lang]['msg_select_vid']
            return QMessageBox.warning(self, "!", msg)
        self.final_new_src = self.input_src.text().strip()
        self.final_new_alt = self.input_alt.text().strip()
        self.accept()


# --- EDITOR PRINCIPAL ---
class EditorEquspedia(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui_lang = "ES"
        self.resize(1200, 950)
        self.html_path = ""

        # --- DATOS INTERNOS (I18N) POR DEFECTO PARA EL LIENZO BILINGÜE ---
        self.meta_i18n = {
            "ES": {"titulo": "Nuevo Título", "subtitulo": "Categoría (ES)"},
            "EN": {"titulo": "New Title", "subtitulo": "Category (EN)"}
        }
        self.meta_event_info = {"fecha_evento": "", "hora_evento": ""}

        self.stack = QStackedWidget()
        self.browser = QWebEngineView()
        self.browser.loadFinished.connect(self.on_load_finished)

        # --- LIENZO EN BLANCO TIPO BLOGGER ---
        self.google_fonts_css = '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=Roboto:wght@400;700&family=Noto+Sans+JP:wght@400;700&family=Noto+Sans+Arabic:wght@400;700&family=Noto+Sans+SC:wght@400;700&display=swap" rel="stylesheet">'

        self.html_base_por_defecto = f"""<!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            {self.google_fonts_css}
            <style>
                body {{ font-family: 'Montserrat', sans-serif; padding: 40px; margin: 0 auto; max-width: 900px; }}
                .lang-block {{ display: none; }}
                .active-lang {{ display: block !important; }}
                #display-title {{ font-size: 2.5em; border-bottom: 1px solid #ccc; padding-bottom: 10px; margin-bottom: 5px; outline: none; }}
                #display-subtitle {{ color: #888; font-weight: normal; margin-top: 0; margin-bottom: 30px; outline: none; }}
                .content {{ outline: none; min-height: 500px; }}
            </style>
            <script>
                const EVENT_INFO = {{ fecha_evento: "{self.meta_event_info['fecha_evento']}", hora_evento: "{self.meta_event_info['hora_evento']}" }};
                const I18N = {{
                    ES: {{ titulo: "{self.meta_i18n['ES']['titulo']}", subtitulo: "{self.meta_i18n['ES']['subtitulo']}" }},
                    EN: {{ titulo: "{self.meta_i18n['EN']['titulo']}", subtitulo: "{self.meta_i18n['EN']['subtitulo']}" }}
                }};
                function init() {{ }}
            </script>
        </head>
        <body>
            <h1 id="display-title">Nuevo Título</h1>
            <h3 id="display-subtitle">Categoría (ES)</h3>

            <div class="lang-block active-lang" id="bloque-ES">
                <div class="content active">
                    <p>Escribe aquí...</p>
                </div>
            </div>

            <div class="lang-block" id="bloque-EN">
                <div class="content active">
                    <p>Start typing your content here...</p>
                </div>
            </div>
        </body>
        </html>"""

        self.browser.setHtml(self.html_base_por_defecto)

        self.editor_codigo = QPlainTextEdit()
        f = QFont("Monospace", 11); f.setStyleHint(QFont.TypeWriter); self.editor_codigo.setFont(f)
        self.stack.addWidget(self.browser)
        self.stack.addWidget(self.editor_codigo)
        self.setCentralWidget(self.stack)

        # BARRA DE SISTEMA E IDIOMAS
        self.toolbar_main = QToolBar("Principal")
        self.toolbar_main.setMovable(False); self.addToolBar(Qt.TopToolBarArea, self.toolbar_main)

        self.acc_theme = QAction("", self); self.acc_theme.triggered.connect(self.cambiar_tema_app)
        self.toolbar_main.addAction(self.acc_theme)

        self.acc_ui_toggle = QAction("", self); self.acc_ui_toggle.triggered.connect(self.toggle_ui_lang)
        self.toolbar_main.addAction(self.acc_ui_toggle); self.toolbar_main.addSeparator()

        self.acc_abrir = QAction("", self); self.acc_abrir.triggered.connect(self.abrir_archivo)
        self.toolbar_main.addAction(self.acc_abrir); self.toolbar_main.addSeparator()

        self.combo_idioma = QComboBox()
        self.combo_idioma.currentTextChanged.connect(self.cambiar_idioma)
        self.toolbar_main.addWidget(self.combo_idioma)

        self.acc_add_lang = QAction("", self); self.acc_add_lang.triggered.connect(self.agregar_nuevo_idioma)
        self.toolbar_main.addAction(self.acc_add_lang); self.toolbar_main.addSeparator()

        self.acc_img = QAction("", self); self.acc_img.triggered.connect(self.abrir_galeria_imagenes)
        self.toolbar_main.addAction(self.acc_img)

        self.acc_vid = QAction("", self); self.acc_vid.triggered.connect(self.abrir_galeria_videos)
        self.toolbar_main.addAction(self.acc_vid); self.toolbar_main.addSeparator()

        self.acc_meta = QAction("", self); self.acc_meta.triggered.connect(self.gestionar_metadatos_i18n)
        self.toolbar_main.addAction(self.acc_meta); self.toolbar_main.addSeparator()

        self.acc_vista = QAction("", self); self.acc_vista.triggered.connect(self.alternar_vista)
        self.toolbar_main.addAction(self.acc_vista)

        self.acc_save = QAction("", self); self.acc_save.triggered.connect(self.guardar_archivo)
        self.toolbar_main.addAction(self.acc_save)

        self.toolbar_main.addSeparator()

        self.acc_about = QAction("", self); self.acc_about.triggered.connect(self.mostrar_acerca_de)
        self.toolbar_main.addAction(self.acc_about)

        # BARRA DE FORMATO (CON TIPOGRAFÍA AVANZADA)
        self.toolbar_formato = QToolBar("Formato")
        self.toolbar_formato.setMovable(False); self.addToolBar(Qt.TopToolBarArea, self.toolbar_formato); self.insertToolBarBreak(self.toolbar_formato)

        self.combo_fuente = QFontComboBox()
        self.combo_fuente.setFixedWidth(180)
        self.combo_fuente.addItems(["Montserrat", "Roboto", "Noto Sans JP", "Noto Sans Arabic", "Noto Sans SC", "Arial", "Times New Roman", "Verdana", "Courier New"])
        self.combo_fuente.currentTextChanged.connect(lambda f: self.aplicar_comando('fontName', f))
        self.toolbar_formato.addWidget(self.combo_fuente)

        self.combo_tamanio = QComboBox()
        self.combo_tamanio.addItems(["1", "2", "3", "4", "5", "6", "7"])
        self.combo_tamanio.setCurrentIndex(2) # Tamaño 3 por defecto
        self.combo_tamanio.currentTextChanged.connect(lambda t: self.aplicar_comando('fontSize', t))
        self.toolbar_formato.addWidget(self.combo_tamanio)

        self.toolbar_formato.addSeparator()

        self.combo_bloque = QComboBox()
        self.combo_bloque.currentTextChanged.connect(self.cambiar_formato_bloque)
        self.toolbar_formato.addWidget(self.combo_bloque)

        self.toolbar_formato.addSeparator()

        self.acc_bold = QAction(QIcon.fromTheme("format-text-bold"), "B", self); self.acc_bold.triggered.connect(lambda: self.aplicar_comando('bold'))
        self.acc_italic = QAction(QIcon.fromTheme("format-text-italic"), "I", self); self.acc_italic.triggered.connect(lambda: self.aplicar_comando('italic'))
        self.acc_under = QAction(QIcon.fromTheme("format-text-underline"), "U", self); self.acc_under.triggered.connect(lambda: self.aplicar_comando('underline'))

        self.toolbar_formato.addActions([self.acc_bold, self.acc_italic, self.acc_under])
        self.toolbar_formato.addSeparator()

        self.acc_left = QAction(QIcon.fromTheme("format-justify-left"), "Izq", self); self.acc_left.triggered.connect(lambda: self.aplicar_comando('justifyLeft'))
        self.acc_center = QAction(QIcon.fromTheme("format-justify-center"), "Cen", self); self.acc_center.triggered.connect(lambda: self.aplicar_comando('justifyCenter'))
        self.acc_right = QAction(QIcon.fromTheme("format-justify-right"), "Der", self); self.acc_right.triggered.connect(lambda: self.aplicar_comando('justifyRight'))
        self.acc_just = QAction(QIcon.fromTheme("format-justify-fill"), "Jus", self); self.acc_just.triggered.connect(lambda: self.aplicar_comando('justifyFull'))

        self.toolbar_formato.addActions([self.acc_left, self.acc_center, self.acc_right, self.acc_just])
        self.toolbar_formato.addSeparator()

        self.acc_color = QAction(QIcon.fromTheme("format-text-color"), "Color", self); self.acc_color.triggered.connect(self.escoger_color)
        self.toolbar_formato.addAction(self.acc_color)

        self.acc_bullet = QAction(QIcon.fromTheme("format-list-unordered"), "Viñeta", self); self.acc_bullet.triggered.connect(lambda: self.aplicar_comando('insertUnorderedList'))
        self.toolbar_formato.addAction(self.acc_bullet)

        self.acc_num = QAction(QIcon.fromTheme("format-list-ordered"), "Num", self); self.acc_num.triggered.connect(lambda: self.aplicar_comando('insertOrderedList'))
        self.toolbar_formato.addAction(self.acc_num)

        self.acc_quote = QAction(QIcon.fromTheme("format-text-blockquote"), "Cita", self); self.acc_quote.triggered.connect(lambda: self.aplicar_comando('formatBlock', '<blockquote>'))
        self.toolbar_formato.addAction(self.acc_quote); self.toolbar_formato.addSeparator()

        self.acc_link = QAction(QIcon.fromTheme("insert-link"), "Link", self); self.acc_link.triggered.connect(self.insertar_enlace)
        self.toolbar_formato.addAction(self.acc_link)

        # TIMER PARA AUTO-DETECCIÓN DE LETRA Y TAMAÑO
        self.timer_deteccion = QTimer()
        self.timer_deteccion.timeout.connect(self.detectar_formato_actual)
        self.timer_deteccion.start(500)

        # Iniciar UI y Tema
        self.actualizar_textos_ui()
        self.forzar_paleta_colores()

    # --- FUNCIÓN: MOSTRAR ACERCA DE ---
    def mostrar_acerca_de(self):
        QMessageBox.about(self, UI[self.ui_lang]['about_title'], UI[self.ui_lang]['about_text'])

    # --- FUNCIÓN: EXTRACTOR I18N ---
    def extraer_datos_script(self, html_content):
        m_fecha = re.search(r'fecha_evento:\s*"(.*?)"', html_content)
        m_hora = re.search(r'hora_evento:\s*"(.*?)"', html_content)
        if m_fecha: self.meta_event_info['fecha_evento'] = m_fecha.group(1)
        if m_hora: self.meta_event_info['hora_evento'] = m_hora.group(1)

        self.meta_i18n = {}
        bloques_idioma = re.findall(r'([A-Z]{2}):\s*\{(.*?)\}', html_content, re.DOTALL)
        for lang, contenido in bloques_idioma:
            titulo = re.search(r'titulo:\s*"(.*?)"', contenido)
            subtitulo = re.search(r'subtitulo:\s*"(.*?)"', contenido)
            self.meta_i18n[lang] = {
                'titulo': titulo.group(1) if titulo else "",
                'subtitulo': subtitulo.group(1) if subtitulo else ""
            }

    # --- FUNCIÓN: EDICIÓN Y SINCRONIZACIÓN DE METADATOS ---
    def gestionar_metadatos_i18n(self):
        lang_actual = self.combo_idioma.currentText()
        if not lang_actual:
            return QMessageBox.warning(self, "Atención", "Selecciona un idioma en la barra primero.")

        diag = DialogoMetadata(lang_actual, self.meta_i18n, self.meta_event_info, self)
        if diag.exec():
            nuevos = diag.obtener_datos()
            self.meta_i18n = nuevos['i18n']
            self.meta_event_info = nuevos['event_info']

            tit_nuevo = self.meta_i18n[lang_actual]['titulo']
            subt_nuevo = self.meta_i18n[lang_actual]['subtitulo']
            fecha = self.meta_event_info['fecha_evento']
            hora = self.meta_event_info['hora_evento']

            js_update = f"""
            if(document.getElementById('display-title')) document.getElementById('display-title').innerText = "{tit_nuevo}";
            if(document.getElementById('display-subtitle')) document.getElementById('display-subtitle').innerText = "{subt_nuevo}";
            if(typeof EVENT_INFO !== 'undefined') {{
                EVENT_INFO.fecha_evento = "{fecha}";
                EVENT_INFO.hora_evento = "{hora}";
            }}
            if(typeof I18N !== 'undefined' && I18N['{lang_actual}']) {{
                I18N['{lang_actual}'].titulo = "{tit_nuevo}";
                I18N['{lang_actual}'].subtitulo = "{subt_nuevo}";
            }}
            if(typeof init === 'function') init();
            """
            self.browser.page().runJavaScript(js_update)

    # --- AUTO DETECCIÓN DE FORMATO ---
    def detectar_formato_actual(self):
        if self.stack.currentIndex() != 0: return

        js = """
        (function(){
            var block = document.queryCommandValue('formatBlock') || "p";
            return JSON.stringify({
                font: document.queryCommandValue('fontName').replace(/['"]/g, ""),
                size: document.queryCommandValue('fontSize'),
                block: block.toLowerCase()
            });
        })();
        """
        self.browser.page().runJavaScript(js, self._actualizar_combos_segun_cursor)

    def _actualizar_combos_segun_cursor(self, json_data):
        if not json_data: return
        try:
            data = json.loads(json_data)
            self.combo_fuente.blockSignals(True)
            self.combo_tamanio.blockSignals(True)
            self.combo_bloque.blockSignals(True)

            index_f = self.combo_fuente.findText(data['font'], Qt.MatchContains)
            if index_f >= 0: self.combo_fuente.setCurrentIndex(index_f)

            index_t = self.combo_tamanio.findText(str(data['size']))
            if index_t >= 0: self.combo_tamanio.setCurrentIndex(index_t)

            block = data.get('block', 'p')
            index_b = self.combo_bloque.findData(block)
            if index_b >= 0: self.combo_bloque.setCurrentIndex(index_b)

            self.combo_fuente.blockSignals(False)
            self.combo_tamanio.blockSignals(False)
            self.combo_bloque.blockSignals(False)
        except: pass

    # --- LÓGICA DE TEMAS Y COLORES ---
    def cambiar_tema_app(self):
        global THEME_MODE
        if THEME_MODE == "system": THEME_MODE = "dark"
        elif THEME_MODE == "dark": THEME_MODE = "light"
        else: THEME_MODE = "system"

        self.actualizar_textos_ui()
        self.forzar_paleta_colores()

    def forzar_paleta_colores(self):
        app = QApplication.instance()
        oscuro = is_dark_mode()

        if THEME_MODE == "system":
            app.setPalette(app.style().standardPalette())
        else:
            p = QPalette()
            if oscuro:
                p.setColor(QPalette.Window, QColor(43, 43, 43))
                p.setColor(QPalette.WindowText, Qt.white)
                p.setColor(QPalette.Base, QColor(30, 30, 30))
                p.setColor(QPalette.AlternateBase, QColor(43, 43, 43))
                p.setColor(QPalette.ToolTipBase, Qt.white)
                p.setColor(QPalette.ToolTipText, Qt.white)
                p.setColor(QPalette.Text, Qt.white)
                p.setColor(QPalette.Button, QColor(53, 53, 53))
                p.setColor(QPalette.ButtonText, Qt.white)
                p.setColor(QPalette.Link, QColor(42, 130, 218))
                p.setColor(QPalette.Highlight, QColor(212, 175, 55))
                p.setColor(QPalette.HighlightedText, Qt.black)
            else:
                p.setColor(QPalette.Window, QColor(240, 240, 240))
                p.setColor(QPalette.WindowText, Qt.black)
                p.setColor(QPalette.Base, Qt.white)
                p.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
                p.setColor(QPalette.ToolTipBase, Qt.black)
                p.setColor(QPalette.ToolTipText, Qt.black)
                p.setColor(QPalette.Text, Qt.black)
                p.setColor(QPalette.Button, QColor(220, 220, 220))
                p.setColor(QPalette.ButtonText, Qt.black)
                p.setColor(QPalette.Link, QColor(42, 130, 218))
                p.setColor(QPalette.Highlight, QColor(212, 175, 55))
                p.setColor(QPalette.HighlightedText, Qt.white)
            app.setPalette(p)

        if oscuro:
            self.editor_codigo.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; padding: 10px; border: none;")
        else:
            self.editor_codigo.setStyleSheet("background-color: #ffffff; color: #111111; padding: 10px; border: 1px solid #ccc;")

    def changeEvent(self, event):
        if event.type() == QEvent.PaletteChange and THEME_MODE == "system":
            self.forzar_paleta_colores()
        super().changeEvent(event)

    def actualizar_textos_ui(self):
        t = UI[self.ui_lang]
        self.setWindowTitle(t['title'])
        self.acc_ui_toggle.setText(t['toggle_btn'])
        self.acc_abrir.setText(t['open'])
        self.acc_add_lang.setText(t['add_lang'])
        self.acc_img.setText(t['img_gal'])
        self.acc_vid.setText(t['vid_gal'])
        self.acc_meta.setText(t['meta_edit'])
        self.acc_about.setText(t['about_btn'])

        if THEME_MODE == "system":
            self.acc_theme.setText("🌗 Auto")
        elif THEME_MODE == "dark":
            self.acc_theme.setText("🌙 Oscuro" if self.ui_lang == "ES" else "🌙 Dark")
        else:
            self.acc_theme.setText("☀️ Claro" if self.ui_lang == "ES" else "☀️ Light")

        if self.stack.currentIndex() == 0:
            self.acc_vista.setText(t['code_mode'])
        else:
            self.acc_vista.setText(t['vis_mode'])

        self.acc_save.setText(t['save'])

        self.combo_bloque.blockSignals(True)
        self.combo_bloque.clear()
        self.combo_bloque.addItem(t['block_normal'], "p")
        self.combo_bloque.addItem(t['block_h1'], "h1")
        self.combo_bloque.addItem(t['block_h2'], "h2")
        self.combo_bloque.addItem(t['block_h3'], "h3")
        self.combo_bloque.blockSignals(False)

        self.acc_left.setToolTip(t['align_left'])
        self.acc_center.setToolTip(t['align_center'])
        self.acc_right.setToolTip(t['align_right'])
        self.acc_just.setToolTip(t['align_just'])
        self.acc_color.setToolTip(t['color'])
        self.acc_bullet.setToolTip(t['bullet'])
        self.acc_num.setToolTip(t['num'])
        self.acc_quote.setToolTip(t['quote'])
        self.acc_link.setToolTip(t['link'])

    def toggle_ui_lang(self):
        self.ui_lang = "EN" if self.ui_lang == "ES" else "ES"
        self.actualizar_textos_ui()

    def cambiar_formato_bloque(self, texto):
        tag = self.combo_bloque.currentData()
        if tag:
            # TRUCO WEBKIT: Fuerza el cambio a "Texto Normal" o "Título" aunque borres toda la línea
            js_force = f"""
            (function() {{
                var sel = window.getSelection();
                if (sel.rangeCount > 0 && sel.getRangeAt(0).collapsed) {{
                    document.execCommand('insertText', false, 'x');
                    document.execCommand('formatBlock', false, '<{tag}>');
                    document.execCommand('delete', false, null);
                }} else {{
                    document.execCommand('formatBlock', false, '<{tag}>');
                }}
            }})();
            """
            self.browser.page().runJavaScript(js_force)

    # --- LÓGICA CORE ---
    def abrir_archivo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select HTML" if self.ui_lang == "EN" else "Seleccionar Plantilla", "", "HTML (*.html)")
        if path:
            self.html_path = path
            with open(path, 'r', encoding='utf-8') as f:
                c = f.read()
                self.editor_codigo.setPlainText(c)
                self.browser.setHtml(c)

            self.extraer_datos_script(c)
            self.stack.setCurrentIndex(0)

    def on_load_finished(self, ok):
        if ok:
            self.browser.page().runJavaScript("document.designMode = 'on';")
            js_langs = """
            (function(){
                var res = [];
                var b = document.querySelectorAll('.lang-block');
                for(var i=0; i<b.length; i++){
                    if(b[i].id && b[i].id.indexOf('bloque-') !== -1){
                        res.push(b[i].id.replace('bloque-', ''));
                    }
                }
                return JSON.stringify(res);
            })();
            """
            self.browser.page().runJavaScript(js_langs, self._set_idiomas)

    def _set_idiomas(self, json_data):
        if json_data:
            try:
                langs = json.loads(json_data)
                self.combo_idioma.blockSignals(True)
                self.combo_idioma.clear()
                self.combo_idioma.addItems(langs)
                self.combo_idioma.blockSignals(False)
                if langs: self.cambiar_idioma(self.combo_idioma.currentText())
            except Exception: pass

    def cambiar_idioma(self, lang):
        if not lang: return
        js = f"document.querySelectorAll('.lang-block').forEach(b => b.classList.remove('active-lang')); var t = document.getElementById('bloque-{lang}'); if(t) t.classList.add('active-lang');"
        self.browser.page().runJavaScript(js)

        js_update_bar = f"""
        if(typeof I18N !== 'undefined' && I18N['{lang}']) {{
            if(document.getElementById('display-title')) document.getElementById('display-title').innerText = I18N['{lang}'].titulo;
            if(document.getElementById('display-subtitle')) document.getElementById('display-subtitle').innerText = I18N['{lang}'].subtitulo;

            /* Traducir pestañas si existen */
            for(let i=0; i<4; i++) {{
                const btn = document.getElementById('tab'+i);
                if(btn && I18N['{lang}'].tabs && I18N['{lang}'].tabs[i]) btn.innerText = I18N['{lang}'].tabs[i];
            }}
            /* Traducir Navbar */
            const navLinks = document.getElementById('navbar-links') ? document.getElementById('navbar-links').getElementsByTagName('a') : [];
            for(let i=0; i < navLinks.length; i++) {{
                if(I18N['{lang}'].cinta && I18N['{lang}'].cinta[i]) navLinks[i].innerText = I18N['{lang}'].cinta[i];
            }}
            /* Traducir Footer */
            if(document.getElementById('sep-h') && I18N['{lang}'].pie && I18N['{lang}'].pie[0]) document.getElementById('sep-h').innerText = I18N['{lang}'].pie[0];
            if(document.getElementById('sep-u') && I18N['{lang}'].pie && I18N['{lang}'].pie[1]) document.getElementById('sep-u').innerText = I18N['{lang}'].pie[1];
            if(document.getElementById('footer-copyright') && I18N['{lang}'].copyright) document.getElementById('footer-copyright').innerText = I18N['{lang}'].copyright;

            if(typeof calculateLocalTime === 'function') calculateLocalTime('{lang}');
        }}
        """
        self.browser.page().runJavaScript(js_update_bar)

    def agregar_nuevo_idioma(self):
        curr = self.combo_idioma.currentText()
        if not curr: return

        txt_title = "Add Language" if self.ui_lang == "EN" else "Nuevo Idioma"
        txt_prompt = f"Clone '{curr}' to new language (e.g. IT, DE):" if self.ui_lang == "EN" else f"Clonar '{curr}'. Código del nuevo idioma (Ej: IT, DE):"

        nuevo, ok = QInputDialog.getText(self, txt_title, txt_prompt)
        if ok and nuevo:
            nuevo = nuevo.strip().upper()
            js = f"""
            (function(){{
                var src = document.getElementById('bloque-{curr}');
                if(!src) return false;
                var clone = src.cloneNode(true);
                clone.id = 'bloque-{nuevo}';
                clone.classList.remove('active-lang');
                src.parentNode.appendChild(clone);
                return true;
            }})();
            """
            self.browser.page().runJavaScript(js, lambda res: self._idioma_creado(res, nuevo))

    def _idioma_creado(self, success, nuevo):
        if success:
            self.combo_idioma.addItem(nuevo)
            self.combo_idioma.setCurrentText(nuevo)
            QMessageBox.information(self, UI[self.ui_lang]['msg_success'], f"Block {nuevo} created!" if self.ui_lang == "EN" else f"Bloque {nuevo} creado.")

    def alternar_vista(self):
        if self.stack.currentIndex() == 0: self.browser.page().toHtml(self._sincronizar_a_codigo)
        else: self.browser.setHtml(self.editor_codigo.toPlainText()); self.stack.setCurrentIndex(0); self.actualizar_textos_ui()

    def _sincronizar_a_codigo(self, html):
        self.editor_codigo.setPlainText(html.replace('designMode="on"', '')); self.stack.setCurrentIndex(1); self.actualizar_textos_ui()

    # --- LÓGICA DE GALERÍAS ---
    def abrir_galeria_imagenes(self):
        if not self.html_path and self.stack.currentIndex() == 0 and not "<html>" in self.editor_codigo.toPlainText(): return QMessageBox.warning(self, "!", UI[self.ui_lang]['msg_open_first'])
        js = """
        (function(){
            var r = []; var imgs = document.querySelectorAll('img');
            for(var i=0; i<imgs.length; i++){
                var src = imgs[i].getAttribute('src'); var alt = imgs[i].getAttribute('alt') || "";
                if(src){
                    var existe = false; for(var j=0; j<r.length; j++) { if(r[j].src === src) { existe = true; break; } }
                    if(!existe) r.push({'src': src, 'alt': alt});
                }
            }
            return JSON.stringify(r);
        })();
        """
        self.browser.page().runJavaScript(js, lambda data: self._abrir_galeria(data, "imagen"))

    def abrir_galeria_videos(self):
        if not self.html_path and self.stack.currentIndex() == 0 and not "<html>" in self.editor_codigo.toPlainText(): return QMessageBox.warning(self, "!", UI[self.ui_lang]['msg_open_first'])
        js = """
        (function(){
            var r = []; var vids = document.querySelectorAll('iframe');
            for(var i=0; i<vids.length; i++){
                var src = vids[i].getAttribute('src');
                if(src){
                    var existe = false; for(var j=0; j<r.length; j++) { if(r[j].src === src) { existe = true; break; } }
                    if(!existe) r.push({'src': src});
                }
            }
            return JSON.stringify(r);
        })();
        """
        self.browser.page().runJavaScript(js, lambda data: self._abrir_galeria(data, "video"))

    def _abrir_galeria(self, json_data, tipo):
        if not json_data: return
        items = json.loads(json_data)
        if not items:
            msg = UI[self.ui_lang]['msg_no_img'] if tipo == "imagen" else UI[self.ui_lang]['msg_no_vid']
            return QMessageBox.warning(self, "!", msg)

        d = SelectorElementos(items, tipo, self.ui_lang, self)
        if d.exec():
            old_src = d.old_src
            new_src = d.final_new_src

            if tipo == "imagen":
                old_alt = d.old_alt
                new_alt = d.final_new_alt
                js = f"""
                (function(){{
                    var c = 0; var els = document.querySelectorAll('img');
                    for(var i=0; i<els.length; i++){{
                        if(els[i].getAttribute('src') === '{old_src}') {{
                            if('{new_src}' !== '{old_src}' && '{new_src}' !== '') els[i].setAttribute('src', '{new_src}');
                            if('{new_alt}' !== '{old_alt}' && '{new_alt}' !== '') els[i].setAttribute('alt', '{new_alt}');
                            c++;
                        }}
                    }}
                    return c;
                }})();
                """
            else:
                js = f"""
                (function(){{
                    var c = 0; var els = document.querySelectorAll('iframe');
                    for(var i=0; i<els.length; i++){{
                        if(els[i].getAttribute('src') === '{old_src}') {{
                            if('{new_src}' !== '{old_src}' && '{new_src}' !== '') els[i].setAttribute('src', '{new_src}');
                            c++;
                        }}
                    }}
                    return c;
                }})();
                """
            self.browser.page().runJavaScript(js, lambda res: QMessageBox.information(self, UI[self.ui_lang]['msg_success'], UI[self.ui_lang]['msg_updated'].format(res)))

    # --- FORMATO ---
    def aplicar_comando(self, cmd, value=None):
        self.browser.page().runJavaScript(f"document.execCommand('{cmd}', false, {json.dumps(value) if value else 'null'});")

    def escoger_color(self):
        color = QColorDialog.getColor()
        if color.isValid(): self.aplicar_comando('foreColor', color.name())

    def insertar_enlace(self):
        js_get_current_link = """
        (function() {
            var node = document.getSelection().anchorNode;
            while (node && node.nodeName !== 'A') { node = node.parentNode; }
            if (node && node.nodeName === 'A') { return node.href; }
            return "";
        })();
        """
        self.browser.page().runJavaScript(js_get_current_link, self._procesar_dialogo_enlace)

    def _procesar_enlace(self, u):
        d = DialogoEnlace(u, self.ui_lang, self)
        if d.exec():
            n = d.get_url()
            if n: self.aplicar_comando('createLink', n)
            elif u: self.aplicar_comando('unlink')

    # --- GUARDADO INTELIGENTE ---
    def guardar_archivo(self):
        if not self.html_path:
            path_guardar, _ = QFileDialog.getSaveFileName(self, "Save As..." if self.ui_lang == "EN" else "Guardar como...", "", "HTML (*.html)")
            if path_guardar:
                self.html_path = path_guardar
            else:
                return

        if self.stack.currentIndex() == 0: self.browser.page().toHtml(self._procesar_y_guardar_final)
        else: self._escribir_al_disco(self.editor_codigo.toPlainText())

    def _procesar_y_guardar_final(self, html):
        html = re.sub(r'fecha_evento:\s*".*?"', f'fecha_evento: "{self.meta_event_info["fecha_evento"]}"', html)
        html = re.sub(r'hora_evento:\s*".*?"', f'hora_evento: "{self.meta_event_info["hora_evento"]}"', html)

        for lang, datos in self.meta_i18n.items():
            patron_titulo = r'(' + lang + r':\s*\{.*?titulo:\s*").*?(")'
            patron_distancia = r'(' + lang + r':\s*\{.*?subtitulo:\s*").*?(")'

            html = re.sub(patron_titulo, r'\g<1>' + datos['titulo'] + r'\g<2>', html, flags=re.DOTALL)
            html = re.sub(patron_distancia, r'\g<1>' + datos['subtitulo'] + r'\g<2>', html, flags=re.DOTALL)

        if self.google_fonts_css not in html:
            html = html.replace('<head>', f'<head>\n    {self.google_fonts_css}')

        self._escribir_al_disco(html)

    def _escribir_al_disco(self, html):
        with open(self.html_path, 'w', encoding='utf-8') as f: f.write(html.replace('designMode="on"', ''))
        QMessageBox.information(self, UI[self.ui_lang]['msg_success'], UI[self.ui_lang]['msg_saved'])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ex = EditorEquspedia()

    # --- ICONO DE LA APLICACIÓN ---
    icono = QIcon(ruta_recurso("icono.png"))
    app.setWindowIcon(icono)   # Icono en la barra de tareas / dock
    ex.setWindowIcon(icono)    # Icono en la ventana principal

    ex.show()
    sys.exit(app.exec())
