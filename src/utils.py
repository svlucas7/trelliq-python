"""
Utilitários gerais para o sistema Trelliq Python.
Funções auxiliares para formatação, validação e criação de elementos visuais.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional, Tuple
import streamlit as st
from datetime import datetime
import base64
import io

def format_number(value: int) -> str:
    """Formata número para exibição com separadores."""
    return f"{value:,}".replace(",", ".")

def format_percentage(value: float) -> str:
    """Formata percentual para exibição."""
    return f"{value:.1f}%"

def create_download_link(df: pd.DataFrame, filename: str, link_text: str = "📥 Download") -> str:
    """
    Cria link de download para DataFrame como CSV.
    
    Args:
        df: DataFrame para download
        filename: Nome do arquivo
        link_text: Texto do link
        
    Returns:
        HTML do link de download
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def create_status_pie_chart(status_data: Dict[str, int], title: str = "Distribuição de Status") -> go.Figure:
    """
    Cria gráfico de pizza para distribuição de status.
    
    Args:
        status_data: Dicionário com contagem por status
        title: Título do gráfico
        
    Returns:
        Figura Plotly
    """
    if not status_data:
        return go.Figure()
    
    labels = list(status_data.keys())
    values = list(status_data.values())
    
    colors = {
        'pendente': '#E74C3C',
        'andamento': '#F39C12', 
        'revisao': '#3498DB',
        'concluido': '#27AE60',
        'arquivado': '#95A5A6'
    }
    
    chart_colors = [colors.get(label, '#BDC3C7') for label in labels]
    
    fig = px.pie(
        values=values,
        names=labels,
        title=title,
        color_discrete_sequence=chart_colors
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=True,
        height=400,
        font=dict(size=12)
    )
    
    return fig

def create_group_bar_chart(group_data: Dict[str, int], title: str = "Tarefas por Grupo") -> go.Figure:
    """
    Cria gráfico de barras para distribuição por grupos.
    
    Args:
        group_data: Dicionário com contagem por grupo
        title: Título do gráfico
        
    Returns:
        Figura Plotly
    """
    if not group_data:
        return go.Figure()
    
    groups = list(group_data.keys())
    counts = list(group_data.values())
    
    colors = ['#E74C3C', '#3498DB', '#27AE60', '#F39C12']
    
    fig = px.bar(
        x=groups,
        y=counts,
        title=title,
        color=groups,
        color_discrete_sequence=colors
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Tarefas: %{y}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Grupos",
        yaxis_title="Número de Tarefas",
        font=dict(size=12)
    )
    
    return fig

def create_collaborator_chart(collab_data: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """
    Cria gráfico de colaboradores mais ativos.
    
    Args:
        collab_data: DataFrame com dados de colaboradores
        top_n: Número de top colaboradores a mostrar
        
    Returns:
        Figura Plotly
    """
    if collab_data.empty:
        return go.Figure()
    
    # Pega top N colaboradores
    top_collabs = collab_data.nlargest(top_n, 'total_tasks')
    
    fig = px.bar(
        top_collabs,
        x='total_tasks',
        y='colaborador',
        orientation='h',
        title=f"Top {top_n} Colaboradores Mais Ativos",
        color='total_tasks',
        color_continuous_scale='viridis'
    )
    
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Tarefas: %{x}<extra></extra>'
    )
    
    fig.update_layout(
        height=max(400, top_n * 40),
        xaxis_title="Número de Tarefas",
        yaxis_title="Colaboradores",
        showlegend=False,
        font=dict(size=12)
    )
    
    return fig

