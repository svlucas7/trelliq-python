"""
Aplicação principal Streamlit para o sistema Trelliq Python.
Replica a interface e funcionalidade completa do sistema TypeScript.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional
import base64
import io

# Configuração da página
st.set_page_config(
    page_title="Trelliq - Relatórios de Marketing",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/svlucas7/trelliq-python',
        'Report a bug': 'https://github.com/svlucas7/trelliq-python/issues',
        'About': "# Trelliq Python\nSistema de relatórios Trello com lógica avançada de deduplicação"
    }
)

# Imports locais
try:
    from src.data_processor import TrelloDataProcessor, TaskReport, CollaboratorReport, ReportSummary
    from src.config import (
        GRUPOS_MARKETING, STREAMLIT_CONFIG, STATUS_COLORS, TASK_STATUSES,
        get_grupo_por_responsavel, CONTENT_CREATORS
    )
    from src.utils import format_number, format_percentage, create_download_link
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.stop()

# CSS personalizado para interface moderna
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .group-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
    }
    
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
    }
    
    .success { background-color: #28a745; }
    .warning { background-color: #ffc107; color: #212529; }
    .danger { background-color: #dc3545; }
    .info { background-color: #17a2b8; }
    .secondary { background-color: #6c757d; }
    
    .sidebar-info {
        background: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    
    .upload-area {
        border: 2px dashed #007bff;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
        transition: all 0.3s ease;
    }
    
    .collaborator-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin-bottom: 0.5rem;
        transition: box-shadow 0.3s ease;
    }
    
    .collaborator-card:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Inicializa o estado da sessão."""
    if 'trello_data' not in st.session_state:
        st.session_state.trello_data = None
    if 'task_reports' not in st.session_state:
        st.session_state.task_reports = []
    if 'collaborator_reports' not in st.session_state:
        st.session_state.collaborator_reports = []
    if 'report_summary' not in st.session_state:
        st.session_state.report_summary = None
    if 'selected_groups' not in st.session_state:
        st.session_state.selected_groups = [g.name for g in GRUPOS_MARKETING]
    if 'date_range' not in st.session_state:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        st.session_state.date_range = (start_date, end_date)

def create_sidebar():
    """Cria a barra lateral com controles."""
    st.sidebar.markdown("""
    <div class="sidebar-info">
        <h3>📊 Trelliq Python</h3>
        <p>Sistema avançado de relatórios Trello com lógica sofisticada de grupos e deduplicação.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload de arquivo
    st.sidebar.header("📁 Upload de Dados")
    
    uploaded_file = st.sidebar.file_uploader(
        "Escolha um arquivo JSON do Trello",
        type=['json'],
        help="Exporte seu board do Trello em formato JSON"
    )
    
    # Botão para dados de exemplo
    if st.sidebar.button("🎯 Usar Dados de Exemplo", help="Carrega dados de exemplo para demonstração"):
        load_sample_data()
    
    # Filtros de data
    st.sidebar.header("📅 Período do Relatório")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Data Início",
            value=st.session_state.date_range[0],
            help="Data de início do período de análise"
        )
    
    with col2:
        end_date = st.date_input(
            "Data Fim", 
            value=st.session_state.date_range[1],
            help="Data de fim do período de análise"
        )
    
    st.session_state.date_range = (start_date, end_date)
    
    # Filtro de grupos
    st.sidebar.header("👥 Filtros de Grupos")
    
    all_groups = [g.name for g in GRUPOS_MARKETING] + ['Sem Grupo']
    
    selected_groups = st.sidebar.multiselect(
        "Selecione os grupos:",
        options=all_groups,
        default=st.session_state.selected_groups,
        help="Escolha quais grupos incluir no relatório"
    )
    
    st.session_state.selected_groups = selected_groups
    
    # Informações do sistema
    if st.session_state.trello_data:
        st.sidebar.markdown("---")
        st.sidebar.header("ℹ️ Informações do Board")
        
        board_name = st.session_state.trello_data.get('name', 'Desconhecido')
        st.sidebar.info(f"**Board:** {board_name}")
        
        total_cards = len(st.session_state.trello_data.get('cards', []))
        total_members = len(st.session_state.trello_data.get('members', []))
        
        st.sidebar.metric("Cards Totais no Board", total_cards)
        st.sidebar.metric("Membros", total_members)
        
        # Informações sobre filtragem
        if st.session_state.task_reports:
            st.sidebar.markdown("---")
            st.sidebar.header("📊 Filtros Aplicados")
            
            # Contar cards únicos nos reports
            unique_card_ids = set()
            for report in st.session_state.task_reports:
                unique_card_ids.add(report.task_id)
            
            cards_no_periodo = len(unique_card_ids)
            cards_filtrados = len(st.session_state.task_reports)
            
            st.sidebar.metric("Cards no Período", cards_no_periodo)
            st.sidebar.metric("Reports Gerados", cards_filtrados)
            
            if cards_no_periodo != cards_filtrados:
                st.sidebar.info(f"💡 Diferença entre cards ({cards_no_periodo}) e reports ({cards_filtrados}) é normal quando há múltiplos colaboradores por tarefa.")
        
        # Botão de reprocessamento
        if st.sidebar.button("🔄 Reprocessar Dados", help="Reprocessa os dados com filtros atuais"):
            process_trello_data()
    
    # Links úteis
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 🔗 Links Úteis
    - [GitHub](https://github.com/svlucas7/trelliq-python)
    - [Trello](https://trello.com)
    - [Documentação](https://github.com/svlucas7/trelliq-python/blob/main/README.md)
    """)
    
    return uploaded_file

