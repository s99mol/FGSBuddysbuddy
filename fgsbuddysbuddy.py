"""
Created on Sep 9 2023

 <FGS Buddysbuddy: Creates xslt file through mapping processes and uses that file to create xml metadata file.>
     Copyright (C) 2023 The Buddy Project
     Author: The Buddy Project, with AI Assistant.
     Contact: fgsbuddyproject@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

import csv
import json
import os
import re
import tempfile
import threading
import uuid
import webbrowser
from collections import Counter
from pathlib import Path

import FreeSimpleGUI as sg
from lxml import etree, isoschematron
import pandas as pd

# --- Global Variables & Constants ---

VERSION = '0.3.0'
CWD = os.getcwd()
HOME = Path.home()
TEMP_XML_FILE = None
created_objects = {}
current_object_mappings = []
csv_headers_list = []
xsd_elements_list = []
object_count = 0


# --- Helper Functions ---

def detect_csv_separator(file_path):
    """Detects the delimiter of a CSV file using csv.Sniffer."""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            sniffer = csv.Sniffer()
            sample = f.read(2048)
            f.seek(0)
            dialect = sniffer.sniff(sample, delimiters=';,:\t|')
            return dialect.delimiter
    except (csv.Error, UnicodeDecodeError) as e:
        print(f"Could not determine separator for {os.path.basename(file_path)}. Defaulting to ';'. Error: {e}")
        return ';'


def csv_to_xml(csv_path, separator):
    """
    Converts a CSV file to a new temporary XML file. It sanitizes column headers
    and returns the file path and the list of sanitized headers.
    """
    try:
        df = pd.read_csv(csv_path, sep=separator, engine='python', dtype=str).fillna('')
        
        sanitized_columns = []
        for col in df.columns:
            new_col = re.sub(r'[^a-zA-Z0-9_]', '_', str(col))
            if new_col and new_col[0].isdigit():
                new_col = '_' + new_col
            if 'Unnamed:' in new_col:
                new_col = new_col.replace(':', '_')
            sanitized_columns.append(new_col)
        
        original_columns = df.columns.tolist()
        df.columns = sanitized_columns
        
        renamed_cols = {orig: new for orig, new in zip(original_columns, sanitized_columns) if orig != new}
        if renamed_cols:
            print("ℹ️ Note: The following CSV headers were renamed to be XML-compatible:")
            for orig, new in renamed_cols.items():
                print(f"  - '{orig}' -> '{new}'")

        fd, temp_path = tempfile.mkstemp(suffix=".xml", text=True)
        os.close(fd)
        df.to_xml(temp_path, index=False, root_name='data', row_name='row')
        print(f"Successfully converted CSV to new temporary XML: {os.path.basename(temp_path)}")
        return temp_path, sanitized_columns
        
    except Exception as e:
        sg.popup_error_with_traceback(f'Error during CSV to XML conversion:', e, icon=window_icon_b64, keep_on_top=True)
        return None, None


def json_to_xml(json_path):
    """
    Reads a JSON file, flattens it, and converts it to a new temporary XML file.
    Returns the file path and the sanitized list of headers.
    """
    try:
        with open(json_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

        records_to_normalize = data
        if isinstance(data, dict):
            found_records = False
            for key, value in data.items():
                if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                    records_to_normalize = value
                    print(f"ℹ️ Auto-detected record list in JSON key: '{key}'")
                    found_records = True
                    break
            if not found_records:
                records_to_normalize = [data]

        df = pd.json_normalize(records_to_normalize)

        df.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', str(col)) for col in df.columns]
        sanitized_columns = df.columns.tolist()

        fd, temp_path = tempfile.mkstemp(suffix=".xml", text=True)
        os.close(fd)
        df.to_xml(temp_path, index=False, root_name='data', row_name='row')
        print(f"Successfully converted JSON to new temporary XML: {os.path.basename(temp_path)}")
        return temp_path, sanitized_columns

    except Exception as e:
        sg.popup_error_with_traceback(f'Error during JSON to XML conversion:', e, icon=window_icon_b64, keep_on_top=True)
        return None, None


def json_to_dataframe(json_path):
    """
    Reads a potentially nested JSON file, pre-processes it to remove nulls,
    and flattens it into a pandas DataFrame, ensuring all data remains as strings.
    """
    try:
        def remove_nulls(obj):
            if isinstance(obj, dict):
                return {k: remove_nulls(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [remove_nulls(elem) for elem in obj]
            return "" if obj is None else obj

        with open(json_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        
        clean_data = remove_nulls(data)
        
        records_to_normalize = clean_data
        if isinstance(clean_data, dict):
            found_records = False
            for key, value in clean_data.items():
                if isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
                    records_to_normalize = value
                    print(f"ℹ️ Auto-detected record list in JSON key: '{key}'")
                    found_records = True
                    break
            if not found_records:
                records_to_normalize = [clean_data]

        df = pd.json_normalize(records_to_normalize)
        
        if df is not None:
            df = df.astype(str)
            
        return df

    except Exception as e:
        sg.popup_error_with_traceback(f'Error reading or parsing JSON file:', e, icon=window_icon_b64, keep_on_top=True)
        return None


def flatten_xml_to_dataframe(xml_path):
    """
    Uses a hybrid approach to read XML into a DataFrame, ensuring all data is
    loaded as strings to prevent number formatting issues.
    """
    try:
        print("ℹ️ Attempting simple read for wide-format statistics...")
        tree = etree.parse(xml_path)
        root = tree.getroot()
        nsmap = root.nsmap
        
        if None in nsmap:
            nsmap['doc'] = nsmap.pop(None)

        tags = [etree.QName(element).localname for element in root.iter()]
        tag_counts = Counter(tags)
        
        root_tag = etree.QName(root).localname
        if root_tag in tag_counts:
            del tag_counts[root_tag]
        
        if not tag_counts:
             raise ValueError("No repeating elements found for a simple table read.")

        record_element = tag_counts.most_common(1)[0][0]
        
        xpath_query = f'//doc:{record_element}' if 'doc' in nsmap else f'//{record_element}'
        
        df = pd.read_xml(xml_path, xpath=xpath_query, namespaces=nsmap, dtype=str)
        
        if len(df.columns) > 1:
            print(f"✅ Simple read successful. Detected '<{record_element}>' as the record.")
            df.fillna('', inplace=True)
            return df.astype(str)
        else:
            raise ValueError("Simple read produced a single-column DataFrame; file is likely nested.")

    except Exception as e:

        print(f"⚠️ Simple read failed ({e}), falling back to deep scan for complex XML...")
        
        try:
            tree = etree.parse(xml_path)
            data_list = []

            for element in tree.iter():
                if element.attrib:
                    for attr_name, attr_value in element.attrib.items():
                        path_parts = [etree.QName(el).localname for el in element.iterancestors()]
                        path_parts.reverse()
                        path_parts.append(etree.QName(element).localname)
                        attr_path = '/'.join(path_parts) + f'/@{etree.QName(attr_name).localname}'
                        data_list.append({
                            'ElementPath': attr_path,
                            'ElementName': f"@{etree.QName(attr_name).localname}",
                            'ElementValue': attr_value
                        })
                if element.text and element.text.strip():
                    path_parts = [etree.QName(el).localname for el in element.iterancestors()]
                    path_parts.reverse()
                    path_parts.append(etree.QName(element).localname)
                    data_list.append({
                        'ElementPath': '/'.join(path_parts),
                        'ElementName': etree.QName(element).localname,
                        'ElementValue': element.text.strip()
                    })
            
            if not data_list:
                raise ValueError("The XML file appears to contain no text data or attributes.")

            df = pd.DataFrame(data_list).astype(str)
            print("✅ Deep scan successful.")
            return df

        except Exception as e2:
            sg.popup_error(f"Failed to read XML with both simple and deep scan methods.\n\nDetails: {e2}", icon=window_icon_b64, keep_on_top=True)
            return None

           
def load_xsd_isolated(file_path):
    """Loads XSD elements, attributes, and targetNamespace."""
    try:
        tree = etree.parse(file_path)
        root = tree.getroot()
        ns = {'xsd': 'http://www.w3.org/2001/XMLSchema'}
        namespace = root.attrib.get('targetNamespace', '')
        
        elements = [elem.get('name') for elem in root.findall('.//xsd:element', ns) if elem.get('name')]
        attributes = [attr.get('name') for attr in root.findall('.//xsd:attribute', ns) if attr.get('name')]
        all_names = sorted(list(set(elements + attributes)))
        
        top_level_elements = [elem.get('name') for elem in root.findall('./xsd:element', ns) if elem.get('name')]
        suggested_root = top_level_elements[0] if top_level_elements else ''
        
        print(f"XSD loaded with {len(all_names)} elements/attributes. Namespace: {namespace or 'Not found'}.")
        return all_names, namespace, suggested_root
    except Exception as e:
        sg.popup_error(f"Error loading XSD: {e}", icon=window_icon_b64, keep_on_top=True)
        return [], '', ''


def get_elements_from_xml(xml_path):
    """Parses an XML file and returns a sorted list of unique element tags."""
    if not xml_path or not os.path.exists(xml_path):
        return []
    try:
        tree = etree.parse(xml_path)
        elements = sorted(list(set([elem.tag for elem in tree.iter() if isinstance(elem, etree._Element)])))
        return elements
    except etree.XMLSyntaxError as e:
        sg.popup_error(f"Error parsing the intermediate XML file. It may be malformed.\n\nDetails: {e}", icon=window_icon_b64, keep_on_top=True)
        return []

       
def calculate_statistics(df):
    """
    Performs statistical analysis on a DataFrame and returns a dictionary of the results.
    """
    if df is None or df.empty:
        return None
    
    s1 = df.count()
    s2 = df.nunique()
    df_totals = pd.concat([s1, s2], axis=1)
    df_totals.rename(columns={0: 'TotalCount', 1: 'UniqueCount'}, inplace=True)
    
    num_duplicate_rows = df.duplicated().sum()
    duplicate_rows_df = None
    if num_duplicate_rows > 0:
        duplicate_rows_df = df[df.duplicated(keep=False)]

    return {
        'totals_df': df_totals,
        'num_duplicates': num_duplicate_rows,
        'duplicate_rows_df': duplicate_rows_df,
    }


def save_statistics_report(stats_data, output_folder):
    """
    Saves the results from calculate_statistics to a set of CSV files.
    """
    try:
        report_dir = os.path.join(output_folder, f"statistics_report_{uuid.uuid4().hex[:8]}")
        os.makedirs(report_dir, exist_ok=True)
        print(f"--- Saving Full Statistics Report ---")
        print(f"Saving reports to: {report_dir}")

        stats_data['totals_df'].to_csv(os.path.join(report_dir, 'totals_and_unique.csv'), index_label='Column')
        
        if stats_data['duplicate_rows_df'] is not None:
            stats_data['duplicate_rows_df'].to_csv(os.path.join(report_dir, 'duplicate_rows.csv'), index=False)
        
        sg.popup_ok(f"Successfully saved statistics reports to:\n{report_dir}", icon=window_icon_b64, keep_on_top=True)
    
    except Exception as e:
        sg.popup_error_with_traceback("Failed to save statistics report:", e, icon=window_icon_b64, keep_on_top=True)

            
def suggest_keys(df):
    """
    Analyzes a DataFrame to suggest a 3-level key hierarchy, prioritizing
    column names and their position in the file.
    """
    if df is None or df.empty or len(df.columns) < 1:
        return []

    num_rows = len(df)
    suggestions = []
    key_identifiers = ['id', 'key', 'nummer', 'code']

    candidates = []
    for col in df.columns:
        unique_count = df[col].nunique()
        if unique_count <= 1 or unique_count == num_rows:
            continue
        is_priority_name = any(sub.lower() in str(col).lower() for sub in key_identifiers)
        candidates.append({'name': col, 'is_priority': is_priority_name})

    if not candidates:
        return []

    priority_candidates = [c for c in candidates if c['is_priority']]
    best_parent_candidate = None
    if priority_candidates:
        best_parent_candidate = min(priority_candidates, key=lambda c: df.columns.get_loc(c['name']))
    else:
        normal_candidates = [c for c in candidates if not c['is_priority']]
        if normal_candidates:
            for c in normal_candidates:
                c['uniqueness'] = df[c['name']].nunique() / num_rows
            best_parent_candidate = min(normal_candidates, key=lambda x: x['uniqueness'])
    
    if not best_parent_candidate:
        return []

    key1 = best_parent_candidate['name']
    suggestions.append(key1)
    if len(candidates) < 2:
        return suggestions

    best_combo_uniqueness = -1
    key2 = None
    remaining_cols = [c['name'] for c in candidates if c['name'] != key1]
    for col in remaining_cols:
        combo_uniqueness = len(df.groupby([key1, col])) / num_rows
        if combo_uniqueness > best_combo_uniqueness:
            best_combo_uniqueness = combo_uniqueness
            key2 = col
    if key2:
        suggestions.append(key2)
    else:
        return suggestions

    if len(candidates) < 3:
        return suggestions

    best_combo_uniqueness_3 = -1
    key3 = None
    remaining_cols_3 = [c for c in remaining_cols if c != key2]
    for col in remaining_cols_3:
        combo_uniqueness_3 = len(df.groupby([key1, key2, col])) / num_rows
        if combo_uniqueness_3 > best_combo_uniqueness_3:
            best_combo_uniqueness_3 = combo_uniqueness_3
            key3 = col
    
    if key3 and best_combo_uniqueness_3 > best_combo_uniqueness:
        suggestions.append(key3)
            
    return suggestions

    
def format_hierarchy_view(df, keys, triggers):
    """
    Takes a DataFrame and selected keys/triggers and returns a formatted,
    indented string representing the data hierarchy.
    """
    if df is None or df.empty or not keys:
        return "No data or keys to preview."

    all_cols = keys + [t for t in triggers if t]
    if not all(col in df.columns for col in all_cols):
        return "Error: One or more selected columns not found in the data."

    sorted_df = df.sort_values(by=keys).reset_index(drop=True)
    
    output_lines = ["--- Hierarchy Preview ---"]
    last_keys = [None] * len(keys)

    for index, row in sorted_df.iterrows():
        for i, key_col in enumerate(keys):
            if row[key_col] != last_keys[i]:
                indent = '    ' * i
                output_lines.append(f"{indent}{key_col}: {row[key_col]}")
                for j in range(i, len(keys)):
                    last_keys[j] = row[key_col] if i == j else None
        
        trigger_col = triggers[len(keys) - 1]
        if trigger_col and row[trigger_col]:
             indent = '    ' * len(keys)
             output_lines.append(f"{indent}- {trigger_col}: {row[trigger_col]}")

    return "\n".join(output_lines)

    
def generate_node_xslt(node, indent_level, csv_headers):
    """Generates XSLT for a complex node, handling an optional inner wrapper element."""
    lines, indent_space = [], '    '
    indent = indent_space * indent_level
    tag_name = node['name']
    wrapper_name = node.get('wrapper_name')
    
    attributes = [c for c in node.get('children', []) if c['type'] == 'attribute']
    elements = [c for c in node.get('children', []) if c['type'] == 'element']

    lines.append(f"{indent}<{tag_name}>")
    
    if wrapper_name:
        lines.append(f"{indent}{indent_space}<{wrapper_name}>")
    
    child_indent = indent + indent_space * (2 if wrapper_name else 1)
    
    for attr in attributes:
        lines.append(f"{child_indent}<xsl:attribute name=\"{attr['name']}\">")
        if attr['value_is_header']:
            lines.append(f"{child_indent}{indent_space}<xsl:value-of select=\"{attr['value']}\"/>")
        else:
            lines.append(f"{child_indent}{indent_space}<xsl:text>{attr['value']}</xsl:text>")
        lines.append(f"{child_indent}</xsl:attribute>")
            
    for elem in elements:
        lines.append(f"{child_indent}<{elem['name']}>")
        
        if elem.get('attribute'):
            attr = elem['attribute']
            lines.append(f"{child_indent}{indent_space}<xsl:attribute name=\"{attr['name']}\">")
            if attr['value_is_header']:
                lines.append(f"{child_indent}{indent_space*2}<xsl:value-of select=\"{attr['value']}\"/>")
            else:
                lines.append(f"{child_indent}{indent_space*2}<xsl:text>{attr['value']}</xsl:text>")
            lines.append(f"{child_indent}{indent_space}</xsl:attribute>")

        if elem['value_is_header']:
            lines.append(f"{child_indent}{indent_space}<xsl:value-of select=\"{elem['value']}\"/>")
        else:
            lines.append(f"{child_indent}{indent_space}<xsl:text>{elem['value']}</xsl:text>")
        
        lines.append(f"{child_indent}</{elem['name']}>")

    if wrapper_name:
        lines.append(f"{indent}{indent_space}</{wrapper_name}>")

    lines.append(f"{indent}</{tag_name}>")
    return lines

    
def generate_xslt_with_fstrings(created_objects_data, ui_values, object_count, csv_headers, output_path):
    """Generates the final XSLT stylesheet."""
    try:
        root_element = ui_values.get('-ROOT_ELEMENT-', "Leveransobjekt")
        xmlns = ui_values.get('-XML_NAMESPACE-', "")
        indent_space = '    '

        template_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" xmlns="{xmlns}">',
            f'{indent_space}<xsl:strip-space elements="*"/>',
            f'{indent_space}<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>',
        ]

        root_key_csv = ui_values.get('-ID_CSV_1-')
        if not root_key_csv and object_count > 0:
            sg.popup_error("Error: 'Key input 1' for Config 1 is required.", icon=window_icon_b64, keep_on_top=True)
            return False
            
        for i in range(1, object_count + 1):
            id_csv = ui_values.get(f'-ID_CSV_{i}-')
            if not id_csv: continue
            key_use_expr = id_csv if i == 1 else f"concat({root_key_csv}, '|', {id_csv})"
            key_tag_template = f'{indent_space}<xsl:key name="{{name}}" match="row" use="{{expr}}"/>'
            if i == 2 and ui_values.get(f'-REPEAT_ENABLE_{i}-'):
                 template_parts.append(key_tag_template.format(name='mode_2', expr=key_use_expr))
                 template_parts.append(key_tag_template.format(name='mode_3', expr=key_use_expr))
            else:
                 template_parts.append(key_tag_template.format(name=f'mode_{i}', expr=key_use_expr))

        sub_element_1 = ui_values.get('-SUB_ELEMENT_1-')
        template_parts.extend([
            f'{indent_space}<xsl:template match="/data">', f'{indent_space*2}<{root_element}>'
        ])
        if sub_element_1: template_parts.append(f'{indent_space*3}<{sub_element_1}>')
        if root_key_csv:
            indent = indent_space * 4 if sub_element_1 else indent_space * 3
            template_parts.append(f"{indent}<xsl:apply-templates select=\"row[generate-id() = generate-id(key('mode_1', {root_key_csv})[1])]\" mode='mode_1'/>")
        if sub_element_1: template_parts.append(f'{indent_space*3}</{sub_element_1}>')
        template_parts.extend([f'{indent_space*2}</{root_element}>', f'{indent_space}</xsl:template>'])
        
        def get_mapping_xslt(mapping, indent_level, csv_headers_list):
            lines = []
            indent = '    ' * indent_level
            
            if mapping.get('is_complex'):
                trigger_column = None
                for child in mapping.get('children', []):
                    if child.get('value_is_header'):
                        trigger_column = child['value']
                        break
                    if child.get('attribute') and child['attribute']['value_is_header']:
                        trigger_column = child['attribute']['value']
                        break
                
                if trigger_column:
                    lines.append(f'{indent}<xsl:if test="string({trigger_column})">')
                    lines.extend(generate_node_xslt(mapping, indent_level + 1, csv_headers_list))
                    lines.append(f'{indent}</xsl:if>')
                else: 
                    lines.extend(generate_node_xslt(mapping, indent_level, csv_headers_list))
                return lines

            if mapping['value_is_header']:
                lines.append(f'{indent}<xsl:if test="string({mapping["value"]})">')
            
            lines.append(f'{indent}    <{mapping["xsd"]}>')

            if mapping.get('type') == 'simple_with_attr':
                attr = mapping['attribute']
                lines.append(f'{indent}        <xsl:attribute name="{attr["name"]}">')
                if attr['value_is_header']:
                    lines.append(f'{indent}            <xsl:value-of select="{attr["value"]}"/>')
                else:
                    lines.append(f'{indent}            <xsl:text>{attr["value"]}</xsl:text>')
                lines.append(f'{indent}        </xsl:attribute>')

            if mapping['value_is_header']:
                lines.append(f'{indent}        <xsl:value-of select="{mapping["value"]}"/>')
            else:
                lines.append(f'{indent}        <xsl:text>{mapping["value"]}</xsl:text>')

            lines.append(f'{indent}    </{mapping["xsd"]}>')
            if mapping['value_is_header']:
                lines.append(f'{indent}</xsl:if>')
                
            return lines

        for i in range(1, object_count + 1):
            obj_type = ui_values.get(f'-OBJECT_TYPE_{i}-')
            id_csv = ui_values.get(f'-ID_CSV_{i}-')
            id_xsd = ui_values.get(f'-ID_XSD_{i}-')
            sysid_name = ui_values.get(f'-SYSID_XSD_{i}-')
            
            if not all([obj_type, id_csv, id_xsd]) or obj_type not in created_objects_data: continue
            
            obj_details = created_objects_data[obj_type]
            obj_xsd_element = obj_details.get('xsd_element', obj_type)

            template_parts.append(f'{indent_space}<xsl:template match="row" mode="mode_{i}">')
            template_parts.append(f'{indent_space*2}<{obj_xsd_element}>')
            
            if sysid_name:
                template_parts.extend([f'{indent_space*3}<xsl:attribute name="{sysid_name}"/>'])

            if i > 1 and ui_values.get(f'-COMBINE_KEY_{i}-'):
                separator = ui_values.get(f'-KEY_SEPARATOR_{i}-', '/')
                template_parts.extend([
                    f'{indent_space*3}<{id_xsd}>', 
                    f'{indent_space*4}<xsl:value-of select="{root_key_csv}"/>',
                    f'{indent_space*4}<xsl:text>{separator}</xsl:text>', 
                    f'{indent_space*4}<xsl:value-of select="{id_csv}"/>',
                    f'{indent_space*3}</{id_xsd}>',
                ])
            else:
                template_parts.extend([
                    f'{indent_space*3}<{id_xsd}>', 
                    f'{indent_space*4}<xsl:value-of select="{id_csv}"/>', 
                    f'{indent_space*3}</{id_xsd}>'
                ])
            
            for mapping in obj_details['mappings']:
                template_parts.extend(get_mapping_xslt(mapping, 3, csv_headers))

            if ui_values.get(f'-REPEAT_ENABLE_{i}-'):
                key_for_group = id_csv if i == 1 else f"concat({root_key_csv}, '|', {id_csv})"
                template_parts.append(f'{indent_space*3}<xsl:apply-templates select="key(\'mode_{i}\', {key_for_group})" mode="repeat_mode_{i}"/>')

            if i < object_count:
                child_id_csv = ui_values.get(f'-ID_CSV_{i+1}-')
                if child_id_csv:
                    child_sub_element = ui_values.get(f'-SUB_ELEMENT_{i+1}-')
                    next_level_key_name = f'mode_{i+1}'
                    key_val_for_child = f"concat({root_key_csv}, '|', {child_id_csv})"
                    select_expr = f"key('mode_{i}', {id_csv})[generate-id() = generate-id(key('{next_level_key_name}', {key_val_for_child})[1])]"
                    apply_templates_line = f'<xsl:apply-templates mode="{next_level_key_name}" select="{select_expr}"/>'
                    
                    template_parts.append(f'{indent_space*3}<xsl:if test="string({child_id_csv})">')
                    if child_sub_element:
                        template_parts.extend([f'{indent_space*4}<{child_sub_element}>', f'{indent_space*5}{apply_templates_line}', f'{indent_space*4}</{child_sub_element}>'])
                    else:
                        template_parts.append(f'{indent_space*4}{apply_templates_line}')
                    template_parts.append(f'{indent_space*3}</xsl:if>')
            
            template_parts.extend([f'{indent_space*2}</{obj_xsd_element}>', f'{indent_space}</xsl:template>'])

        for i in range(1, object_count + 1):
            if ui_values.get(f'-REPEAT_ENABLE_{i}-'):
                repeat_obj_type = ui_values.get(f'-REPEAT_OBJECT_TYPE_{i}-')
                repeat_trigger_csv = ui_values.get(f'-REPEAT_CSV_TRIGGER_{i}-')
                
                if repeat_obj_type and repeat_trigger_csv and repeat_obj_type in created_objects_data:
                    rep_obj_details = created_objects_data[repeat_obj_type]
                    mappings = rep_obj_details.get('mappings', [])
                    
                    template_parts.append(f'{indent_space}<xsl:template match="row" mode="repeat_mode_{i}">')
                    template_parts.append(f'{indent_space*2}<xsl:if test="string({repeat_trigger_csv})">')
                    
                    if len(mappings) == 1 and mappings[0].get('is_complex'):
                        template_parts.extend(generate_node_xslt(mappings[0], 3, csv_headers))
                    else:
                        rep_root_tag = rep_obj_details.get('xsd_element', repeat_obj_type)
                        template_parts.append(f'{indent_space*3}<{rep_root_tag}>')
                        for mapping in mappings:
                            if not mapping.get('is_complex'):
                                if mapping['value_is_header']:
                                    template_parts.extend([
                                        f'{indent_space*4}<xsl:if test="string({mapping["value"]})">',
                                        f'{indent_space*5}<{mapping["xsd"]}><xsl:value-of select="{mapping["value"]}"/></{mapping["xsd"]}>',
                                        f'{indent_space*4}</xsl:if>'
                                    ])
                                else:
                                    template_parts.extend([f'{indent_space*4}<{mapping["xsd"]}><xsl:text>{mapping["value"]}</xsl:text></{mapping["xsd"]}>'])
                        template_parts.append(f'{indent_space*3}</{rep_root_tag}>')
                    
                    template_parts.extend([f'{indent_space*2}</xsl:if>', f'{indent_space}</xsl:template>'])

        template_parts.append('</xsl:stylesheet>')
        final_xslt_output = "\n".join(template_parts)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_xslt_output)
        sg.popup_ok(f"XSLT generated successfully:\n{output_path}", icon=window_icon_b64, keep_on_top=True)
        return True

    except Exception as e:
        sg.popup_error_with_traceback("An unexpected error occurred during XSLT generation:", e, icon=window_icon_b64, keep_on_top=True)
        return False

    
def run_xslt_transform(xml_input, xslt_path, output_path):
    """Transforms an XML file using an XSLT file."""
    try:
        dom = etree.parse(xml_input)
        xslt = etree.parse(xslt_path)
        transform = etree.XSLT(xslt)
        result_tree = transform(dom)
        
        if not confirm_overwrite(output_path):
            return False
        
        result_tree.write(output_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        print(f"✅ Transformation successful. Output saved to: {output_path}")
        return True
    except Exception as e:
        print(f"❌ XSLT Transformation Failed: {e}")
        sg.popup_error(f"XSLT Transformation Failed:\n\n{e}", icon=window_icon_b64, keep_on_top=True)
        return False

        
def run_xml_schema_validation(xml_path, xsd_path):
    """Validates an XML file against an XSD schema."""
    try:
        xmlschema_doc = etree.parse(xsd_path)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        xml_doc = etree.parse(xml_path)
        xmlschema.assertValid(xml_doc)
        print(f"✅ XML is valid against the schema: {os.path.basename(xsd_path)}")
        return True
    except etree.DocumentInvalid as e:
        print(f"❌ XML Validation Failed:\n{str(e)}")
        sg.popup_error(f"XML Validation Failed:\n\n{str(e)}", icon=window_icon_b64, keep_on_top=True)
        return False
    except Exception as e:
        print(f"❌ An error occurred during validation: {e}")
        sg.popup_error(f"An error occurred during validation:\n\n{e}", icon=window_icon_b64, keep_on_top=True)
        return False

        
def run_schematron_validation(xml_path, schematron_path, output_folder):
    """
    Validates an XML file against a Schematron schema and generates a report.
    """
    print(f"\n--- Running Schematron Validation on {os.path.basename(xml_path)} ---")
    try:
        sct_doc = etree.parse(schematron_path)
        schematron = isoschematron.Schematron(sct_doc, store_report=True)
        
        doc = etree.parse(xml_path)

        is_valid = schematron.validate(doc)
        print(f"Schematron validation result: {is_valid}")

        report = schematron.validation_report
        
        unique_id = uuid.uuid4().hex[:8]
        report_filename = f"schematronreport_{unique_id}.xml"
        report_path = os.path.join(output_folder, report_filename)
        
        report.write(report_path, pretty_print=True, encoding='UTF-8')
        print(f"✅ Schematron report saved to: {report_path}")

        if not is_valid:
            ns = {'svrl': 'http://purl.oclc.org/dsdl/svrl'}
            failed_asserts = report.xpath('//svrl:failed-assert', namespaces=ns)
            
            if failed_asserts:
                print(f"❌ Found {len(failed_asserts)} validation failures:")
                for i, failure in enumerate(failed_asserts[:5]):
                    text = failure.findtext('svrl:text', namespaces=ns).strip()
                    location = failure.get('location')
                    print(f"  - Error at {location}: {text}")
                if len(failed_asserts) > 5:
                    print("  ... and more. See the full report for details.")
        return True

    except Exception as e:
        error_message = f"❌ Schematron validation failed with an error: {e}"
        print(error_message)
        sg.popup_error(f"Schematron Validation Error:\n\n{e}", icon=window_icon_b64, keep_on_top=True)
        return False

        
def add_uuids_to_xml(xml_path, targets):
    """
    Parses an XML file and adds UUIDs to specified attributes.
    
    :param xml_path: Path to the XML file to modify.
    :param targets: A list of tuples, where each tuple is (element_name, attribute_name).
    """
    if not targets:
        print("ℹ️ No targets for UUID generation were specified.")
        return
        
    print(f"ℹ️ Adding UUIDs to {os.path.basename(xml_path)}...")
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(xml_path, parser)
        root = tree.getroot()
        
        for elem_name, attr_name in targets:
            for element in root.xpath(f"//*[local-name()='{elem_name}']"):
                element.set(attr_name, uuid.uuid4().hex)
        
        tree.write(xml_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        print(f"✅ UUIDs successfully added.")
    except Exception as e:
        sg.popup_error(f"Failed to add UUIDs to the XML file:\n\n{e}", icon=window_icon_b64, keep_on_top=True)

            
def show_buddy_window():
    """Displays the 'About' window with release notes."""
    releasenotes_path = os.path.join(CWD, 'releasenotes.txt')
    releasenotes = "Release notes file not found."
    if os.path.exists(releasenotes_path):
        with open(releasenotes_path, encoding='utf-8') as f:
            releasenotes = f.read()

    about_layout = [
        [sg.Text('Buddysbuddy', font='Arial 12 bold')],
        [sg.Text(f'Version: {VERSION}\nLicens: GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007')],
        [sg.Text('This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.')],
        [sg.Text('This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty ofMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.')],
        [sg.Text('You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.')],
        [sg.Text('FGS Buddysbuddy on GitHub', font='Consolas 10 underline', text_color='blue', enable_events=True, key='-LINK_BUDDYSBUDDY-')],
        [sg.VPush()],
        [sg.Button('OK')]
    ]
    about_window = sg.Window('About FGS Buddysbuddy', about_layout, modal=True, icon=window_icon_b64, keep_on_top=True)
    while True:
        event, _ = about_window.read()
        if event in (sg.WIN_CLOSED, 'OK'):
            break
        elif event == '-LINK_BUDDYSBUDDY-':
            webbrowser.open('https://github.com/s99mol/FGSBuddysbuddy')
    about_window.close()

       
def confirm_overwrite(file_path):
    """
    Checks if a file exists and asks the user for confirmation to overwrite.
    Returns True if the program should proceed, False if it should cancel.
    """
    if os.path.exists(file_path):
        answer = sg.popup_yes_no(
            f"A file named '{os.path.basename(file_path)}' already exists.\nDo you want to overwrite it?",
            title="Confirm Overwrite",
            icon=window_icon_b64,
            keep_on_top=True
        )
        if answer == 'No':
            print(f"⚠️ Operation cancelled by user. Did not overwrite {os.path.basename(file_path)}.")
            return False
    return True

    
def create_complex_element_window(xsd_elements, csv_headers):
    """Opens a popup window to build a complex XML element with an optional wrapper."""
    children = []
    
    attribute_frame = [
        [sg.Checkbox('Add Attribute to this Element', key='-CHILD_ADD_ATTR-', default=False, enable_events=True)],
        [sg.Text("Attr Name:", size=(10,1)), sg.Combo(xsd_elements, key='-CHILD_ATTR_NAME-', size=(20,1), readonly=False, disabled=True)],
        [sg.Radio('From Header', 'CHILD_ATTR_TYPE', key='-CHILD_ATTR_IS_HEADER-', default=True, disabled=True, enable_events=True),
         sg.Combo(csv_headers, key='-CHILD_ATTR_HEADER_VALUE-', size=(20,1), readonly=False, disabled=True)],
        [sg.Radio('Fixed Value', 'CHILD_ATTR_TYPE', key='-CHILD_ATTR_IS_FIXED-', disabled=True, enable_events=True),
         sg.Input(key='-CHILD_ATTR_FIXED_VALUE-', size=(22,1), disabled=True)]
    ]

    layout = [
        [sg.Text("Complex Element Builder", font=("Arial", 12, "bold"))],
        [sg.Text("Parent Element Name:*", size=(20,1)), sg.Combo(xsd_elements, key='-PARENT_NAME-', size=(30,1), readonly=False)],
        [sg.Checkbox('Add optional wrapper element', key='-ADD_WRAPPER-', enable_events=True, default=False)],
        [sg.Text('Wrapper Element Name:', size=(20,1)), sg.Combo(xsd_elements, key='-WRAPPER_NAME-', size=(30,1), disabled=True, readonly=False)],
        [sg.HSeparator()],
        [sg.Text("Define a Child or Attribute:")],
        [sg.Radio('Element', "TYPE", default=True, key='-IS_ELEMENT-', enable_events=True), sg.Radio('Attribute', "TYPE", key='-IS_ATTRIBUTE-', enable_events=True)],
        [sg.Text("Name:", size=(10,1)), sg.Combo(xsd_elements, key='-CHILD_NAME-', size=(30,1), readonly=False)],
        [sg.Text("Value Source:", pad=((5,0), (10,0)))],
        [sg.Radio('From Input Header', 'CHILD_VAL_TYPE', key='-CHILD_IS_HEADER-', default=True, enable_events=True, pad=((15,0),0)),
         sg.Combo(csv_headers, key='-CHILD_HEADER_VALUE-', size=(28,1), readonly=False)],
        [sg.Radio('Use Fixed Value', 'CHILD_VAL_TYPE', key='-CHILD_IS_FIXED-', enable_events=True, pad=((15,0),0)),
         sg.Input(key='-CHILD_FIXED_VALUE-', size=(30,1), disabled=True)],
        [sg.Frame("Attribute (for Element child)", attribute_frame, key='-CHILD_ATTR_FRAME-')],
        [sg.Button("Add Child/Attribute", button_color=('white', 'green'))],
        [sg.HSeparator()],
        [sg.Text("Current Structure:")],
        [sg.Listbox(values=[], size=(80, 10), key='-CHILD_LIST-')],
        [sg.Button("Save Complex Element", button_color=('black', 'lightblue'))]
    ]

    window = sg.Window("Complex Element Builder", layout, modal=True, finalize=True, icon=window_icon_b64, keep_on_top=True)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Cancel"): return None

        elif event == '-ADD_WRAPPER-':
            window['-WRAPPER_NAME-'].update(disabled=not values['-ADD_WRAPPER-'])
        elif event == '-CHILD_IS_HEADER-':
            window['-CHILD_HEADER_VALUE-'].update(disabled=False)
            window['-CHILD_FIXED_VALUE-'].update(disabled=True)
        elif event == '-CHILD_IS_FIXED-':
            window['-CHILD_HEADER_VALUE-'].update(disabled=True)
            window['-CHILD_FIXED_VALUE-'].update(disabled=False)
        elif event == '-CHILD_ADD_ATTR-':
            is_checked = values['-CHILD_ADD_ATTR-']
            for k in ['-CHILD_ATTR_NAME-', '-CHILD_ATTR_IS_HEADER-', '-CHILD_ATTR_IS_FIXED-']:
                window[k].update(disabled=not is_checked)
            if is_checked: 
                window['-CHILD_ATTR_HEADER_VALUE-'].update(disabled=not values['-CHILD_ATTR_IS_HEADER-'])
                window['-CHILD_ATTR_FIXED_VALUE-'].update(disabled=not values['-CHILD_ATTR_IS_FIXED-'])
        elif event == '-CHILD_ATTR_IS_HEADER-':
            window['-CHILD_ATTR_HEADER_VALUE-'].update(disabled=False)
            window['-CHILD_ATTR_FIXED_VALUE-'].update(disabled=True)
        elif event == '-CHILD_ATTR_IS_FIXED-':
            window['-CHILD_ATTR_HEADER_VALUE-'].update(disabled=True)
            window['-CHILD_ATTR_FIXED_VALUE-'].update(disabled=False)

        elif event == "Add Child/Attribute":
            child_type = 'element' if values['-IS_ELEMENT-'] else 'attribute'
            child_name = values['-CHILD_NAME-']
            if not child_name:
                sg.popup_error("Name must be provided.", icon=window_icon_b64, keep_on_top=True)
                continue

            is_header = values['-CHILD_IS_HEADER-']
            child_value = values['-CHILD_HEADER_VALUE-'] if is_header else values['-CHILD_FIXED_VALUE-']
            
            if not child_value and child_type == 'element':
                sg.popup_error("Value must be provided for elements.", icon=window_icon_b64, keep_on_top=True)
                continue
            
            child_data = {'type': child_type, 'name': child_name, 'value': child_value, 'value_is_header': is_header}

            if child_type == 'element' and values['-CHILD_ADD_ATTR-']:
                attr_is_header = values['-CHILD_ATTR_IS_HEADER-']
                attr_name = values['-CHILD_ATTR_NAME-']
                attr_value = values['-CHILD_ATTR_HEADER_VALUE-'] if attr_is_header else values['-CHILD_ATTR_FIXED_VALUE-']
                if attr_name and attr_value:
                    child_data['attribute'] = {'name': attr_name, 'value': attr_value, 'value_is_header': attr_is_header}
                else:
                    sg.popup_error("Attribute Name and Value are required.", icon=window_icon_b64, keep_on_top=True)
                    continue
            
            children.append(child_data)
            
            display_list = []
            for c in children:
                val_type = "Header" if c['value_is_header'] else "Fixed"
                attr_str = ''
                if c.get('attribute'):
                    attr = c['attribute']
                    attr_val_type = "Header" if attr['value_is_header'] else "Fixed"
                    attr_str = f' [ATTR: {attr["name"]}={attr["value"]} ({attr_val_type})]'
                display_list.append(f"[{c['type']}] {c['name']} = {c['value']} ({val_type}){attr_str}")
            window['-CHILD_LIST-'].update(values=display_list)

        elif event == "Save Complex Element":
            parent_name = values['-PARENT_NAME-']
            if not parent_name: sg.popup_error("Parent Element Name is required.", icon=window_icon_b64, keep_on_top=True); continue
            if not children: sg.popup_error("You must add at least one child or attribute.", icon=window_icon_b64, keep_on_top=True); continue
            
            result = {'is_complex': True, 'name': parent_name, 'children': children}

            if values['-ADD_WRAPPER-'] and values['-WRAPPER_NAME-']:
                result['wrapper_name'] = values['-WRAPPER_NAME-']

            window.close()
            return result
            
    window.close()
    return None


def add_new_config_frame(window, preselected_key=None, onetomany_trigger=None):
    """
    Dynamically adds a new 'Config' frame to the XSLT Mapper tab,
    with optional pre-selected values for the key and one-to-many trigger.
    """
    global object_count
    object_count += 1
    
    repeat_enabled_default = bool(onetomany_trigger)
    trigger_default = onetomany_trigger or ''
    related_fields_disabled = not repeat_enabled_default
    
    repeating_element_frame = [
        [sg.Checkbox('Enable One-to-Many', key=f'-REPEAT_ENABLE_{object_count}-', default=repeat_enabled_default, enable_events=True)],
        [sg.Text('└ Repeating Object Type:', size=(22,1)), sg.Combo(values=list(created_objects.keys()), size=(30, 1), key=f'-REPEAT_OBJECT_TYPE_{object_count}-', readonly=False, disabled=related_fields_disabled)],
        [sg.Text('└ Source Column for Repetition:', size=(22,1)), sg.Combo(values=csv_headers_list, size=(30, 1), key=f'-REPEAT_CSV_TRIGGER_{object_count}-', default_value=trigger_default, readonly=False, disabled=related_fields_disabled)],
    ]
    key_combination_option = [[
        sg.Checkbox('Combine Key with Parent Key', key=f'-COMBINE_KEY_{object_count}-', default=False, enable_events=True),
        sg.Text("Separator:"),
        sg.Combo(['/', '-', '_', '.'], default_value='/', size=(5, 1), key=f'-KEY_SEPARATOR_{object_count}-', readonly=False, disabled=False)
    ]]
    
    new_rows = [[sg.Frame(f"Config {object_count}", [
            [sg.Text(f"Object Type:*", size=(22,1)), sg.Combo(values=list(created_objects.keys()), size=(30, 1), key=f'-OBJECT_TYPE_{object_count}-', readonly=True)],
            [sg.Text(f"Grouping Key (Input):*", size=(22,1)), sg.Combo(values=csv_headers_list, size=(30, 1), key=f'-ID_CSV_{object_count}-', default_value=preselected_key or '')],
            [sg.Text(f"Grouping Key (XSD):*", size=(22,1)), sg.Combo(values=xsd_elements_list, size=(30, 1), key=f'-ID_XSD_{object_count}-')],
            [sg.Frame('Key Options (for Level 2+)', key_combination_option, font='Arial 9 bold')],
            [sg.Text(f"Wrapper Element Name:", size=(22,1)), sg.Combo(values=xsd_elements_list, size=(30, 1), key=f'-SUB_ELEMENT_{object_count}-')],
            [sg.Text(f"System ID Attr Name:", size=(22,1)), sg.Combo(values=xsd_elements_list, size=(30, 1), key=f'-SYSID_XSD_{object_count}-', readonly=False, tooltip="The name of the attribute to receive the UUID.")],
            [sg.Frame('One-to-Many Settings', repeating_element_frame, font='Arial 9 bold')]
        ], font="Arial 10 bold")], [sg.HSeparator()]]

    window.extend_layout(window["-OBJECTS_COLUMN-"], new_rows)
    window.refresh()
    window['-OBJECTS_COLUMN-'].contents_changed()


def load_data_in_thread(window, input_file):
    """
    Worker function to load data from any source and consistently create both a
    DataFrame for analysis and a flat intermediate XML file for transformation.
    """
    global TEMP_XML_FILE
    
    if TEMP_XML_FILE and os.path.exists(TEMP_XML_FILE):
        try: os.remove(TEMP_XML_FILE)
        except OSError: pass

    df = None
    xml_path = None
    sanitized_headers = None

    try:
        if input_file.lower().endswith('.csv'):
            separator = detect_csv_separator(input_file)
            window.write_event_value('-UPDATE_SEPARATOR-', separator)
            df = pd.read_csv(input_file, sep=separator, dtype=str, na_filter=False)
            xml_path, sanitized_headers = csv_to_xml(input_file, separator)

        elif input_file.lower().endswith('.json'):
            df = json_to_dataframe(input_file)
            if df is not None:
                xml_path, sanitized_headers = json_to_xml(input_file)

        elif input_file.lower().endswith('.xml'):
            df = flatten_xml_to_dataframe(input_file)
            if df is not None:
                sanitized_headers = df.columns.tolist()
                fd, temp_path = tempfile.mkstemp(suffix=".xml", text=True)
                os.close(fd)
                df.to_xml(temp_path, index=False, root_name='data', row_name='row')
                xml_path = temp_path
        
        TEMP_XML_FILE = xml_path
        
        if df is not None and sanitized_headers is not None:
            df = df.astype(str)
            preview_data = df.head(200).values.tolist()
            window.write_event_value('-DATA_LOADED-', (df, sanitized_headers, preview_data))
        else:
            window.write_event_value('-DATA_LOAD_FAILED-', "Could not create or process the input file.")

    except Exception as e:
        window.write_event_value('-DATA_LOAD_FAILED-', str(e))


# --- GUI Layout and Main Application ---

sg.theme('greenMono')

window_icon_b64 = b'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'


# --- Tab 1: Input Analyser Layout ---
input_analyser_tab_layout = [
    [sg.Text("Input Analyser", font=("Arial", 12, "bold"))],
    [sg.Text("Analyse an input file to preview its data and select the hierarchy keys.")],
    [sg.HSeparator()],
    [
        sg.Column([
            [sg.Frame("Select Hierarchy & Repetition", [
                [sg.Text("Level 1 Key (Parent):", size=(18,1)), sg.Combo([], key='-A_KEY1_SELECT-', size=(25,1), readonly=True), 
                 sg.Text("Repetition Trigger:", size=(15,1)), sg.Combo([], key='-A_OTM_TRIGGER1-', size=(25,1), readonly=True)],
                [sg.Text("Level 2 Key (Child):", size=(18,1)), sg.Combo([], key='-A_KEY2_SELECT-', size=(25,1), readonly=True),
                 sg.Text("Repetition Trigger:", size=(15,1)), sg.Combo([], key='-A_OTM_TRIGGER2-', size=(25,1), readonly=True)],
                [sg.Text("Level 3 Key (Sub-Child):", size=(18,1)), sg.Combo([], key='-A_KEY3_SELECT-', size=(25,1), readonly=True),
                 sg.Text("Repetition Trigger:", size=(15,1)), sg.Combo([], key='-A_OTM_TRIGGER3-', size=(25,1), readonly=True)],
            ])]
        ]),
        sg.VSeperator(),
        sg.Column([
            [sg.Frame("Quick Statistics", [
                [sg.Table(values=[], headings=['Column', 'TotalCount', 'UniqueCount'],
                          key='-A_STATS_TABLE-', num_rows=4, auto_size_columns=False, col_widths=[20,10,10])],
                [sg.Text('Duplicate Rows Found: N/A', key='-A_DUPLICATE_COUNT-')],
                [sg.Text("Output Folder for Report:", size=(22,1))],
                [sg.Input(str(HOME), key='-A_OUTPUT_FOLDER-', size=(40,1)), sg.FolderBrowse()],
                [sg.Button('Save Full Statistics Report', key='-A_SAVE_STATS-', disabled=True, size=(25,1))]
            ])]
        ])
    ],

    [
        sg.Button('Preview as Table', key='-A_PREVIEW_TABLE-', disabled=True),
        sg.Button('Preview as Hierarchy', key='-A_PREVIEW_HIERARCHY-', disabled=True),
        sg.Button('Use These Keys in Mapper', key='-A_USE_KEYS-', disabled=True, size=(30,1), font=("Arial", 10, "bold"))
    ],
    
    [sg.HSeparator()],
    [sg.Text("Data Preview:", key='-A_PREVIEW_LABEL-')],
    [sg.Multiline(size=(100, 20), key='-A_DATA_PREVIEW-', font=('Courier New', 10), 
                  expand_x=True, expand_y=True, 
                  wrap_lines=False, horizontal_scroll=True)],
]

col1 = [
    [sg.Text("1. Load XSD File along with Input File (above)", font=("Arial", 12, "bold"))],
    [sg.Text("XSD File:", size=(10,1)), sg.Input(key="-XSD_FILE-", enable_events=True, tooltip=".xsd"), sg.FileBrowse(file_types=(("XSD Files", "*.xsd"),))],
    [sg.HSeparator()],
    [sg.Text("2. Define Object Structure NB: Don't map key headers here --> 3.", font=("Arial", 12, "bold"))],
    [sg.Text("Object Name:*"), sg.Combo(values=[], size=(30, 1), key='-OBJECT_NAME-', readonly=False, tooltip="Name of the Object Type that pops up in 3. Config. XSLT Hierarchy.")],
    [sg.Text("Mappings for this Object:"), sg.Button("Clear Mappings", key="-CLEAR_MAPPINGS-", size=(15,1))],
    [sg.Listbox(values=[], size=(60, 15), key='-MAPPING_LIST-', background_color='lightyellow')],
    [sg.Text("Add New Simple Mapping:")],
    [sg.Text("-> XSD Element:*", size=(15,1)), sg.Combo(values=[], size=(30, 1), key='-SIMPLE_XSD_ELEMENT-')],
    [sg.Radio('From Input Header:', 'SIMPLE_VAL_TYPE', key='-SIMPLE_IS_HEADER-', default=True, enable_events=True), sg.Combo(values=[], size=(25, 1), key='-SIMPLE_HEADER_VALUE-')],
    [sg.Radio('Use Fixed Value:', 'SIMPLE_VAL_TYPE', key='-SIMPLE_IS_FIXED-', enable_events=True), sg.Input(key='-SIMPLE_FIXED_VALUE-', size=(27, 1), disabled=True)],

    [sg.Frame("Attribute (Optional)", 
        [
            [sg.Checkbox('Add Attribute', key='-SIMPLE_ADD_ATTRIBUTE-', enable_events=True, disabled=True)],
            [sg.Text("Name:"), sg.Combo([], key='-SIMPLE_ATTR_NAME-', size=(15,1), disabled=True)],
            [sg.Radio('From Header', 'SIMPLE_ATTR_TYPE', key='-SIMPLE_ATTR_IS_HEADER-', default=True, disabled=True, enable_events=True), sg.Combo([], key='-SIMPLE_ATTR_HEADER_VALUE-', size=(15,1), disabled=True)],
            [sg.Radio('Fixed Value', 'SIMPLE_ATTR_TYPE', key='-SIMPLE_ATTR_IS_FIXED-', disabled=True, enable_events=True), sg.Input(key='-SIMPLE_ATTR_FIXED_VALUE-', size=(15,1), disabled=True)]
        ]
    )],
    
    [sg.Button("Add Simple Mapping", key="-ADD_MAPPING-"), sg.Button("Create Complex Element", key="-CREATE_COMPLEX-")],
    [sg.HSeparator()],
    [sg.Button("Create/Update Object Definition", key="-CREATE_OBJECT-", button_color=('black', 'lightgreen'))],
    [sg.Text("Defined Objects Library:")],
    [sg.Listbox(values=[], size=(60, 4), key='-OBJECT_LIST-', background_color='lightgreen')],
]

col2 = [
    [sg.Text("3. Configure XSLT Hierarchy", font=("Arial", 12, "bold"))],
    [sg.Text("targetNamespace:", size=(16, 1)), sg.Input(key='-XML_NAMESPACE-', size=(35, 1))],
    [sg.Text("Root Element:*", size=(16, 1)), sg.Combo(values=[], size=(30, 1), key='-ROOT_ELEMENT-', readonly=False)],
    [sg.Button("Add New Object Configuration", key="-CREATE_NEW_OBJECT-")],
    [sg.Column([], key="-OBJECTS_COLUMN-", scrollable=True, vertical_scroll_only=True, expand_x=True, size=(None, 400))],
    [sg.HSeparator()],
    [sg.Text("4. Generate Files", font=("Arial", 12, "bold"))],
    [sg.Text("Output Folder:*"), sg.Input(str(HOME), key="-XSLT_OUT_FOLDER-"), sg.FolderBrowse()],
    [sg.Text("XSLT Filename:*"), sg.Input("xsl_transform.xsl", key="-XSLT_OUT_FILENAME-")],
    [sg.Checkbox("Generate, Transform, and Validate in one go", key="-FULL_WORKFLOW-", default=True)],
    [sg.Checkbox("Generate UUIDs for System IDs", key="-GENERATE_UUIDS-", default=True, tooltip="If checked, adds UUIDs to the attributes defined in 'System ID Attr Name' after transformation.")],
    [sg.Button("Generate XSLT", key="-GENERATE_XSLT-", button_color=('black', 'lightblue'), size=(30, 2), font=("Arial", 12, "bold"))]
]

mapper_tab_layout = [[sg.Column(col1, vertical_alignment='top'), sg.VSeperator(), sg.Column(col2, vertical_alignment='top')]]

# --- Tab 3: Transformer & Validator Layout---
transform_tab_layout = [
    [sg.Text("Manual Transformation with optional xsd validation", font=("Arial", 12, "bold"))],
    [sg.Text("This tab can be used to run transformations with existing XSLT files.")],
    [sg.HSeparator()],
    [sg.Text("XSLT Stylesheet*", size=(20,1)), sg.Input(key='-T_XSLT_IN-'), sg.FileBrowse(file_types=(("XSLT Files", "*.xsl *.xslt"),))],
    [sg.Text("XSD Schema (Optional)", size=(20,1)), sg.Input(key='-T_XSD_IN-'), sg.FileBrowse(file_types=(("XSD Files", "*.xsd"),))],
    [sg.HSeparator()],
    [sg.Text("Output XML Filename*", size=(20,1)), sg.Input("metadata.xml", key='-T_XML_OUT_NAME-')],
    [sg.Text("Output Folder*", size=(20,1)), sg.Input(str(HOME), key='-T_OUTPUT_FOLDER-'), sg.FolderBrowse()],
    [sg.Button("Run Transformation", key="-RUN_TRANSFORM-", button_color=('black', 'lightblue'), size=(20,2), font=("Arial", 12, "bold"))],
]

# --- Tab 4 Validator Layout ---
validate_tab_layout = [
    [sg.Text("Manual Validation", font=("Arial", 12, "bold"))],
    [sg.Text("Validate any CSV or XML file against an XSD or Schematron (SCH) schema.")],
    [sg.HSeparator()],
    [sg.Text("File to Validate (CSV/XML)*", size=(22,1)), 
     sg.Input(key='-V_INPUT_FILE-'), 
     sg.FileBrowse(file_types=(("XML Files", "*.xml"), ("CSV Files", "*.csv"),))],
    [sg.Text("CSV Separator", size=(22,1)), 
     sg.Combo([';', ',', ':', '|', '\t'], default_value=';', size=10, key='-V_SEPARATOR-')],
    [sg.Text("Schema File (XSD/SCH)*", size=(22,1)), 
     sg.Input(key='-V_SCHEMA_FILE-'), 
     sg.FileBrowse(file_types=(("Schema Files", "*.xsd *.sch"), ("All Files", "*.*")))],
    [sg.Text("Output Folder for Report*", size=(22,1)), 
     sg.Input(str(HOME), key='-V_OUTPUT_FOLDER-'), sg.FolderBrowse()],
    [sg.HSeparator()],
    [sg.Button("Run Validation", key="-RUN_VALIDATION-", button_color=('black', 'lightblue'), size=(20,2), font=("Arial", 12, "bold"))],
]

# --- Tab 5 Placeholder for FGS Buddy ---
package_tab_layout = [
    [sg.Text("FGS Buddy", font=("Arial", 12, "bold"))],
    [sg.Text("This tab is for now just a reference to FGS Buddy: https://github.com/Viktor-Lundberg/FGSBuddy")],
    [sg.Text('See help menu above for link.')],
]

# --- Main Window Layout ---
menu_def = [['File', ['Exit']],
            ['Help', ['FGS Documentation', 'DILCIS Board', 'FGS Buddy on GitHub', 'About...']]]

layout = [[sg.Menu(menu_def)],
          
          [sg.Frame('Input File All Tabs (CSV, XML, JSON):', [
               [sg.Input(key='-INPUT_FILE-', enable_events=True), 
               sg.FileBrowse(file_types=(("Input Files", "*.csv *.json *.xml"), ("All Files", "*.*"))),
               sg.Text("CSV Separator:"), #, size=(12,1)
               sg.Combo([';', ',', ':', '|', '\t'], default_value=';', size=10, key='-SEPARATOR-')],
          ], expand_x=True)],
          
          [sg.TabGroup([[
              sg.Tab('Input Analyser', input_analyser_tab_layout, key='-TAB1-'),
              sg.Tab('XSLT Mapper', mapper_tab_layout, key='-TAB2-'),
              sg.Tab('Transformer', transform_tab_layout, key='-TAB3-'),
              sg.Tab('Validator', validate_tab_layout, key='-TAB4-'),
			  sg.Tab('Package Creator (SIP)', package_tab_layout, key='-TAB5-')
          ]], key='-TABGROUP-')],
          
          [sg.Text("Output log:")],
          [sg.Output(size=(120, 15), font='Consolas 8', key='-OUTPUT-')]]

window = sg.Window(f"FGS Buddysbuddy v{VERSION}", layout, resizable=True, finalize=True, icon=window_icon_b64)

# --- Main Event Loop ---
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    if isinstance(event, str):
        if event.startswith('-COMBINE_KEY_'):
            config_num = event.split('_')[-1]
            window[f'-KEY_SEPARATOR_{config_num}'].update(disabled=not values[event])
        elif event.startswith('-REPEAT_ENABLE_'):
            config_num = event.split('_')[-1]
            is_checked = values[event]
            window[f'-REPEAT_OBJECT_TYPE_{config_num}'].update(disabled=not is_checked)
            window[f'-REPEAT_CSV_TRIGGER_{config_num}'].update(disabled=not is_checked)

    # --- Menu Events ---
    if event == 'About...':
        show_buddy_window()
    elif event == 'FGS Documentation':
        webbrowser.open('https://riksarkivet.se/faststallda-kommande-fgser')
    elif event == 'DILCIS Board':
        webbrowser.open('https://dilcis.eu')
    elif event == 'FGS Buddy on GitHub':
        webbrowser.open('https://github.com/Viktor-Lundberg/FGSBuddy')
        
    if event == '-INPUT_FILE-':
        input_file = values['-INPUT_FILE-']
        if input_file and os.path.exists(input_file):
            window['-A_DATA_PREVIEW-'].update("Loading... Please wait...")
            threading.Thread(target=load_data_in_thread, args=(window, input_file), daemon=True).start()
            
    elif event == '-UPDATE_SEPARATOR-':
        window['-SEPARATOR-'].update(value=values[event])

    elif event == '-DATA_LOADED-':
        df, headers, data = values[event]
        full_df_for_analyser = df
        csv_headers_list = headers
        
        window['-A_PREVIEW_LABEL-'].update("Data Preview (first 200 rows):")
        window['-A_DATA_PREVIEW-'].update(df.head(200).to_string(line_width=5000))

        current_stats_data = calculate_statistics(df)
        if current_stats_data:
            totals_data = current_stats_data['totals_df'].reset_index().values.tolist()
            window['-A_STATS_TABLE-'].update(values=totals_data)
            num_dupes = current_stats_data['num_duplicates']
            window['-A_DUPLICATE_COUNT-'].update(f"Duplicate Rows Found: {num_dupes}")
            window['-A_SAVE_STATS-'].update(disabled=False)

        suggested_keys = suggest_keys(df)
        key1_sugg = suggested_keys[0] if len(suggested_keys) > 0 else ""
        key2_sugg = suggested_keys[1] if len(suggested_keys) > 1 else ""
        key3_sugg = suggested_keys[2] if len(suggested_keys) > 2 else ""
        
        headers_with_blank = [''] + headers
        window['-A_KEY1_SELECT-'].update(values=headers_with_blank, value=key1_sugg)
        window['-A_KEY2_SELECT-'].update(values=headers_with_blank, value=key2_sugg)
        window['-A_KEY3_SELECT-'].update(values=headers_with_blank, value=key3_sugg)
        
        window['-A_OTM_TRIGGER1-'].update(values=headers_with_blank, value='')
        window['-A_OTM_TRIGGER2-'].update(values=headers_with_blank, value='')
        window['-A_OTM_TRIGGER3-'].update(values=headers_with_blank, value='')

        window['-A_PREVIEW_TABLE-'].update(disabled=False)
        window['-A_PREVIEW_HIERARCHY-'].update(disabled=(len(suggested_keys) == 0))
        window['-A_USE_KEYS-'].update(disabled=(len(suggested_keys) == 0))
        
        print(f"✅ Loaded {len(df)} rows and {len(headers)} columns for analysis.")
        
        print("Updating XSLT Mapper dropdowns...")
        if TEMP_XML_FILE and os.path.exists(TEMP_XML_FILE):
             xsd_elements_list_from_xml = get_elements_from_xml(TEMP_XML_FILE)
             window["-SIMPLE_XSD_ELEMENT-"].update(values=xsd_elements_list_from_xml)
        
        window["-SIMPLE_HEADER_VALUE-"].update(values=csv_headers_list)
        window["-SIMPLE_ATTR_HEADER_VALUE-"].update(values=csv_headers_list)
        for i in range(1, object_count + 1):
            window[f'-ID_CSV_{i}-'].update(values=csv_headers_list)
            window[f'-SYSID_XSD_{i}-'].update(values=csv_headers_list)
            window[f'-REPEAT_CSV_TRIGGER_{i}-'].update(values=csv_headers_list)

        print(f"✅ Analysis complete. {len(df)} rows loaded.")

    elif event == '-DATA_LOAD_FAILED-':
        error_message = values[event]
        sg.popup_error(f"Failed to load the file.\n\nError: {error_message}", icon=window_icon_b64, keep_on_top=True)
        window['-A_DATA_PREVIEW-'].update("Error: Could not load file.")
        window['-A_PREVIEW_TABLE-'].update(disabled=True)
        window['-A_PREVIEW_HIERARCHY-'].update(disabled=True)
        window['-A_USE_KEYS-'].update(disabled=True)
        window['-A_SAVE_STATS-'].update(disabled=True)

    # --- Analyser Tab Events ---
    elif values['-TABGROUP-'] == '-TAB1-':
        if event == '-A_SAVE_STATS-':
            if current_stats_data:
                output_folder = values['-A_OUTPUT_FOLDER-']
                if output_folder and os.path.isdir(output_folder):
                    save_statistics_report(current_stats_data, output_folder)
                else:
                    sg.popup_error("Please select a valid output folder first.", icon=window_icon_b64, keep_on_top=True)
            else:
                sg.popup_error("No statistics data to save. Please load a file first.", icon=window_icon_b64, keep_on_top=True)
                
        elif event == '-A_PREVIEW_TABLE-':
            if full_df_for_analyser is not None:
                window['-A_PREVIEW_LABEL-'].update("Data Preview (first 200 rows):")
                window['-A_DATA_PREVIEW-'].update(full_df_for_analyser.head(200).to_string(line_width=5000))
            else:
                sg.popup_error("Please load a file first.", icon=window_icon_b64, keep_on_top=True)

        elif event == '-A_PREVIEW_HIERARCHY-':
            if full_df_for_analyser is not None:
                keys = [values['-A_KEY1_SELECT-'], values['-A_KEY2_SELECT-'], values['-A_KEY3_SELECT-']]
                triggers = [values['-A_OTM_TRIGGER1-'], values['-A_OTM_TRIGGER2-'], values['-A_OTM_TRIGGER3-']]
                active_keys = [k for k in keys if k]

                if not active_keys:
                    sg.popup_error("Please select at least one Hierarchy Key to preview the hierarchy.", icon=window_icon_b64, keep_on_top=True)
                    continue

                preview_text = format_hierarchy_view(full_df_for_analyser, active_keys, triggers)
                window['-A_PREVIEW_LABEL-'].update("Hierarchy Preview (first 500 rows):")
                window['-A_DATA_PREVIEW-'].update(preview_text)
            else:
                sg.popup_error("Please load a file first.", icon=window_icon_b64, keep_on_top=True)

        elif event == '-A_USE_KEYS-':
            object_count = 0

            window['-OBJECTS_COLUMN-'].update('')
                     
            keys = [values['-A_KEY1_SELECT-'], values['-A_KEY2_SELECT-'], values['-A_KEY3_SELECT-']]
            triggers = {
                1: values['-A_OTM_TRIGGER1-'],
                2: values['-A_OTM_TRIGGER2-'],
                3: values['-A_OTM_TRIGGER3-']
            }
            keys_to_use = [k for k in keys if k]

            if not keys_to_use:
                sg.popup_error("No hierarchy keys were selected.", icon=window_icon_b64, keep_on_top=True)
                continue
            
            print(f"--- Sending {len(keys_to_use)} key(s) to the XSLT Mapper ---")
            for i, key in enumerate(keys_to_use):
                level = i + 1
                onetomany_trigger = triggers.get(level)
                add_new_config_frame(window, preselected_key=key, onetomany_trigger=onetomany_trigger)
            
            window['-TAB2-'].select()

    elif values['-TABGROUP-'] == '-TAB2-':

       if event == '-SIMPLE_IS_HEADER-':
           window['-SIMPLE_HEADER_VALUE-'].update(disabled=False)
           window['-SIMPLE_FIXED_VALUE-'].update(disabled=True)
           window['-SIMPLE_ADD_ATTRIBUTE-'].update(disabled=False)
       elif event == '-SIMPLE_IS_FIXED-':
           window['-SIMPLE_HEADER_VALUE-'].update(disabled=True)
           window['-SIMPLE_FIXED_VALUE-'].update(disabled=False)
           window['-SIMPLE_ADD_ATTRIBUTE-'].update(disabled=False)
       elif event == '-SIMPLE_ADD_ATTRIBUTE-':
           is_checked = values['-SIMPLE_ADD_ATTRIBUTE-']
           for k in ['-SIMPLE_ATTR_NAME-', '-SIMPLE_ATTR_IS_HEADER-', '-SIMPLE_ATTR_IS_FIXED-']:
               window[k].update(disabled=not is_checked)
           if is_checked:
               window['-SIMPLE_ATTR_HEADER_VALUE-'].update(disabled=not values['-SIMPLE_ATTR_IS_HEADER-'])
               window['-SIMPLE_ATTR_FIXED_VALUE-'].update(disabled=not values['-SIMPLE_ATTR_IS_FIXED-'])
       elif event == '-SIMPLE_ATTR_IS_HEADER-':
           window['-SIMPLE_ATTR_HEADER_VALUE-'].update(disabled=False)
           window['-SIMPLE_ATTR_FIXED_VALUE-'].update(disabled=True)
       elif event == '-SIMPLE_ATTR_IS_FIXED-':
           window['-SIMPLE_ATTR_HEADER_VALUE-'].update(disabled=True)
           window['-SIMPLE_ATTR_FIXED_VALUE-'].update(disabled=False)
       
       elif event == "-XSD_FILE-":
           xsd_path = values["-XSD_FILE-"]
           if xsd_path and os.path.exists(xsd_path):
               xsd_elements_list, namespace, root = load_xsd_isolated(xsd_path)
               
               window["-SIMPLE_XSD_ELEMENT-"].update(values=xsd_elements_list)
               window["-OBJECT_NAME-"].update(values=xsd_elements_list)
               window["-ROOT_ELEMENT-"].update(values=xsd_elements_list, value=root)
               window["-SIMPLE_ATTR_NAME-"].update(values=xsd_elements_list)
               window['-XML_NAMESPACE-'].update(namespace)
               
               for i in range(1, object_count + 1):
                   window[f'-ID_XSD_{i}-'].update(values=xsd_elements_list)
                   window[f'-SUB_ELEMENT_{i}-'].update(values=xsd_elements_list)
                   window[f'-SYSID_XSD_{i}-'].update(values=xsd_elements_list)

       elif event == "-CLEAR_MAPPINGS-":
           current_object_mappings.clear()
           window["-MAPPING_LIST-"].update(values=[])
       
       elif event == "-ADD_MAPPING-":
           target = values['-SIMPLE_XSD_ELEMENT-']
           is_header = values['-SIMPLE_IS_HEADER-']
           source = values['-SIMPLE_HEADER_VALUE-'] if is_header else values['-SIMPLE_FIXED_VALUE-']

           if not (source and target):
               sg.popup_error("Both Value and XSD Element must be provided.", icon=window_icon_b64, keep_on_top=True)
               continue
           
           mapping_data = {'type': 'simple', 'xsd': target, 'value': source, 'value_is_header': is_header}
           
           if values['-SIMPLE_ADD_ATTRIBUTE-']:
               attr_is_header = values['-SIMPLE_ATTR_IS_HEADER-']
               attr_name = values['-SIMPLE_ATTR_NAME-']
               attr_value = values['-SIMPLE_ATTR_HEADER_VALUE-'] if attr_is_header else values['-SIMPLE_ATTR_FIXED_VALUE-']

               if not (attr_name and attr_value):
                   sg.popup_error("Attribute Name and Value are required when checked.", icon=window_icon_b64, keep_on_top=True)
                   continue
               
               mapping_data['type'] = 'simple_with_attr'
               mapping_data['attribute'] = {'name': attr_name, 'value': attr_value, 'value_is_header': attr_is_header}

           current_object_mappings.append(mapping_data)

           new_display_list = []
           for m in current_object_mappings:
               if m.get('is_complex'):
                   new_display_list.append(f"Complex: {m['name']}")
               else: 
                   m_val_type = "Header" if m['value_is_header'] else "Fixed"
                   disp_str = f"Simple: {m['value']} ({m_val_type}) -> {m['xsd']}"
                   if m.get('attribute'):
                       attr = m['attribute']
                       a_val_type = "Header" if attr['value_is_header'] else "Fixed"
                       disp_str += f" [ATTR: {attr['name']}={attr['value']} ({a_val_type})]"
                   new_display_list.append(disp_str)
           
           window["-MAPPING_LIST-"].update(values=new_display_list)

       elif event == "-CREATE_COMPLEX-":
           complex_element = create_complex_element_window(xsd_elements_list, csv_headers_list)
           if complex_element:
               current_object_mappings.append(complex_element)
               new_display_list = []
               for m in current_object_mappings:
                   if m.get('is_complex'):
                       new_display_list.append(f"Complex: {m['name']}")
                   else:
                       m_val_type = "Header" if m['value_is_header'] else "Fixed"
                       disp_str = f"Simple: {m['value']} ({m_val_type}) -> {m['xsd']}"
                       if m.get('attribute'):
                           attr = m['attribute']
                           a_val_type = "Header" if attr['value_is_header'] else "Fixed"
                           disp_str += f" [ATTR: {attr['name']}={attr['value']} ({a_val_type})]"
                       new_display_list.append(disp_str)
               window["-MAPPING_LIST-"].update(values=new_display_list)

       elif event == "-CREATE_NEW_OBJECT-":
           add_new_config_frame(window)

       elif event == "-CREATE_OBJECT-":
           object_name = values['-OBJECT_NAME-']
           if not object_name:
               sg.popup_error("Object Name cannot be empty.", icon=window_icon_b64, keep_on_top=True)
           else:
               created_objects[object_name] = {'mappings': list(current_object_mappings), 'xsd_element': object_name}
               object_keys = list(created_objects.keys())
               window['-OBJECT_LIST-'].update(values=object_keys)
               for i in range(1, object_count + 1):
                   window[f'-OBJECT_TYPE_{i}-'].update(values=object_keys)
                   window[f'-REPEAT_OBJECT_TYPE_{i}-'].update(values=object_keys)
               
               current_object_mappings.clear()
               window['-MAPPING_LIST-'].update(values=[])
               window['-OBJECT_NAME-'].update(value='')
               sg.popup_quick_message(f"Object '{object_name}' saved!", auto_close_duration=2, icon=window_icon_b64, keep_on_top=True)

       elif event == "-GENERATE_XSLT-":
           if not created_objects or object_count == 0:
               sg.popup_error("Please define at least one object and configure its hierarchy first.", icon=window_icon_b64, keep_on_top=True)
               continue

           output_folder = values['-XSLT_OUT_FOLDER-']
           output_filename = values['-XSLT_OUT_FILENAME-']
           if not (output_folder and output_filename):
               sg.popup_error("XSLT Output Folder and Filename must be specified.", icon=window_icon_b64, keep_on_top=True)
               continue
           
           if not output_filename.lower().endswith(('.xsl', '.xslt')):
               output_filename += '.xsl'
           
           xslt_output_path = os.path.join(output_folder, output_filename)
           
           if not confirm_overwrite(xslt_output_path):
               continue

           success = generate_xslt_with_fstrings(created_objects, values, object_count, csv_headers_list, xslt_output_path)
           
           if success and values['-FULL_WORKFLOW-']:
               print("\n--- Starting Automated Workflow ---")
               
               if not TEMP_XML_FILE or not os.path.exists(TEMP_XML_FILE):
                   sg.popup_error("Cannot run full workflow: No intermediate XML file. Please select an input file first.", icon=window_icon_b64, keep_on_top=True)
                   continue
               
               final_xml_path = os.path.join(output_folder, "transformed_metadata.xml")

               if run_xslt_transform(TEMP_XML_FILE, xslt_output_path, final_xml_path):
                   if values['-GENERATE_UUIDS-']:
                       targets = []
                       for i in range(1, object_count + 1):
                           obj_type = values.get(f'-OBJECT_TYPE_{i}-')
                           sysid_name = values.get(f'-SYSID_XSD_{i}-')
                           if obj_type and sysid_name:
                               xsd_element = created_objects[obj_type].get('xsd_element', obj_type)
                               targets.append((xsd_element, sysid_name))
                       
                       add_uuids_to_xml(final_xml_path, targets)

                   xsd_file = values['-XSD_FILE-']
                   if xsd_file and os.path.exists(xsd_file):
                       run_xml_schema_validation(final_xml_path, xsd_file)
                   else:
                       print("ℹ️ Skipping validation: No XSD schema file provided.")

    # --- Transformer Tab Events ---
    elif values['-TABGROUP-'] == '-TAB3-':

        if event == "-RUN_TRANSFORM-":
            xslt_in = values['-T_XSLT_IN-']
            xsd_in = values['-T_XSD_IN-']
            out_name = values['-T_XML_OUT_NAME-']
            out_folder = values['-T_OUTPUT_FOLDER-']

            if not (xslt_in and out_name and out_folder):
                sg.popup_error("Please fill all required fields: XSLT, Output Filename, and Output Folder.", icon=window_icon_b64, keep_on_top=True)
                continue
                
            if not TEMP_XML_FILE or not os.path.exists(TEMP_XML_FILE):
                sg.popup_error("Please load an input file using the 'Input File' field at the top first.", icon=window_icon_b64, keep_on_top=True)
                continue
            
            print("\n--- Starting Manual Transformation ---")
            
            final_xml_output_path = os.path.join(out_folder, out_name)
            if run_xslt_transform(TEMP_XML_FILE, xslt_in, final_xml_output_path):
                if xsd_in and os.path.exists(xsd_in):
                    run_xml_schema_validation(final_xml_output_path, xsd_in)
                else:
                    print("ℹ️ Skipping validation: No XSD schema file provided.")

    # --- Validator Tab Events ---
    elif values['-TABGROUP-'] == '-TAB4-':
        if event == "-RUN_VALIDATION-":
            input_file = values['-V_INPUT_FILE-']
            schema_file = values['-V_SCHEMA_FILE-']
            output_folder = values['-V_OUTPUT_FOLDER-']

            if not (input_file and schema_file):
                sg.popup_error("Please provide both a 'File to Validate' and a 'Schema File'.", icon=window_icon_b64, keep_on_top=True)
                continue
            
            xml_to_validate = None
            is_temp_file = False
            
            if input_file.lower().endswith('.csv'):
                separator = values['-V_SEPARATOR-']
                xml_to_validate, _ = csv_to_xml(input_file, separator)
                is_temp_file = True
            elif input_file.lower().endswith('.xml'):
                xml_to_validate = input_file
            
            if xml_to_validate:
                print("\n--- Starting Validation ---")
                if schema_file.lower().endswith('.xsd'):
                    run_xml_schema_validation(xml_to_validate, schema_file)
                elif schema_file.lower().endswith('.sch'):
                    run_schematron_validation(xml_to_validate, schema_file, output_folder)
                
                if is_temp_file and os.path.exists(xml_to_validate):
                    os.remove(xml_to_validate)

window.close()

if TEMP_XML_FILE and os.path.exists(TEMP_XML_FILE):
    try:
        os.remove(TEMP_XML_FILE)
        print("Final cleanup: Removed application temporary XML file.")
    except OSError as e:
        print(f"Error during final cleanup of temp file: {e}")