def create_progress_metrics(metrics: Dict[str, Any]) -> go.Figure:
    """
    Cria dashboard de métricas de progresso.
    
    Args:
        metrics: Dicionário com métricas do projeto
        
    Returns:
        Figura Plotly com subplots
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            'Taxa de Conclusão',
            'Cards Ativos vs Total',
            'Distribuição por Status',
            'Colaboradores Únicos'
        ],
        specs=[
            [{'type': 'indicator'}, {'type': 'bar'}],
            [{'type': 'pie'}, {'type': 'indicator'}]
        ]
    )
    
    # Taxa de conclusão
    completion_rate = metrics.get('completion_rate', 0)
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=completion_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Taxa de Conclusão (%)"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#27AE60"},
                'steps': [
                    {'range': [0, 50], 'color': "#E74C3C"},
                    {'range': [50, 80], 'color': "#F39C12"},
                    {'range': [80, 100], 'color': "#27AE60"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ),
        row=1, col=1
    )
    
    # Cards ativos vs total
    total_cards = metrics.get('total_cards', 0)
    active_cards = metrics.get('active_cards', 0)
    
    fig.add_trace(
        go.Bar(
            x=['Total', 'Ativos'],
            y=[total_cards, active_cards],
            marker_color=['#3498DB', '#27AE60'],
            name='Cards'
        ),
        row=1, col=2
    )
    
    # Distribuição por status
    status_dist = metrics.get('status_distribution', {})
    if status_dist:
        fig.add_trace(
            go.Pie(
                labels=list(status_dist.keys()),
                values=list(status_dist.values()),
                name='Status'
            ),
            row=2, col=1
        )
    
    # Colaboradores únicos
    unique_collaborators = metrics.get('unique_collaborators', 0)
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=unique_collaborators,
            title={'text': "Colaboradores Únicos"},
            number={'font': {'size': 40, 'color': '#2C3E50'}}
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="Dashboard de Métricas",
        title_x=0.5
    )
    
    return fig

def format_dataframe_for_display(df: pd.DataFrame, max_rows: int = 100) -> pd.DataFrame:
    """
    Formata DataFrame para exibição no Streamlit.
    
    Args:
        df: DataFrame original
        max_rows: Número máximo de linhas a exibir
        
    Returns:
        DataFrame formatado
    """
    if df.empty:
        return df
    
    # Limita número de linhas
    df_display = df.head(max_rows).copy()
    
    # Formata colunas de data
    date_columns = ['created_date', 'due_date']
    for col in date_columns:
        if col in df_display.columns:
            df_display[col] = pd.to_datetime(df_display[col]).dt.strftime('%d/%m/%Y')
    
    # Formata listas como strings
    list_columns = ['members', 'task_names', 'top_status']
    for col in list_columns:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else str(x)
            )
    
    return df_display

def download_excel_link(df_dict: Dict[str, pd.DataFrame], filename: str) -> str:
    """
    Cria link de download para arquivo Excel.
    
    Args:
        df_dict: Dicionário com DataFrames para cada aba
        filename: Nome do arquivo
        
    Returns:
        String com link de download base64
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📥 Download Excel</a>'
    return href

def validate_json_structure(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida estrutura do JSON do Trello.
    
    Args:
        data: Dados JSON carregados
        
    Returns:
        Tupla (válido, lista_de_erros)
    """
    errors = []
    
    # Verifica se tem estrutura básica
    if not isinstance(data, dict):
        errors.append("JSON deve ser um objeto")
        return False, errors
    
    # Verifica cards
    if 'cards' not in data:
        errors.append("Campo 'cards' não encontrado")
    elif not isinstance(data['cards'], list):
        errors.append("Campo 'cards' deve ser uma lista")
    elif len(data['cards']) == 0:
        errors.append("Lista 'cards' está vazia")
    
    # Verifica membros
    if 'members' not in data:
        errors.append("Campo 'members' não encontrado")
    elif not isinstance(data['members'], list):
        errors.append("Campo 'members' deve ser uma lista")
    
    # Verifica estrutura de cards
    if 'cards' in data and isinstance(data['cards'], list) and len(data['cards']) > 0:
        sample_card = data['cards'][0]
        required_fields = ['id', 'name']
        
        for field in required_fields:
            if field not in sample_card:
                errors.append(f"Campo obrigatório '{field}' não encontrado nos cards")
    
    is_valid = len(errors) == 0
    return is_valid, errors

@st.cache_data
def load_sample_data() -> Dict[str, Any]:
    """
    Carrega dados de exemplo (cached).
    
    Returns:
        Dicionário com dados de exemplo
    """
    return {
        "cards": [
            {
                "id": "sample1",
                "name": "Tarefa de Exemplo 1",
                "desc": "Descrição da tarefa",
                "list": {"name": "Em Progresso"},
                "members": [{"username": "lucas.silva"}],
                "dateLastActivity": "2024-01-15T10:00:00.000Z",
                "due": None,
                "closed": False,
                "url": "https://trello.com/sample1"
            },
            {
                "id": "sample2", 
                "name": "Tarefa de Exemplo 2",
                "desc": "Outra descrição",
                "list": {"name": "Concluído"},
                "members": [{"username": "maria.santos"}, {"username": "lucas.silva"}],
                "dateLastActivity": "2024-01-14T15:30:00.000Z",
                "due": "2024-01-20T00:00:00.000Z",
                "closed": False,
                "url": "https://trello.com/sample2"
            }
        ],
        "members": [
            {"id": "member1", "username": "lucas.silva", "fullName": "Lucas Silva"},
            {"id": "member2", "username": "maria.santos", "fullName": "Maria Santos"}
        ]
    }