def load_sample_data():
    """Carrega dados de exemplo do arquivo público."""
    try:
        # Carregar dados de exemplo (seria melhor ter um arquivo dedicado)
        sample_data = {
            "name": "Board de Marketing - Exemplo",
            "cards": [
                {
                    "id": "sample1",
                    "name": "Criação de Post Instagram",
                    "desc": "Post para campanha de lançamento",
                    "idList": "list1",
                    "idMembers": ["member1"],
                    "due": "2024-12-20T12:00:00.000Z",
                    "dateLastActivity": "2024-12-15T10:30:00.000Z",
                    "closed": False
                }
            ],
            "lists": [
                {"id": "list1", "name": "EM PROCESSO DE CONTEÚDO"},
                {"id": "list2", "name": "FEITOS"}
            ],
            "members": [
                {"id": "member1", "username": "jamillyfreitass", "fullName": "Jamily Freitas"}
            ]
        }
        
        st.session_state.trello_data = sample_data
        st.sidebar.success("✅ Dados de exemplo carregados!")
        process_trello_data()
        
    except Exception as e:
        st.sidebar.error(f"Erro ao carregar dados de exemplo: {e}")

def process_uploaded_file(uploaded_file):
    """Processa arquivo carregado pelo usuário."""
    try:
        # Ler arquivo JSON
        data = json.load(uploaded_file)
        
        # Validar estrutura
        processor = TrelloDataProcessor()
        is_valid, errors = processor.validate_trello_data(data)
        
        if not is_valid:
            st.error("❌ Arquivo JSON inválido!")
            for error in errors:
                st.error(f"• {error}")
            return False
        
        # Salvar dados na sessão
        st.session_state.trello_data = data
        st.sidebar.success("✅ Arquivo carregado com sucesso!")
        
        # Processar dados automaticamente
        process_trello_data()
        return True
        
    except json.JSONDecodeError:
        st.error("❌ Erro ao decodificar arquivo JSON. Verifique se o arquivo está correto.")
        return False
    except Exception as e:
        st.error(f"❌ Erro inesperado: {e}")
        return False

def process_trello_data():
    """Processa dados do Trello com filtros aplicados."""
    if not st.session_state.trello_data:
        return
        
    try:
        processor = TrelloDataProcessor()
        
        # Gerar relatórios de tarefas
        start_date, end_date = st.session_state.date_range
        task_reports = processor.generate_task_reports(
            st.session_state.trello_data,
            start_date,
            end_date
        )
        
        # Filtrar por grupos selecionados
        filtered_reports = []
        for report in task_reports:
            report_group = report.grupo or 'Sem Grupo'
            if report_group in st.session_state.selected_groups:
                filtered_reports.append(report)
        
        # Gerar relatórios derivados
        st.session_state.task_reports = filtered_reports
        st.session_state.collaborator_reports = processor.generate_collaborator_reports(filtered_reports)
        st.session_state.report_summary = processor.generate_report_summary(filtered_reports)
        
        st.sidebar.success(f"✅ Processados {len(filtered_reports)} registros")
        
    except Exception as e:
        st.error(f"❌ Erro ao processar dados: {e}")

