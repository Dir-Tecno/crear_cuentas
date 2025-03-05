import pandas as pd
import numpy as np
import streamlit as st

# Definimos las reglas como un DataFrame
rules_data = {
    'Campo': [
        'TIPO DE REGISTRO', 'SUCURSAL', 'MONEDA', 'TIPO DOCUMENTO', 'NRO DOCUMENTO',
        'CLAVE FISCAL', 'NRO CLAVE FISCAL', 'TIPO CUENTA', 'NRO CUENTA', 'FECHA ALTA',
        'PRIMER APELLIDO', 'SEGUNDO APELLIDO', 'PRIMER NOMBRE', 'SEGUNDO NOMBRE',
        'CONDICION IVA', 'DOMICILIO PARTICULAR', 'NRO DOMICILIO', 'PISO', 'DEPARTAMENTO',
        'BARRIO', 'LOCALIDAD', 'CODIGO PROVINCIA', 'CODIGO POSTAL', 'CODIGO POSTAL EXTENDIDO',
        'PREF. TEL PARTICULAR', 'TEL. PARTICULAR', 'PREF. TEL CEL', 'TEL MOVIL',
        'DOMICILIO COMERCIAL', 'NRO DOMICILIO COMERCIAL', 'PISO COMERCIAL',
        'DEPARTAMENTO COMERCIAL', 'BARRIO COMERCIAL', 'LOCALIDAD COMERCIAL',
        'COD. PROV. COMERC', 'COD POSTAL COMERCIAL', 'COD POSTAL EXTENDIDO COMERC',
        'PREF. TEL COMERCIAL', 'TELEFONO COMERCIAL', 'FECHA NACIMIENTO', 'ESTADO CIVIL',
        'RESIDENTE', 'SEXO', 'NACIONALIDAD', 'EMAIL', 'TIPO PERSONA', 'COD. ACT. BCRA',
        'COD. NAT. JURIDICA', 'PRIMER APELLIDO CONYUGE', 'SEGUNDO APELLIDO CONYUGE',
        'PRIMER NOMBRE CONYUGE', 'SEGUNDO NOMBRE CONYUGE', 'SEXO CONYUGE',
        'TIPO DOC CONYUGE', 'NRO DOC CONYUGE', 'CUIT CONYUGE', 'FECHA NACIMIENTO CONYUGE',
        'NACIONALIDAD CONYUGE', 'NRO EMPRESA', 'TIPO CONVENIO', 'VALIDA NOMBRE',
        'NOMBRE CLIENTE SEGÚN PATRON', 'FILLER', 'TIPO SOLICITUD', 'CBU', 'FILLER 2',
        'DATOS PARA EMPRESA', 'MOTIVO DEL ERROR 1', 'MOTIVO DEL ERROR 2',
        'MOTIVO DEL ERROR 3', 'MOTIVO DEL ERROR 4', 'MOTIVO DEL ERROR 5',
        'MOTIVO DEL ERROR 6', 'MOTIVO DEL ERROR 7'
    ],
    'Total': [
        1, 5, 2, 3, 11, 3, 11, 2, 9, 8, 15, 15, 15, 15, 2, 30, 5, 2, 3, 30, 30,
        3, 5, 8, 5, 11, 5, 11, 30, 5, 2, 3, 30, 30, 3, 5, 8, 5, 11, 8, 4, 1, 1,
        3, 30, 1, 5, 3, 15, 15, 15, 15, 1, 3, 11, 11, 8, 3, 5, 3, 1, 30, 409, 2,
        22, 330, 21, 5, 5, 5, 5, 5, 5, 5
    ],
    'Tipo': [
        'A', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A', 'A', 'A', 'A',
        'N', 'A', 'N', 'N', 'A', 'A', 'A', 'N', 'N', 'A', 'A', 'A', 'A', 'A',
        'A', 'N', 'N', 'A', 'A', 'A', 'N', 'N', 'A', 'A', 'N', 'N', 'N', 'A',
        'A', 'N', 'A', 'A', 'N', 'N', 'A', 'A', 'A', 'A', 'A', 'N', 'N', 'N',
        'N', 'N', 'N', 'N', 'A', 'A', 'A', 'N', 'A', 'A', 'A', 'A', 'A', 'A',
        'A', 'A', 'A', 'A'
    ]
}

