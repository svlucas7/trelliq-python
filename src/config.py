"""
Configurações dos grupos de marketing e parâmetros do sistema.
"""

from typing import Dict, List, Any

# Configuração dos 4 grupos de marketing
GRUPOS_MARKETING = {
    "Grupo 1": {
        "nome": "Criadores de Conteúdo",
        "responsaveis": ["lucas.silva", "maria.santos", "joao.oliveira"],
        "etapas": ["Ideação", "Criação", "Revisão"],
        "cor": "#E74C3C"  # Vermelho
    },
    "Grupo 2": {
        "nome": "Social Media",
        "responsaveis": ["ana.costa", "pedro.lima", "carla.ferreira"],
        "etapas": ["Planejamento", "Publicação", "Engajamento"],
        "cor": "#3498DB"  # Azul
    },
    "Grupo 3": {
        "nome": "Análise e Relatórios",
        "responsaveis": ["rafael.souza", "julia.martins", "bruno.alves"],
        "etapas": ["Coleta", "Análise", "Relatório"],
        "cor": "#27AE60"  # Verde
    },
    "Grupo 4": {
        "nome": "Flávia + Coordenação",
        "responsaveis": ["flavia.coordenacao", "equipe.gestao"],
        "etapas": ["Coordenação", "Supervisão", "Aprovação"],
        "cor": "#F39C12"  # Laranja
    }
}

# Mapeamento de status do Trello
STATUS_MAPPING = {
    "A Fazer": "pendente",
    "To Do": "pendente",
    "Backlog": "pendente",
    "Em Progresso": "andamento",
    "In Progress": "andamento",
    "Fazendo": "andamento",
    "Revisão": "revisao",
    "Review": "revisao",
    "Em Revisão": "revisao",
    "Concluído": "concluido",
    "Done": "concluido",
    "Finalizado": "concluido",
    "Arquivado": "arquivado"
}

# Configurações de exportação
EXPORT_CONFIG = {
    "excel": {
        "sheet_names": {
            "tasks": "Relatório de Tarefas",
            "collaborators": "Análise de Colaboradores", 
            "summary": "Resumo Executivo",
            "metrics": "Métricas Avançadas"
        },
        "formatting": {
            "header_color": "#2C3E50",
            "header_font_color": "#FFFFFF",
            "date_format": "dd/mm/yyyy"
        }
    },
    "charts": {
        "default_height": 400,
        "color_palette": ["#E74C3C", "#3498DB", "#27AE60", "#F39C12", "#9B59B6", "#E67E22"]
    }
}

# Configurações da aplicação Streamlit
STREAMLIT_CONFIG = {
    "page_title": "Trelliq - Relatórios de Marketing",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Validações de dados
DATA_VALIDATION = {
    "required_fields": ["id", "name", "list", "members"],
    "date_formats": ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d", "%d/%m/%Y"],
    "max_file_size_mb": 10
}