def display_header():
    """Exibe cabeçalho principal."""
    st.markdown("""
    <div class="main-header">
        <h1>📊 Trelliq Python - Relatórios de Marketing</h1>
        <p>Sistema avançado de análise Trello com lógica sofisticada de grupos e deduplicação</p>
    </div>
    """, unsafe_allow_html=True)

def display_metrics_overview():
    """Exibe métricas principais com informações detalhadas."""
    if not st.session_state.report_summary:
        return
        
    summary = st.session_state.report_summary
    
    st.header("📈 Visão Geral")
    
    # Métrica de debug sobre filtragem
    with st.expander("🔍 Detalhes da Filtragem", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_board_cards = len(st.session_state.trello_data.get('cards', []))
            st.metric("Cards no Board", total_board_cards)
            
        with col2:
            # Contar cards únicos que passaram pelo filtro
            unique_card_ids = set()
            for report in st.session_state.task_reports:
                unique_card_ids.add(report.task_id)
            cards_no_periodo = len(unique_card_ids)
            st.metric("Cards no Período", cards_no_periodo)
            
        with col3:
            reduction_percentage = ((total_board_cards - cards_no_periodo) / total_board_cards * 100) if total_board_cards > 0 else 0
            st.metric("Redução do Filtro", f"{reduction_percentage:.1f}%")
        
        if cards_no_periodo != summary.total_tasks:
            st.info(f"💡 **Explicação:** {cards_no_periodo} cards únicos geram {summary.total_tasks} tarefas únicas após deduplicação por colaboradores.")
        
        start_date, end_date = st.session_state.date_range
        st.write(f"**Período analisado:** {start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')}")
    
    # Métricas principais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total de Tarefas",
            summary.total_tasks,
            help="Número total de tarefas únicas no período (após deduplicação)"
        )
    
    with col2:
        completion_rate = (summary.completed_tasks / summary.total_tasks * 100) if summary.total_tasks > 0 else 0
        st.metric(
            "Taxa de Conclusão",
            f"{completion_rate:.1f}%",
            help="Percentual de tarefas concluídas"
        )
    
    with col3:
        st.metric(
            "Em Andamento",
            summary.in_progress_tasks,
            help="Tarefas atualmente em execução"
        )
    
    with col4:
        st.metric(
            "Atrasadas",
            summary.late_tasks,
            help="Tarefas que passaram do prazo"
        )
    
    with col5:
        st.metric(
            "Colaboradores",
            summary.total_collaborators,
            help="Número de colaboradores únicos"
        )

