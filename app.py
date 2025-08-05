"""
Aplicação principal Streamlit para o sistema Trelliq.
Sistema de relatórios Trello com eliminação automática de duplicatas.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Trelliq - Relatórios de Marketing",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-username/trelliq-python',
        'Report a bug': 'https://github.com/your-username/trelliq-python/issues',
        'About': "# Trelliq Web App\nSistema de relatórios Trello com eliminação automática de duplicatas"
    }
)

# Imports locais
from src.data_processor import TrelloDataProcessor
from src.config import GRUPOS_MARKETING, STREAMLIT_CONFIG
from src.utils import (
    create_status_pie_chart,
    create_group_bar_chart, 
    create_collaborator_chart,
    create_progress_metrics,
    format_dataframe_for_display,
    validate_json_structure,
    load_sample_data
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2C3E50, #3498DB);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #F8F9FA;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3498DB;
        margin: 0.5rem 0;
    }
    
    .success-message {
        background: #D4EDDA;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #C3E6CB;
    }
    
    .warning-message {
        background: #FFF3CD;
        color: #856404;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #FFEAA7;
    }
    
    .error-message {
        background: #F8D7DA;
        color: #721C24;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #F5C6CB;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Função principal da aplicação."""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>📊 Trelliq - Sistema de Relatórios Trello</h1>
        <p>🌐 Web App para processamento inteligente de dados com eliminação automática de duplicatas</p>
        <small>✨ Acesse de qualquer lugar • 📱 Responsivo • 🚀 Deploy automático</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializa processador na sessão
    if 'processor' not in st.session_state:
        st.session_state.processor = TrelloDataProcessor()
    
    # Sidebar para upload e configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Upload de arquivo
        st.subheader("📤 Upload de Dados")
        uploaded_file = st.file_uploader(
            "Selecione o arquivo JSON do Trello",
            type=['json'],
            help="Faça o export do board do Trello em formato JSON. O arquivo será processado automaticamente."
        )
        
        # Instruções rápidas
        with st.expander("📋 Como exportar do Trello"):
            st.markdown("""
            1. Abra seu board no Trello
            2. Clique em **Menu** → **Mais** → **Imprimir e Exportar**
            3. Selecione **Exportar JSON**
            4. Baixe o arquivo e faça upload aqui
            """)
        
        # Opção de usar dados de exemplo
        if st.button("🎯 Usar Dados de Exemplo", help="Carrega dados de exemplo para testar o sistema"):
            sample_data = load_sample_data()
            if st.session_state.processor.load_trello_data(json.dumps(sample_data)):
                st.success("✅ Dados de exemplo carregados!")
                st.rerun()
        
        # Configuração dos grupos
        st.subheader("👥 Grupos Configurados")
        for grupo, config in GRUPOS_MARKETING.items():
            with st.expander(f"{grupo}: {config['nome']}"):
                st.write(f"**Responsáveis:** {', '.join(config['responsaveis'])}")
                st.write(f"**Etapas:** {', '.join(config['etapas'])}")
                st.color_picker("Cor", config['cor'], disabled=True)
    
    # Processamento do upload
    if uploaded_file is not None:
        try:
            # Lê conteúdo do arquivo
            json_content = uploaded_file.read().decode('utf-8')
            
            # Valida estrutura JSON
            try:
                json_data = json.loads(json_content)
                is_valid, errors = validate_json_structure(json_data)
                
                if not is_valid:
                    st.markdown(f"""
                    <div class="error-message">
                        <strong>❌ Arquivo JSON inválido:</strong><br>
                        {'<br>'.join(errors)}
                    </div>
                    """, unsafe_allow_html=True)
                    return
                
            except json.JSONDecodeError as e:
                st.markdown(f"""
                <div class="error-message">
                    <strong>❌ Erro ao decodificar JSON:</strong><br>
                    {str(e)}
                </div>
                """, unsafe_allow_html=True)
                return
            
            # Carrega dados no processador
            if st.session_state.processor.load_trello_data(json_content):
                st.markdown("""
                <div class="success-message">
                    ✅ <strong>Dados carregados com sucesso!</strong> Todos os relatórios foram atualizados.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="error-message">
                    ❌ <strong>Erro ao processar dados.</strong> Verifique o formato do arquivo.
                </div>
                """, unsafe_allow_html=True)
                return
                
        except Exception as e:
            st.markdown(f"""
            <div class="error-message">
                <strong>❌ Erro inesperado:</strong><br>
                {str(e)}
            </div>
            """, unsafe_allow_html=True)
            return
    
    # Verifica se há dados carregados
    if st.session_state.processor.raw_data is None:
        st.markdown("""
        <div class="warning-message">
            <strong>⚠️ Nenhum dado carregado.</strong><br>
            Faça upload de um arquivo JSON do Trello ou use dados de exemplo para começar.
        </div>
        """, unsafe_allow_html=True)
        
        # Instruções para o usuário
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📋 Como usar este Web App:
            
            1. **Exporte seus dados do Trello:**
               - Acesse seu board no Trello
               - Vá em Menu → Mais → Imprimir e Exportar → Exportar JSON
               - Baixe o arquivo JSON
            
            2. **Faça upload do arquivo:**
               - Use o botão "Browse files" na barra lateral
               - Selecione o arquivo JSON baixado
            
            3. **Visualize os relatórios:**
               - Os dados serão processados automaticamente
               - Todas as duplicatas serão removidas
               - Relatórios e gráficos serão gerados
            """)
        
        with col2:
            st.markdown("""
            ### 🌟 Recursos do Web App:
            
            ✅ **Zero Duplicações**: Pandas elimina automaticamente  
            ✅ **4 Grupos**: Suporte completo aos grupos de marketing  
            ✅ **Gráficos Interativos**: Visualizações dinâmicas  
            ✅ **Export Profissional**: Excel, CSV, JSON formatados  
            ✅ **Responsivo**: Funciona em qualquer dispositivo  
            ✅ **Online 24/7**: Acesse de qualquer lugar  
            
            ### 🚀 Vantagens:
            - Sem instalação necessária
            - Processamento em tempo real
            - Interface moderna e intuitiva
            - Compartilhável com a equipe
            """)
        
        # Demonstração com imagem ou vídeo (opcional)
        st.markdown("""
        ### 🎯 Teste Agora:
        Clique em **"🎯 Usar Dados de Exemplo"** na barra lateral para ver o sistema funcionando!
        """)
        return
    
    # Dashboard principal com dados carregados
    display_dashboard()

def display_dashboard():
    """Exibe o dashboard principal com todos os relatórios."""
    
    processor = st.session_state.processor
    
    # Gera métricas resumidas
    metrics = processor.generate_summary_metrics()
    
    # Seção de métricas principais
    st.header("📈 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total de Cards",
            metrics.get('total_cards', 0),
            help="Número total de cards processados"
        )
    
    with col2:
        st.metric(
            "Cards Ativos", 
            metrics.get('active_cards', 0),
            help="Cards não arquivados"
        )
    
    with col3:
        st.metric(
            "Colaboradores Únicos",
            metrics.get('unique_collaborators', 0),
            help="Número de colaboradores distintos"
        )
    
    with col4:
        completion_rate = metrics.get('completion_rate', 0)
        st.metric(
            "Taxa de Conclusão",
            f"{completion_rate:.1f}%",
            help="Percentual de cards concluídos"
        )
    
    # Dashboard de métricas visual
    st.header("📊 Dashboard Visual")
    
    # Cria gráfico de métricas
    if metrics:
        progress_chart = create_progress_metrics(metrics)
        st.plotly_chart(progress_chart, use_container_width=True)
    
    # Gráficos de distribuição
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Distribuição por Status")
        status_dist = metrics.get('status_distribution', {})
        if status_dist:
            status_chart = create_status_pie_chart(status_dist)
            st.plotly_chart(status_chart, use_container_width=True)
        else:
            st.info("Nenhum dado de status disponível")
    
    with col2:
        st.subheader("👥 Tarefas por Grupo")
        group_dist = metrics.get('group_distribution', {})
        if group_dist:
            group_chart = create_group_bar_chart(group_dist)
            st.plotly_chart(group_chart, use_container_width=True)
        else:
            st.info("Nenhum dado de grupo disponível")
    
    # Relatório de colaboradores
    st.header("👤 Análise de Colaboradores")
    
    collab_report = processor.generate_collaborator_report()
    if not collab_report.empty:
        # Gráfico de colaboradores
        collab_chart = create_collaborator_chart(collab_report)
        st.plotly_chart(collab_chart, use_container_width=True)
        
        # Tabela de colaboradores
        st.subheader("📊 Detalhes dos Colaboradores")
        collab_display = format_dataframe_for_display(collab_report)
        st.dataframe(collab_display, use_container_width=True)
    else:
        st.info("Nenhum dado de colaborador disponível")
    
    # Relatório de tarefas
    st.header("📋 Relatório de Tarefas")
    
    task_report = processor.generate_task_report()
    if not task_report.empty:
        task_display = format_dataframe_for_display(task_report)
        st.dataframe(task_display, use_container_width=True)
        
        # Estatísticas do relatório
        st.subheader("📈 Estatísticas das Tarefas")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_groups = len(task_report['grupo'].unique())
            st.metric("Grupos Ativos", total_groups)
        
        with col2:
            total_entries = len(task_report)
            st.metric("Entradas no Relatório", total_entries)
        
        with col3:
            avg_tasks = task_report['total_tasks'].mean() if 'total_tasks' in task_report.columns else 0
            st.metric("Média Tarefas/Grupo", f"{avg_tasks:.1f}")
    else:
        st.info("Nenhum relatório de tarefa disponível")
    
    # Seção de exportação
    st.header("💾 Exportar Dados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Exportar Excel Completo", help="Baixa relatório completo em Excel"):
            filename = f"relatorio_trello_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            if processor.export_to_excel(filename):
                st.success(f"✅ Dados exportados para {filename}")
                st.info("💡 O arquivo foi salvo localmente no servidor. Para uma versão web completa, use os botões de download abaixo.")
            else:
                st.error("❌ Erro ao exportar dados")
    
    with col2:
        if st.button("📋 Baixar Relatório de Tarefas", help="Download CSV de tarefas"):
            if not task_report.empty:
                csv = task_report.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"tarefas_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    help="Clique para baixar o arquivo CSV"
                )
            else:
                st.warning("⚠️ Nenhum dado de tarefa para exportar")
    
    with col3:
        if st.button("👤 Baixar Relatório de Colaboradores", help="Download CSV de colaboradores"):
            if not collab_report.empty:
                csv = collab_report.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"colaboradores_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    help="Clique para baixar o arquivo CSV"
                )
            else:
                st.warning("⚠️ Nenhum dado de colaborador para exportar")
    
    # Footer do web app
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7F8C8D; padding: 1rem;">
        <small>
        🌐 <strong>Trelliq Web App</strong> • Desenvolvido com Streamlit e Python<br>
        📊 Sistema de relatórios Trello com eliminação automática de duplicatas<br>
        🚀 Acesse de qualquer lugar • 📱 Responsivo • ⚡ Rápido
        </small>
    </div>
    """, unsafe_allow_html=True)

# Executar aplicação
if __name__ == "__main__":
    main()
