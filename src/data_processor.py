"""
Processador de dados do Trello com foco em eliminação de duplicatas.
Utiliza pandas para operações eficientes de dados.
"""

import pandas as pd
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from src.config import GRUPOS_MARKETING, STATUS_MAPPING

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrelloDataProcessor:
    """
    Processador principal de dados do Trello com eliminação automática de duplicatas.
    """
    
    def __init__(self):
        self.raw_data: Optional[Dict] = None
        self.df_cards: Optional[pd.DataFrame] = None
        self.df_members: Optional[pd.DataFrame] = None
        
    def load_trello_data(self, json_data: str) -> bool:
        """
        Carrega dados JSON do Trello e converte para DataFrames.
        
        Args:
            json_data: String JSON com dados do Trello
            
        Returns:
            bool: True se carregamento foi bem-sucedido
        """
        try:
            self.raw_data = json.loads(json_data)
            logger.info("Dados JSON carregados com sucesso")
            
            # Converte cards para DataFrame
            if 'cards' in self.raw_data:
                self.df_cards = pd.DataFrame(self.raw_data['cards'])
                logger.info(f"Carregados {len(self.df_cards)} cards")
            
            # Converte members para DataFrame 
            if 'members' in self.raw_data:
                self.df_members = pd.DataFrame(self.raw_data['members'])
                logger.info(f"Carregados {len(self.df_members)} membros")
            
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao carregar dados: {e}")
            return False
    
    def _normalize_card_data(self) -> pd.DataFrame:
        """
        Normaliza dados dos cards eliminando duplicatas automaticamente.
        
        Returns:
            DataFrame normalizado sem duplicatas
        """
        if self.df_cards is None:
            return pd.DataFrame()
        
        # Cria DataFrame normalizado
        normalized_cards = []
        
        for _, card in self.df_cards.iterrows():
            # Extrai lista atual
            list_name = ""
            if 'list' in card and isinstance(card['list'], dict):
                list_name = card['list'].get('name', '')
            
            # Mapeia status baseado na lista
            status = self._map_status(list_name)
            
            # Extrai membros
            members = []
            if 'members' in card and isinstance(card['members'], list):
                members = [member.get('username', '') for member in card['members']]
            
            # Extrai datas
            created_date = self._parse_date(card.get('dateLastActivity'))
            due_date = self._parse_date(card.get('due'))
            
            normalized_card = {
                'id': card.get('id', ''),
                'name': card.get('name', ''),
                'description': card.get('desc', ''),
                'list_name': list_name,
                'status': status,
                'members': members,
                'member_count': len(members),
                'created_date': created_date,
                'due_date': due_date,
                'url': card.get('url', ''),
                'closed': card.get('closed', False)
            }
            
            normalized_cards.append(normalized_card)
        
        df_normalized = pd.DataFrame(normalized_cards)
        
        # Remove duplicatas baseado no ID (chave primária do Trello)
        df_normalized = df_normalized.drop_duplicates(subset=['id'], keep='first')
        
        logger.info(f"Cards normalizados: {len(df_normalized)} únicos")
        return df_normalized
    
    def _map_status(self, list_name: str) -> str:
        """
        Mapeia nome da lista para status padronizado.
        
        Args:
            list_name: Nome da lista do Trello
            
        Returns:
            Status mapeado
        """
        for trello_name, status in STATUS_MAPPING.items():
            if trello_name.lower() in list_name.lower():
                return status
        return "indefinido"
    
    def _parse_date(self, date_str: Any) -> Optional[datetime]:
        """
        Converte string de data para datetime.
        
        Args:
            date_str: String de data em formato ISO ou None
            
        Returns:
            Objeto datetime ou None
        """
        if not date_str:
            return None
        
        try:
            if isinstance(date_str, str):
                return pd.to_datetime(date_str)
            return None
        except:
            return None
    
    def assign_groups(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Atribui cards aos grupos baseado nos membros.
        Elimina duplicações automaticamente usando pandas.
        
        Args:
            df: DataFrame com cards normalizados
            
        Returns:
            DataFrame com grupos atribuídos
        """
        def get_card_group(members: List[str]) -> str:
            """Determina o grupo baseado nos membros do card."""
            if not members:
                return "Sem Grupo"
            
            # Conta membros por grupo
            group_counts = {}
            for group_name, group_config in GRUPOS_MARKETING.items():
                count = sum(1 for member in members 
                          if member in group_config['responsaveis'])
                if count > 0:
                    group_counts[group_name] = count
            
            # Retorna grupo com mais membros
            if group_counts:
                return max(group_counts, key=group_counts.get)
            
            return "Sem Grupo"
        
        # Aplica atribuição de grupos
        df['grupo'] = df['members'].apply(get_card_group)
        
        # Remove duplicatas por ID e grupo (garante unicidade)
        df_unique = df.drop_duplicates(subset=['id'], keep='first')
        
        logger.info(f"Grupos atribuídos: {len(df_unique)} cards únicos")
        return df_unique
    
    def generate_task_report(self) -> pd.DataFrame:
        """
        Gera relatório de tarefas sem duplicatas.
        
        Returns:
            DataFrame com relatório de tarefas
        """
        if self.df_cards is None:
            return pd.DataFrame()
        
        # Normaliza e atribui grupos
        df_normalized = self._normalize_card_data()
        df_with_groups = self.assign_groups(df_normalized)
        
        # Filtra apenas cards não arquivados
        df_active = df_with_groups[~df_with_groups['closed']]
        
        # Agrupa por grupo e status para estatísticas
        report = df_active.groupby(['grupo', 'status']).agg({
            'id': 'count',
            'name': lambda x: list(x),
            'member_count': 'mean'
        }).reset_index()
        
        report.columns = ['grupo', 'status', 'total_tasks', 'task_names', 'avg_members']
        
        logger.info(f"Relatório de tarefas gerado: {len(report)} entradas")
        return report
    
    def generate_collaborator_report(self) -> pd.DataFrame:
        """
        Gera relatório de colaboradores sem duplicatas.
        
        Returns:
            DataFrame com análise de colaboradores
        """
        if self.df_cards is None:
            return pd.DataFrame()
        
        df_normalized = self._normalize_card_data()
        df_with_groups = self.assign_groups(df_normalized)
        
        # Explode members para análise individual
        df_members_expanded = df_with_groups.explode('members')
        df_members_expanded = df_members_expanded.dropna(subset=['members'])
        
        # Remove duplicatas de membro-tarefa
        df_members_unique = df_members_expanded.drop_duplicates(
            subset=['id', 'members'], keep='first'
        )
        
        # Agrupa por colaborador
        collaborator_stats = df_members_unique.groupby('members').agg({
            'id': 'count',
            'grupo': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Múltiplos',
            'status': lambda x: list(x.value_counts().index[:3])  # Top 3 status
        }).reset_index()
        
        collaborator_stats.columns = ['colaborador', 'total_tasks', 'grupo_principal', 'top_status']
        
        logger.info(f"Relatório de colaboradores gerado: {len(collaborator_stats)} únicos")
        return collaborator_stats
    
    def generate_summary_metrics(self) -> Dict[str, Any]:
        """
        Gera métricas resumidas do projeto.
        
        Returns:
            Dicionário com métricas principais
        """
        if self.df_cards is None:
            return {}
        
        df_normalized = self._normalize_card_data()
        df_with_groups = self.assign_groups(df_normalized)
        
        # Calcula métricas
        total_cards = len(df_with_groups)
        active_cards = len(df_with_groups[~df_with_groups['closed']])
        unique_collaborators = len(df_with_groups.explode('members')['members'].unique())
        
        # Status distribution
        status_dist = df_with_groups['status'].value_counts().to_dict()
        
        # Group distribution
        group_dist = df_with_groups['grupo'].value_counts().to_dict()
        
        metrics = {
            'total_cards': total_cards,
            'active_cards': active_cards,
            'unique_collaborators': unique_collaborators,
            'status_distribution': status_dist,
            'group_distribution': group_dist,
            'completion_rate': (status_dist.get('concluido', 0) / total_cards * 100) if total_cards > 0 else 0
        }
        
        logger.info("Métricas resumidas geradas")
        return metrics
    
    def export_to_excel(self, filename: str) -> bool:
        """
        Exporta todos os relatórios para Excel.
        
        Args:
            filename: Nome do arquivo de saída
            
        Returns:
            bool: True se exportação foi bem-sucedida
        """
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Relatório de tarefas
                task_report = self.generate_task_report()
                task_report.to_excel(writer, sheet_name='Tarefas', index=False)
                
                # Relatório de colaboradores
                collab_report = self.generate_collaborator_report()
                collab_report.to_excel(writer, sheet_name='Colaboradores', index=False)
                
                # Dados normalizados
                df_normalized = self._normalize_card_data()
                df_with_groups = self.assign_groups(df_normalized)
                df_with_groups.to_excel(writer, sheet_name='Dados_Completos', index=False)
                
                # Métricas resumidas
                metrics = self.generate_summary_metrics()
                metrics_df = pd.DataFrame([metrics])
                metrics_df.to_excel(writer, sheet_name='Resumo', index=False)
            
            logger.info(f"Dados exportados para {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar para Excel: {e}")
            return False