def create_status_distribution_chart():
    """Cria gráfico de distribuição de status."""
    if not st.session_state.task_reports:
        return None
        
    # Contar status
    status_counts = {}
    for report in st.session_state.task_reports:
        status = report.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Criar gráfico de pizza
    fig = go.Figure(data=[go.Pie(
        labels=list(status_counts.keys()),
        values=list(status_counts.values()),
        marker=dict(colors=[STATUS_COLORS.get(status, '#6c757d') for status in status_counts.keys()]),
        textinfo='label+percent',
        textposition='auto',
        hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Distribuição de Status das Tarefas",
        font=dict(size=12),
        showlegend=True,
        height=400
    )
    
    return fig

def create_group_distribution_chart():
    """Cria gráfico de distribuição por grupos."""
    if not st.session_state.report_summary:
        return None
        
    summary = st.session_state.report_summary
    
    # Preparar dados
    groups = [gs.grupo for gs in summary.group_summaries]
    total_tasks = [gs.total_tasks for gs in summary.group_summaries]
    completed_tasks = [gs.completed_tasks for gs in summary.group_summaries]
    in_progress_tasks = [gs.in_progress_tasks for gs in summary.group_summaries]
    
    # Criar gráfico de barras agrupadas
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Concluídas',
        x=groups,
        y=completed_tasks,
        marker_color='#28a745',
        text=completed_tasks,
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='Em Andamento',
        x=groups,
        y=in_progress_tasks,
        marker_color='#007bff',
        text=in_progress_tasks,
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Distribuição de Tarefas por Grupo",
        xaxis_title="Grupos",
        yaxis_title="Quantidade de Tarefas",
        barmode='group',
        height=400,
        font=dict(size=12)
    )
    
    return fig

def display_group_details():
    """Exibe detalhes dos grupos."""
    if not st.session_state.report_summary:
        return
        
    st.header("👥 Detalhes dos Grupos")
    
    summary = st.session_state.report_summary
    
    # Criar cards para cada grupo
    for group_summary in summary.group_summaries:
        if group_summary.total_tasks == 0:
            continue
            
        with st.expander(f"📋 {group_summary.grupo} ({group_summary.total_tasks} tarefas)", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📊 Estatísticas Gerais**")
                completion_rate = (group_summary.completed_tasks / group_summary.total_tasks * 100) if group_summary.total_tasks > 0 else 0
                st.metric("Taxa de Conclusão", f"{completion_rate:.1f}%")
                st.metric("Total de Tarefas", group_summary.total_tasks)
                
            with col2:
                st.markdown("**⚡ Status das Tarefas**")
                st.metric("Concluídas", group_summary.completed_tasks)
                st.metric("Em Andamento", group_summary.in_progress_tasks)
                st.metric("Atrasadas", group_summary.late_tasks)
                
            with col3:
                st.markdown("**👤 Responsáveis**")
                if group_summary.responsaveis:
                    for responsavel in group_summary.responsaveis:
                        st.write(f"• {responsavel}")
                else:
                    st.write("• Não definidos")
            
            # Tarefas do grupo
            group_tasks = [t for t in st.session_state.task_reports if t.grupo == group_summary.grupo]
            if group_tasks:
                st.markdown("**📋 Tarefas do Grupo**")
                
                # Criar DataFrame para exibição
                task_data = []
                for task in group_tasks[:10]:  # Mostrar apenas as primeiras 10
                    task_data.append({
                        'Tarefa': task.task_name,
                        'Colaborador': task.collaborator_name,
                        'Status': task.status,
                        'Prazo': task.due_date,
                        'Atraso (dias)': task.days_late if task.days_late > 0 else '-'
                    })
                
                df_tasks = pd.DataFrame(task_data)
                st.dataframe(df_tasks, use_container_width=True)
                
                if len(group_tasks) > 10:
                    st.info(f"Mostrando 10 de {len(group_tasks)} tarefas. Use a seção de Relatórios para ver todas.")

def display_collaborator_analysis():
    """Exibe análise de colaboradores."""
    if not st.session_state.collaborator_reports:
        return
        
    st.header("👤 Análise de Colaboradores")
    
    # Top performers
    top_performers = sorted(
        st.session_state.collaborator_reports,
        key=lambda x: x.completion_rate,
        reverse=True
    )[:5]
    
    st.subheader("🏆 Top 5 Performers")
    
    for i, collaborator in enumerate(top_performers, 1):
        with st.expander(f"#{i} {collaborator.collaborator_name} ({collaborator.completion_rate:.1f}%)", expanded=i <= 3):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total de Tarefas", collaborator.total_tasks)
                st.metric("Tarefas Concluídas", collaborator.completed_tasks)
                st.metric("Taxa de Conclusão", f"{collaborator.completion_rate:.1f}%")
                
            with col2:
                st.metric("Em Andamento", collaborator.in_progress_tasks)
                st.metric("Atrasadas", collaborator.late_tasks)
                if collaborator.average_days_late > 0:
                    st.metric("Média de Atraso", f"{collaborator.average_days_late} dias")
            
            # Mostrar algumas tarefas
            if collaborator.tasks:
                st.markdown("**Tarefas Recentes:**")
                for task in collaborator.tasks[:3]:
                    status_color = STATUS_COLORS.get(task.status, '#6c757d')
                    st.markdown(f"• **{task.task_name}** - <span style='color: {status_color};'>●</span> {task.status}", unsafe_allow_html=True)

def display_reports_section():
    """Exibe seção de relatórios detalhados."""
    if not st.session_state.task_reports:
        return
        
    st.header("📊 Relatórios Detalhados")
    
    # Tabs para diferentes relatórios
    tab1, tab2, tab3 = st.tabs(["📋 Relatório de Tarefas", "👤 Relatório de Colaboradores", "📈 Análise Temporal"])
    
    with tab1:
        st.subheader("Relatório Completo de Tarefas")
        
        # Criar DataFrame para exibição
        task_data = []
        for task in st.session_state.task_reports:
            task_data.append({
                'Tarefa': task.task_name,
                'Colaborador': task.collaborator_name,
                'Grupo': task.grupo or 'Sem Grupo',
                'Status': task.status,
                'Lista Atual': task.list_name,
                'Prazo': task.due_date,
                'Dias de Atraso': task.days_late if task.days_late > 0 else 0,
                'Observações': task.observations[:50] + '...' if len(task.observations) > 50 else task.observations
            })
        
        df_tasks = pd.DataFrame(task_data)
        
        # Filtros adicionais
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect(
                "Filtrar por Status:",
                options=df_tasks['Status'].unique(),
                default=df_tasks['Status'].unique()
            )
        
        with col2:
            group_filter = st.multiselect(
                "Filtrar por Grupo:",
                options=df_tasks['Grupo'].unique(),
                default=df_tasks['Grupo'].unique()
            )
        
        # Aplicar filtros
        filtered_df = df_tasks[
            (df_tasks['Status'].isin(status_filter)) &
            (df_tasks['Grupo'].isin(group_filter))
        ]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # Botão de download
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Baixar Relatório CSV",
            data=csv,
            file_name=f"relatorio_tarefas_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with tab2:
        st.subheader("Relatório de Produtividade dos Colaboradores")
        
        if st.session_state.collaborator_reports:
            # Criar DataFrame para colaboradores
            collab_data = []
            for collab in st.session_state.collaborator_reports:
                collab_data.append({
                    'Colaborador': collab.collaborator_name,
                    'Total de Tarefas': collab.total_tasks,
                    'Concluídas': collab.completed_tasks,
                    'Em Andamento': collab.in_progress_tasks,
                    'Atrasadas': collab.late_tasks,
                    'Taxa de Conclusão': f"{collab.completion_rate:.1f}%",
                    'Média de Atraso (dias)': collab.average_days_late
                })
            
            df_collabs = pd.DataFrame(collab_data)
            st.dataframe(df_collabs, use_container_width=True)
            
            # Download
            csv = df_collabs.to_csv(index=False)
            st.download_button(
                label="📥 Baixar Relatório de Colaboradores CSV",
                data=csv,
                file_name=f"relatorio_colaboradores_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with tab3:
        st.subheader("Análise Temporal")
        st.info("🚧 Em desenvolvimento - será implementado em versão futura")

def display_charts_section():
    """Exibe seção de gráficos."""
    if not st.session_state.task_reports:
        return
        
    st.header("📈 Visualizações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de distribuição de status
        status_chart = create_status_distribution_chart()
        if status_chart:
            st.plotly_chart(status_chart, use_container_width=True)
    
    with col2:
        # Gráfico de distribuição por grupos
        group_chart = create_group_distribution_chart()
        if group_chart:
            st.plotly_chart(group_chart, use_container_width=True)

def display_welcome_screen():
    """Exibe tela de boas-vindas quando não há dados."""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Bem-vindo ao Trelliq Python!</h1>
        <p>Sistema avançado de relatórios Trello com lógica sofisticada de grupos</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📋 Como Usar:
        
        1. **Exporte dados do Trello:**
           - Acesse seu board no Trello
           - Menu → Mais → Imprimir e Exportar → Exportar JSON
           
        2. **Faça upload:**
           - Use o botão na barra lateral
           - Ou teste com dados de exemplo
           
        3. **Analise os resultados:**
           - Visualizações interativas
           - Relatórios detalhados
           - Zero duplicações
        """)
    
    with col2:
        st.markdown("""
        ### ✨ Características:
        
        ✅ **Lógica Avançada**: Replica sistema TypeScript  
        ✅ **4 Grupos**: Suporte completo aos grupos de marketing  
        ✅ **Criadores de Conteúdo**: Lógica especial para Jamily e Leo  
        ✅ **Zero Duplicações**: Deduplicação inteligente  
        ✅ **Visualizações**: Gráficos interativos com Plotly  
        ✅ **Relatórios**: Exports profissionais  
        """)
    
    st.markdown("""
    ### 🚀 Comece Agora:
    Use o botão **"🎯 Usar Dados de Exemplo"** na barra lateral para ver o sistema funcionando!
    """)

def main():
    """Função principal da aplicação."""
    # Inicializar estado
    init_session_state()
    
    # Criar sidebar e obter arquivo carregado
    uploaded_file = create_sidebar()
    
    # Processar arquivo carregado
    if uploaded_file is not None:
        process_uploaded_file(uploaded_file)
    
    # Exibir conteúdo principal
    if st.session_state.trello_data is None:
        display_welcome_screen()
    else:
        display_header()
        display_metrics_overview()
        
        # Seções principais
        display_charts_section()
        display_group_details()
        display_collaborator_analysis()
        display_reports_section()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #6c757d; padding: 1rem;">
            💡 Trelliq Python - Sistema de Relatórios Trello | 
            <a href="https://github.com/svlucas7/trelliq-python" target="_blank">GitHub</a>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
