"""
Configurações do sistema Trelliq Python.
"""

from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Responsavel:
    username: str
    nome: str

@dataclass
class GrupoMarketing:
    name: str
    responsaveis: List[Responsavel]
    etapas_abertura: List[str]
    etapas_finalizacao: List[str]
    etapa_feito: List[str]
    color: str

# Criadores de conteúdo que têm lógica específica de conclusão
CONTENT_CREATORS = ['leonardoferreiracardoso5', 'jamillyfreitass']

# Configuração dos 4 grupos de marketing conforme o sistema TypeScript
GRUPOS_MARKETING = [
    GrupoMarketing(
        name='Grupo 1',
        responsaveis=[
            Responsavel(username='jamillyfreitass', nome='Jamily'),
            Responsavel(username='leonardoferreiracardoso5', nome='Leo')
        ],
        etapas_abertura=['EM PROCESSO DE CONTEÚDO'],
        etapas_finalizacao=['EM PROCESSO DE MONTAGEM', 'EM PROCESSO DE ENVIO'],
        etapa_feito=['FEITOS', 'FEITO'],
        color='#4F8EF7'
    ),
    GrupoMarketing(
        name='Grupo 2',
        responsaveis=[
            Responsavel(username='fazstudioart', nome='Luiz'),
            Responsavel(username='miguelluis30', nome='Miguel')
        ],
        etapas_abertura=['PROCESSO DE CRIAÇÃO'],
        etapas_finalizacao=['EM PROCESSO DE MONTAGEM', 'EM PROCESSO DE ENVIO'],
        etapa_feito=['FEITOS', 'FEITO'],
        color='#00B894'
    ),
    GrupoMarketing(
        name='Grupo 3',
        responsaveis=[
            Responsavel(username='samuelpiske1', nome='Samuel')
        ],
        etapas_abertura=['PROCESSO DE GRAVAÇÃO', 'EDIÇÃO'],
        etapas_finalizacao=['EM PROCESSO DE MONTAGEM', 'EM PROCESSO DE ENVIO'],
        etapa_feito=['FEITOS', 'FEITO'],
        color='#FDCB6E'
    ),
    GrupoMarketing(
        name='Grupo 4',
        responsaveis=[
            Responsavel(username='flaviasilva', nome='Flávia'),
            Responsavel(username='coordenacao', nome='Coordenação')
        ],
        etapas_abertura=['EM PROCESSO DE QUALIDADE', 'EM PROCESSO DE EDIÇÃO E REVISÃO'],
        etapas_finalizacao=['EM PROCESSO DE MONTAGEM', 'EM PROCESSO DE ENVIO'],
        etapa_feito=['FEITOS', 'FEITO'],
        color='#E17055'
    )
]

# Mapeamento das listas do Trello para status
LIST_STATUS_MAP = {
    'PLANEJANDO ESTRATÉGIAS': 'Planejamento',
    'ATIVIDADES RECORRENTES': 'Recorrente',
    'EM PROCESSO DE CONTEÚDO': 'Em Andamento',
    'EM PROCESSO DE QUALIDADE': 'Em Andamento',
    'EM PROCESSO DE EDIÇÃO E REVISÃO': 'Em Andamento',
    'EM PROCESSO DE MONTAGEM': 'Em Andamento',
    'EM PROCESSO DE REVISÃO': 'Em Andamento',
    'AGUARDANDO RETORNO DE CORREÇÕES': 'Bloqueada',
    'EM PROCESSO DE ENVIO': 'Em Andamento',
    'FEITO': 'Concluída',
    'FEITOS': 'Concluída'  # Variação plural
}

# Configurações do Streamlit
STREAMLIT_CONFIG = {
    'page_title': 'Trelliq - Relatórios de Marketing',
    'page_icon': '📊',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Status possíveis das tarefas
TASK_STATUSES = [
    'Concluída',
    'Em Andamento', 
    'Atrasada',
    'Bloqueada',
    'Planejamento',
    'Recorrente',
    'Ignorada'
]

# Cores para os status
STATUS_COLORS = {
    'Concluída': '#28a745',
    'Em Andamento': '#007bff',
    'Atrasada': '#dc3545',
    'Bloqueada': '#ffc107',
    'Planejamento': '#6c757d',
    'Recorrente': '#17a2b8',
    'Ignorada': '#6c757d'
}

def get_grupo_por_responsavel(username: str) -> GrupoMarketing | None:
    """Encontra o grupo de um responsável pelo username."""
    for grupo in GRUPOS_MARKETING:
        for responsavel in grupo.responsaveis:
            if responsavel.username == username:
                return grupo
    return None

def get_etapa_atual(list_name: str) -> str:
    """Obtém a etapa atual baseada no nome da lista."""
    return list_name.upper()

def is_finalizada_para_flavia(list_name: str, grupo: GrupoMarketing | None) -> bool:
    """Verifica se a tarefa está finalizada para Flávia."""
    if not grupo:
        return False
    etapa = get_etapa_atual(list_name)
    return any(etapa_fin in etapa for etapa_fin in grupo.etapas_finalizacao)

def is_feita(list_name: str, grupo: GrupoMarketing | None) -> bool:
    """Verifica se a tarefa está feita."""
    if not grupo:
        return False
    etapa = get_etapa_atual(list_name)
    return any(etapa_feito in etapa for etapa_feito in grupo.etapa_feito)

def is_em_revisao(list_name: str) -> bool:
    """Verifica se a tarefa está em revisão."""
    return 'REVISÃO' in get_etapa_atual(list_name)