rules_df = pd.DataFrame(rules_data)

def extract_fields(file, rules_df):
    data = []
    
    try:
        # Asegurarnos de que estamos leyendo el archivo correctamente
        if hasattr(file, 'read'):
            # Si es un objeto de archivo (como el que viene de st.file_uploader)
            content = file.read().decode('latin1').splitlines()
        else:
            # Si es una ruta de archivo
            with open(file, 'r', encoding='latin1') as f:
                content = f.readlines()
        
        # Procesar cada línea
        for line_number, line in enumerate(content, 1):
            line = line.rstrip('\n\r')  # Eliminar saltos de línea
            
            if len(line.strip()) == 0:  # Ignorar líneas vacías
                continue
                
            if len(line) < sum(rules_df['Total']):
                print(f"Advertencia: Línea {line_number} ignorada por longitud insuficiente ({len(line)} caracteres)")
                continue
            
            extracted = {}
            current_position = 0
            
            # Usar rules_df para extraer los campos
            for _, rule in rules_df.iterrows():
                field_name = rule['Campo']
                length = rule['Total']
                # Extraer el campo y eliminar espacios en blanco
                field_value = line[current_position:current_position + length].strip()
                extracted[field_name] = field_value
                current_position += length
            
            data.append(extracted)
        
        if not data:
            raise ValueError("No se pudieron extraer datos del archivo. Verifique el formato del archivo .hab")
            
        return pd.DataFrame(data)
        
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")
        raise


def format_data(data_df, rules_df):
    # Reemplazar caracteres \xA0 por espacios en el DataFrame
    data_df = data_df.replace(to_replace='\xa0', value=' ', regex=True)
    
    formatted_lines = []
    
    for _, row in data_df.iterrows():
        line = ""
        for _, rule in rules_df.iterrows():
            field_name = rule['Campo']
            total_length = rule['Total']
            field_type = rule['Tipo']
            value = row.get(field_name, np.nan)
            
            if pd.isna(value):
                formatted_value = ""
            else:
                formatted_value = str(value)
            
            # Pad the field based on its type
            if field_type == 'A':  # Alphanumeric, pad with spaces
                formatted_value = formatted_value.rjust(total_length)
            elif field_type == 'N':  # Numeric, pad with zeros
                formatted_value = formatted_value.zfill(total_length)
            
            # Truncate to the exact length
            formatted_value = formatted_value[:total_length]
            line += formatted_value

        # Append the formatted line with CRLF as line ending
        formatted_lines.append(line)
    
    return formatted_lines

def correct_suffixes(df):
    # Lista de prefijos a buscar (con ceros para la comparación)
    prefijos = ['0351', '0358', '0353']
    # Mapa de prefijos sin ceros para guardar
    prefijos_sin_ceros = {'0351': '351', '0358': '358', '0353': '353'}
    
    # Pares de columnas a procesar (teléfono y su prefijo correspondiente)
    columnas = [
        ('TEL. PARTICULAR', 'PREF. TEL PARTICULAR'),
        ('TEL MOVIL', 'PREF. TEL CEL'),
        ('TELEFONO COMERCIAL', 'PREF. TEL COMERCIAL')
    ]
    
    # Crear una copia del DataFrame para no modificar el original
    df_copy = df.copy()
    
    def strip_leading_zeros(number):
        """Quita los ceros a la izquierda de un número"""
        # Convertir a string y eliminar espacios
        number = str(number).strip()
        # Si está vacío o es solo ceros, devolver vacío
        if not number or all(c == '0' for c in number):
            return ''
        # Quitar ceros a la izquierda
        return number.lstrip('0')
    
    for tel_col, pref_col in columnas:
        # Asegurarse de que la columna existe y convertir a string
        if tel_col in df_copy.columns:
            # Convertir a string y rellenar valores nulos con string vacío
            df_copy[tel_col] = df_copy[tel_col].astype(str).fillna('')
            df_copy[pref_col] = df_copy[pref_col].astype(str).fillna('')
            
            # Procesar cada fila
            for idx, row in df_copy.iterrows():
                tel = row[tel_col].strip()
                if not tel:  # Si el teléfono está vacío, continuar con la siguiente fila
                    continue
                    
                # Verificar si el teléfono comienza con alguno de los prefijos específicos
                prefix_found = False
                for prefijo in prefijos:
                    if tel.startswith(prefijo):
                        # Extraer el prefijo específico (sin ceros) y actualizar ambas columnas
                        df_copy.at[idx, pref_col] = prefijos_sin_ceros[prefijo]
                        df_copy.at[idx, tel_col] = strip_leading_zeros(tel[len(prefijo):])
                        prefix_found = True
                        break
                
                if not prefix_found and len(tel) > 5:
                    # Si no se encontró un prefijo específico y el número tiene más de 5 dígitos,
                    # tomar los primeros 5 caracteres como prefijo (quitando ceros a la izquierda)
                    df_copy.at[idx, pref_col] = strip_leading_zeros(tel[:5])
                    df_copy.at[idx, tel_col] = strip_leading_zeros(tel[5:])
                elif not prefix_found:
                    # Si el número es muy corto, mantener el número original sin prefijo
                    df_copy.at[idx, tel_col] = strip_leading_zeros(tel)
    
    return df_copy

