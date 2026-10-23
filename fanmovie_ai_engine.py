import os
import json
import random

# ---------------------------------------------------------
# FANMOVIE AI ENGINE - ARQUITECTURA DE 3 DINÁMICAS
# ---------------------------------------------------------

class FanMovieEngine:
    def __init__(self, ruta_crudos):
        self.ruta_crudos = ruta_crudos
        self.base_datos_tomas = self._escanear_y_etiquetar_crudos()

    def _escanear_y_etiquetar_crudos(self):
        print(f"[🤖 MOTOR] Indexando crudos en: {self.ruta_crudos}...")
        archivos = [f for f in os.listdir(self.ruta_crudos) if f.endswith('.mp4')]
        tomas = []
        escalas = ["plano_general", "plano_medio", "primer_plano", "detalle"]
        
        # Simulamos 3 filmmakers
        filmmakers = [
            {"usuario": "yair", "ig": "@yairsafe"},
            {"usuario": "amigo1", "ig": "@amigo_uno"},
            {"usuario": "amigo2", "ig": "@amigo_dos"}
        ]

        for archivo in archivos:
            autor = random.choice(filmmakers)
            tomas.append({
                "archivo": archivo,
                "autor": autor["usuario"],
                "ig_autor": autor["ig"],
                "duracion": round(random.uniform(2.0, 10.0), 1),
                "escala": random.choice(escalas),
                "puntaje_impacto": random.randint(1, 10) # 10 = Toma épica para hook
            })
        return tomas

    # ==========================================
    # DINÁMICA 1: RECAP DEL USUARIO (LOST TAPE)
    # ==========================================
    def generar_recap_usuario(self, usuario):
        print(f"\n[📼 DINÁMICA 1] Generando Recap Automático (Lost Tape) para: {usuario}")
        tomas_usuario = [t for t in self.base_datos_tomas if t['autor'] == usuario]
        
        if not tomas_usuario:
            return "No hay tomas suficientes."

        # Orden narrativo: Mejor toma al principio (Hook), resto al medio, segunda mejor al final
        tomas_ordenadas = sorted(tomas_usuario, key=lambda x: x['puntaje_impacto'], reverse=True)
        hook = tomas_ordenadas.pop(0)
        cierre = tomas_ordenadas.pop(0) if tomas_ordenadas else hook
        
        timeline_usuario = [hook] + tomas_ordenadas + [cierre]
        
        print(f" -> Hook seleccionado: {hook['archivo']} (Impacto: {hook['puntaje_impacto']})")
        print(" -> Aplicando comando FFmpeg: [Filtro VHS + Glitch Transitions + Formato 9:16]")
        print(" -> 📤 Render finalizado. MP4 enviado al perfil del usuario.")
        return timeline_usuario

    # ==========================================
    # DINÁMICA 2: AFTERMOVIE OFICIAL (ADMIN)
    # ==========================================
    def generar_aftermovie_admin(self):
        print(f"\n[🎬 DINÁMICA 2] Generando Aftermovie General (Pool completo)")
        
        # Seleccionar las mejores tomas de TODOS los filmmakers
        mejores_tomas = sorted(self.base_datos_tomas, key=lambda x: x['puntaje_impacto'], reverse=True)[:15]
        
        # Extraer créditos para redes sociales
        creditos_ig = list(set([t['ig_autor'] for t in mejores_tomas]))
        
        print(" -> Timeline multicámara armado con ritmo dinámico (1 seg por plano).")
        print(f" -> 📱 Créditos recolectados para Copy de Instagram: {' '.join(creditos_ig)}")
        return mejores_tomas

    # ==========================================
    # DINÁMICA 3: EXPORTACIÓN XML (HUMAN-IN-THE-LOOP)
    # ==========================================
    def exportar_xml_premiere(self, timeline):
        print(f"\n[⚙️ DINÁMICA 3] Exportando Proyecto para Premiere Pro...")
        
        # Simulación de estructura XML (Final Cut Pro XML format)
        xml_output = "<?xml version='1.0' encoding='UTF-8'?>\n<xmeml version='5'>\n  <sequence>\n"
        for i, clip in enumerate(timeline):
            xml_output += f"    <clip id='{i}' src='{clip['archivo']}' in='0' out='{clip['duracion']}' />\n"
        xml_output += "  </sequence>\n</xmeml>"
        
        nombre_archivo = "FanMovie_Export_Premiere.xml"
        with open(nombre_archivo, "w") as f:
            f.write(xml_output)
            
        print(f" -> 📥 Archivo XML generado: {nombre_archivo}. Listo para importar y pulir a mano.")
        return nombre_archivo

# --- PRUEBA DEL MOTOR ---
if __name__ == '__main__':
    # Crear carpeta y archivos de prueba
    carpeta = "crudos_palermo"
    os.makedirs(carpeta, exist_ok=True)
    for i in range(1, 21):
        open(os.path.join(carpeta, f"clip_{i}.mp4"), 'w').close()

    # Inicializar motor
    motor = FanMovieEngine(carpeta)
    
    # Ejecutar las 3 dinámicas
    motor.generar_recap_usuario("yair")
    timeline_oficial = motor.generar_aftermovie_admin()
    motor.exportar_xml_premiere(timeline_oficial)