def main():
    st.title("Procesador de archivos .hab")
    st.write("Este programa corrige el tema de los teléfonos en los archivos de creación de cuentas .hab")

    # Subir archivo de datos
    uploaded_file = st.file_uploader("Sube tu archivo cli.hab", type=["hab"])
    
    if uploaded_file is not None:
        try:
            # Mostrar información del archivo
            file_details = {
                "Nombre del archivo": uploaded_file.name,
                "Tipo de archivo": uploaded_file.type,
                "Tamaño": uploaded_file.size
            }
            st.write("Detalles del archivo:")
            for key, value in file_details.items():
                st.write(f"{key}: {value}")

            # Procesar el archivo
            with st.spinner('Procesando archivo...'):
                data_df = extract_fields(uploaded_file, rules_df)
                        
            if data_df is not None and not data_df.empty:
                st.write("DataFrame creado exitosamente:")
                st.write(f"- Número de filas: {len(data_df)}")

                # Procesar sufijos con indicador de progreso
                with st.spinner('Procesando prefijos telefónicos...'):
                    data_df = correct_suffixes(data_df)
                
                # Mostrar las primeras filas del DataFrame corregido
                st.write("Primeras filas del DataFrame corregido:")
                st.dataframe(data_df.head())

                # Formatear campos con indicador de progreso
                with st.spinner('Aplicando formato según reglas A/N...'):
                    formatted_data = format_data(data_df, rules_df)
                st.write(f"Líneas formateadas: {len(formatted_data)}")

                # Filtrar líneas vacías o que solo contengan espacios
                formatted_lines = [line for line in formatted_data if line and not line.isspace()]
                
                if formatted_lines:
                    # Crear el DataFrame final
                    output_df = pd.DataFrame(formatted_lines)
                    
                    # Guardar el archivo
                    output_text_path = 'formatted_output.hab'
                    
                    # Escribir directamente al archivo en modo binario para asegurar CRLF y ANSI
                    with open(output_text_path, 'wb') as f:
                        for line in formatted_lines:
                            # Codificar cada línea en ANSI (latin1) y agregar CRLF
                            f.write(line.encode('latin1') + b'\r\n')
                    
                    st.success(f"Archivo procesado y guardado como {output_text_path}")
                    
                    # Leer el archivo en modo binario para el botón de descarga
                    with open(output_text_path, 'rb') as f:
                        output_content = f.read()
                        st.download_button(
                            label="Descargar archivo procesado",
                            data=output_content,
                            file_name="formatted_output.hab",
                            mime="application/octet-stream"
                        )
                else:
                    st.error("No se generaron líneas formateadas válidas")
            else:
                st.error("No se pudieron extraer datos del archivo")
                
        except Exception as e:
            st.error(f"Error durante el procesamiento: {str(e)}")
            st.write("Detalles del error para debugging:")
            import traceback
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
