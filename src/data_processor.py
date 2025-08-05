"""
Processador de dados do Trello - Replica a lógica completa do sistema TypeScript.
"""

import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass

from .config import (
    GRUPOS_MARKETING, CONTENT_CREATORS, LIST_STATUS_MAP, STATUS_COLORS,
    get_grupo_por_responsavel, get_etapa_atual, is_finalizada_para_flavia, 
    is_feita, is_em_revisao, GrupoMarketing
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TaskReport:
    """Relatório de uma tarefa individual."""
    task_id: str  # ID único da tarefa
    collaborator_name: str
    task_name: str
    list_name: str
    due_date: str
    created_at: str
    completed_at: Optional[str]
    status: str
    days_late: int
    observations: str
    grupo: Optional[str]
    etapa_atual: Optional[str]
    finalizada_para_flavia: bool
    feita: bool
    em_revisao: bool

@dataclass
class CollaboratorReport:
    """Relatório de um colaborador."""
    collaborator_name: str
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    pending_tasks: int
    late_tasks: int
    blocked_tasks: int
    completion_rate: float
    average_days_late: int
    tasks: List[TaskReport]

@dataclass
class GroupReportSummary:
    """Resumo de relatório por grupo."""
    grupo: str
    responsaveis: List[str]
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    late_tasks: int
    blocked_tasks: int
    on_time_deliveries: int
    late_deliveries: int

@dataclass
class ReportSummary:
    """Resumo geral do relatório."""
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    late_tasks: int
    overdue_tasks: int
    blocked_tasks: int
    total_collaborators: int
    group_summaries: List[GroupReportSummary]

class TrelloDataProcessor:
    """
    Processador de dados do Trello que replica a lógica completa do sistema TypeScript.
    """
    
    def __init__(self):
        """Inicializa o processador."""
        self.logger = logging.getLogger(__name__)
    
    def validate_trello_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida estrutura do JSON do Trello.
        
        Args:
            data: Dados do JSON do Trello
            
        Returns:
            Tuple com (is_valid, error_messages)
        """
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Dados devem ser um objeto JSON válido")
            return False, errors
            
        required_fields = ['cards', 'lists', 'members', 'name']
        for field in required_fields:
            if field not in data:
                errors.append(f"Campo obrigatório '{field}' não encontrado")
            elif field != 'name' and not isinstance(data[field], list):
                errors.append(f"Campo '{field}' deve ser uma lista")
                
        if not isinstance(data.get('name'), str):
            errors.append("Campo 'name' deve ser uma string")
            
        return len(errors) == 0, errors
    
    def filter_cards_by_date_range(self, cards: List[Dict], start_date: date, end_date: date, lists: List[Dict] = None) -> List[Dict]:
        """
        Filtra cards por período de data com lógica inteligente.
        
        Para tarefas concluídas: verifica due date no período
        Para tarefas em andamento: verifica última atividade no período
        
        Args:
            cards: Lista de cards do Trello
            start_date: Data de início
            end_date: Data de fim
            lists: Lista de listas do board (opcional, para identificar listas concluídas)
            
        Returns:
            Lista de cards filtrados
        """
        logger.info(f"=== FILTRO POR DATA INTELIGENTE ===")
        logger.info(f"Período: {start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')}")
        logger.info(f"Total de cards no board: {len(cards)}")
        
        # Identificar listas de tarefas concluídas
        completed_list_ids = set()
        if lists:
            for lista in lists:
                list_name_upper = lista['name'].upper().strip()
                completed_keywords = ['FEITO', 'FEITOS', 'CONCLUÍ', 'FINALIZADO', 'COMPLETO', 'DONE', 'FINISHED']
                if any(keyword in list_name_upper for keyword in completed_keywords):
                    completed_list_ids.add(lista['id'])
                    logger.info(f"📋 Lista identificada como CONCLUÍDA: {lista['name']}")
        
        filtered_cards = []
        
        for card in cards:
            # Filtrar cards arquivados
            if card.get('closed', False):
                logger.info(f"📦 Card ARQUIVADO ignorado: \"{card.get('name', 'N/A')}\"")
                continue
                
            card_name = card.get('name', 'N/A')
            list_id = card.get('idList')
            is_in_completed_list = list_id in completed_list_ids
            
            # Para tarefas em listas de CONCLUÍDAS: filtrar por due date
            if is_in_completed_list:
                due_date_str = card.get('due')
                if due_date_str:
                    try:
                        if due_date_str.endswith('Z'):
                            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
                        else:
                            due_date = datetime.fromisoformat(due_date_str).date()
                        
                        # Se o due date está no período, incluir o card
                        if start_date <= due_date <= end_date:
                            filtered_cards.append(card)
                            logger.info(f"✅ Card CONCLUÍDO \"{card_name}\": incluído por due date {due_date.strftime('%d/%m/%Y')} no período")
                            continue
                        else:
                            logger.info(f"❌ Card CONCLUÍDO \"{card_name}\": due date {due_date.strftime('%d/%m/%Y')} fora do período")
                            continue
                            
                    except (ValueError, TypeError) as e:
                        logger.error(f"Erro ao processar due date do card \"{card_name}\": {e}")
                        
                # Se não tem due date, não incluir cards concluídos sem data de vencimento
                logger.info(f"❌ Card CONCLUÍDO \"{card_name}\": sem due date, não incluído no período")
                continue
            
            # Para tarefas EM ANDAMENTO: filtrar por última atividade
            last_activity_str = card.get('dateLastActivity')
            if not last_activity_str:
                logger.warning(f"⚠️ Card sem dateLastActivity: \"{card_name}\"")
                continue
                
            try:
                # Parse da data (formato ISO do Trello)
                if last_activity_str.endswith('Z'):
                    last_activity = datetime.fromisoformat(last_activity_str.replace('Z', '+00:00')).date()
                else:
                    last_activity = datetime.fromisoformat(last_activity_str).date()
                    
                # Verificar se está no período
                is_in_range = start_date <= last_activity <= end_date
                
                if is_in_range:
                    filtered_cards.append(card)
                    logger.info(f"✅ Card EM ANDAMENTO \"{card_name}\": incluído por última atividade {last_activity.strftime('%d/%m/%Y')} no período")
                else:
                    logger.info(f"❌ Card EM ANDAMENTO \"{card_name}\": última atividade {last_activity.strftime('%d/%m/%Y')} fora do período")
                    
            except (ValueError, TypeError) as e:
                logger.error(f"Erro ao processar data do card \"{card_name}\": {e}")
                
        logger.info(f"Total de cards no período: {len(filtered_cards)}")
        logger.info("======================")
        
        return filtered_cards
    
    def get_task_status(self, card: Dict, lists: List[Dict], members: List[Dict]) -> str:
        """
        Obtém o status da tarefa baseado na lista.
        
        Args:
            card: Card do Trello
            lists: Listas do board
            members: Membros do board
            
        Returns:
            Status da tarefa
        """
        # Verificar se o card está arquivado
        if card.get('closed', False):
            logger.info(f"📦 Card ARQUIVADO: \"{card.get('name')}\" - Status será CONCLUÍDA")
            return 'Concluída'
            
        # Encontrar a lista do card
        list_obj = next((l for l in lists if l['id'] == card.get('idList')), None)
        if not list_obj:
            logger.warning(f"⚠️ Lista não encontrada para card: {card.get('name')} (ID: {card.get('idList')})")
            return 'Em Andamento'
            
        list_name_upper = list_obj['name'].upper().strip()
        logger.info(f"🔍 Analisando status do card \"{card.get('name')}\" na lista \"{list_obj['name']}\"")
        
        # Verificação prioritária para listas de "concluído"
        completed_keywords = ['FEITO', 'FEITOS', 'CONCLUÍ', 'FINALIZADO', 'COMPLETO', 'DONE', 'FINISHED']
        is_completed = any(keyword in list_name_upper for keyword in completed_keywords)
        
        if is_completed:
            logger.info(f"✅ TAREFA CONCLUÍDA detectada: \"{card.get('name')}\" na lista \"{list_obj['name']}\"")
            return 'Concluída'
            
        # Considerar 'AGUARDANDO RETORNO DE TERCEIROS' como concluída
        if ('AGUARDANDO' in list_name_upper and 
            'RETORNO' in list_name_upper and 
            'TERCEIRO' in list_name_upper):
            logger.info(f"✅ AGUARDANDO TERCEIROS considerada CONCLUÍDA: \"{card.get('name')}\"")
            return 'Concluída'
            
        # Verificar mapeamento direto
        direct_status = LIST_STATUS_MAP.get(list_name_upper)
        if direct_status:
            logger.info(f"📋 Status mapeado diretamente: \"{card.get('name')}\" -> {direct_status}")
            
            # Verificar se está atrasada (exceto se concluída)
            if direct_status != 'Concluída' and card.get('due'):
                if self._is_overdue(card):
                    logger.info(f"⚠️ Tarefa ATRASADA detectada: \"{card.get('name')}\" (prazo: {card.get('due')})")
                    return 'Atrasada'
                    
            return direct_status
            
        # Verificação por palavras-chave para outros status
        if any(keyword in list_name_upper for keyword in ['BLOQUEADA', 'PARADA', 'AGUARDANDO']):
            logger.info(f"🚫 Status BLOQUEADA detectado: \"{card.get('name')}\"")
            return 'Bloqueada'
            
        if any(keyword in list_name_upper for keyword in ['PLANEJ', 'PLAN']):
            logger.info(f"📝 Status PLANEJAMENTO detectado: \"{card.get('name')}\"")
            return 'Planejamento'
            
        if 'RECORREN' in list_name_upper:
            logger.info(f"🔄 Status RECORRENTE detectado: \"{card.get('name')}\"")
            return 'Recorrente'
            
        # Verificar se está atrasada (padrão para tarefas em andamento)
        if card.get('due') and self._is_overdue(card):
            logger.info(f"⚠️ Tarefa ATRASADA detectada: \"{card.get('name')}\" (prazo: {card.get('due')})")
            return 'Atrasada'
            
        logger.info(f"📋 Status padrão EM ANDAMENTO: \"{card.get('name')}\" na lista \"{list_obj['name']}\"")
        return 'Em Andamento'
    
    def get_task_status_for_collaborator(self, card: Dict, collaborator_username: str, lists: List[Dict]) -> str:
        """
        Obtém status específico para criadores de conteúdo.
        
        Args:
            card: Card do Trello
            collaborator_username: Username do colaborador
            lists: Listas do board
            
        Returns:
            Status específico para o colaborador
        """
        # Verificar se o card está arquivado
        if card.get('closed', False):
            logger.info(f"📦 Card ARQUIVADO: \"{card.get('name')}\" - Status será CONCLUÍDA para {collaborator_username}")
            return 'Concluída'
            
        # Verificar se é um criador de conteúdo
        if collaborator_username not in CONTENT_CREATORS:
            return self.get_task_status(card, lists, [])  # Usar lógica padrão
            
        # Encontrar a lista do card
        list_obj = next((l for l in lists if l['id'] == card.get('idList')), None)
        if not list_obj:
            logger.warning(f"⚠️ Lista não encontrada para card: {card.get('name')} (ID: {card.get('idList')})")
            return 'Em Andamento'
            
        list_name_upper = list_obj['name'].upper().strip()
        logger.info(f"🎨 CRIADOR DE CONTEÚDO - Analisando status do card \"{card.get('name')}\" na lista \"{list_obj['name']}\" para {collaborator_username}")
        
        # Para criadores de conteúdo: qualquer coisa que NÃO seja "EM PROCESSO DE CONTEÚDO" é considerada concluída
        if list_name_upper == 'EM PROCESSO DE CONTEÚDO':
            logger.info(f"📝 CRIADOR DE CONTEÚDO - \"{collaborator_username}\": tarefa \"{card.get('name')}\" ainda EM ANDAMENTO (na lista de conteúdo)")
            
            # Verificar se está atrasada
            if card.get('due') and self._is_overdue(card):
                logger.info(f"⚠️ CRIADOR DE CONTEÚDO - Tarefa ATRASADA: \"{card.get('name')}\" (prazo: {card.get('due')})")
                return 'Atrasada'
                
            return 'Em Andamento'
        else:
            # Se não está mais em "EM PROCESSO DE CONTEÚDO", está concluída para o criador de conteúdo
            logger.info(f"✅ CRIADOR DE CONTEÚDO - \"{collaborator_username}\": tarefa \"{card.get('name')}\" CONCLUÍDA (saiu da lista de conteúdo)")
            return 'Concluída'
    
    def calculate_days_late(self, card: Dict) -> int:
        """
        Calcula dias de atraso de uma tarefa.
        
        Args:
            card: Card do Trello
            
        Returns:
            Número de dias de atraso
        """
        if not card.get('due'):
            return 0
            
        # Cards arquivados não têm atraso
        if card.get('closed', False):
            logger.info(f"📦 Card ARQUIVADO: \"{card.get('name')}\" - Sem atraso (arquivado)")
            return 0
            
        try:
            due_date_str = card['due']
            if due_date_str.endswith('Z'):
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
            else:
                due_date = datetime.fromisoformat(due_date_str).date()
                
            today = date.today()
            
            if today <= due_date:
                return 0
                
            days_late = (today - due_date).days
            logger.info(f"📅 Tarefa \"{card.get('name')}\": atraso de {days_late} dias (prazo: {due_date.strftime('%d/%m/%Y')})")
            
            return days_late
            
        except (ValueError, TypeError) as e:
            logger.error(f"Erro ao calcular atraso do card \"{card.get('name')}\": {e}")
            return 0
    
    def calculate_days_late_for_collaborator(self, card: Dict, collaborator_username: str, lists: List[Dict]) -> int:
        """
        Calcula dias de atraso específico para colaborador.
        
        Args:
            card: Card do Trello
            collaborator_username: Username do colaborador
            lists: Listas do board
            
        Returns:
            Número de dias de atraso específico para o colaborador
        """
        if not card.get('due'):
            return 0
            
        # Cards arquivados não têm atraso
        if card.get('closed', False):
            logger.info(f"📦 Card ARQUIVADO: \"{card.get('name')}\" - Sem atraso (arquivado)")
            return 0
            
        # Para criadores de conteúdo, só calcular atraso se ainda estiver na lista "EM PROCESSO DE CONTEÚDO"
        if collaborator_username in CONTENT_CREATORS:
            list_obj = next((l for l in lists if l['id'] == card.get('idList')), None)
            list_name_upper = list_obj['name'].upper().strip() if list_obj else ''
            
            # Se não está mais em "EM PROCESSO DE CONTEÚDO", não há atraso (tarefa foi concluída)
            if list_name_upper != 'EM PROCESSO DE CONTEÚDO':
                logger.info(f"✅ CRIADOR DE CONTEÚDO - \"{collaborator_username}\": sem atraso (tarefa saiu da lista de conteúdo)")
                return 0
                
            # Se ainda está em "EM PROCESSO DE CONTEÚDO", calcular atraso normalmente
            return self.calculate_days_late(card)
            
        # Para outros colaboradores, usar lógica padrão
        return self.calculate_days_late(card)
    
    def _is_overdue(self, card: Dict) -> bool:
        """Verifica se um card está atrasado."""
        if not card.get('due'):
            return False
            
        try:
            due_date_str = card['due']
            if due_date_str.endswith('Z'):
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
            else:
                due_date = datetime.fromisoformat(due_date_str).date()
                
            return date.today() > due_date
            
        except (ValueError, TypeError):
            return False
    
    def get_collaborator_name(self, card: Dict, members: List[Dict]) -> str:
        """
        Obtém nome do colaborador de um card.
        
        Args:
            card: Card do Trello
            members: Lista de membros
            
        Returns:
            Nome do colaborador ou 'Não atribuído'
        """
        id_members = card.get('idMembers', [])
        if not id_members:
            return 'Não atribuído'
            
        member = next((m for m in members if m['id'] == id_members[0]), None)
        return member['fullName'] if member else 'Não atribuído'
    
    def generate_task_reports(self, data: Dict[str, Any], start_date: date, end_date: date) -> List[TaskReport]:
        """
        Gera relatórios de tarefas com lógica corrigida para evitar duplicações.
        
        Args:
            data: Dados do Trello
            start_date: Data de início
            end_date: Data de fim
            
        Returns:
            Lista de relatórios de tarefas
        """
        cards = data.get('cards', [])
        lists = data.get('lists', [])
        members = data.get('members', [])
        
        filtered_cards = self.filter_cards_by_date_range(cards, start_date, end_date, lists)
        reports = []
        
        logger.info('=== GERAÇÃO DE RELATÓRIOS DE TAREFAS ===')
        logger.info(f'Total de cards filtrados: {len(filtered_cards)}')
        
        for card in filtered_cards:
            list_obj = next((l for l in lists if l['id'] == card.get('idList')), None)
            list_name = list_obj['name'] if list_obj else 'Lista não encontrada'
            
            id_members = card.get('idMembers', [])
            
            if not id_members:
                # Card sem colaboradores atribuídos
                task_status = self.get_task_status(card, lists, members)
                due_date_str = self._format_due_date(card.get('due'))
                
                reports.append(TaskReport(
                    task_id=card.get('id', ''),
                    collaborator_name='Não atribuído',
                    task_name=card.get('name', ''),
                    list_name=list_name,
                    due_date=due_date_str,
                    created_at=card.get('dateLastActivity', ''),
                    completed_at=card.get('dateLastActivity', '') if task_status == 'Concluída' else None,
                    status=task_status,
                    days_late=self.calculate_days_late(card),
                    observations=card.get('desc', '') or list_name,
                    grupo=None,
                    etapa_atual=get_etapa_atual(list_name),
                    finalizada_para_flavia=False,
                    feita=False,
                    em_revisao=is_em_revisao(list_name)
                ))
                
                logger.info(f"✅ Adicionado card sem atribuição: \"{card.get('name')}\"")
            else:
                # Card com colaboradores - LÓGICA CORRIGIDA
                card_members = [m for m in members if m['id'] in id_members]
                
                # Mapear membros por grupo para evitar duplicações
                grupos_encontrados = set()
                membros_sem_grupo = []
                
                # Primeiro, identificar todos os grupos únicos dos membros
                for member in card_members:
                    grupo = get_grupo_por_responsavel(member['username'])
                    if grupo:
                        grupos_encontrados.add(grupo.name)
                    else:
                        membros_sem_grupo.append(member)
                
                # Criar UMA entrada por grupo (não por membro do grupo)
                for nome_grupo in grupos_encontrados:
                    grupo = next((g for g in GRUPOS_MARKETING if g.name == nome_grupo), None)
                    if not grupo:
                        continue
                        
                    # Pegar todos os membros deste grupo que estão no card
                    membros_do_grupo = [m for m in card_members 
                                      if get_grupo_por_responsavel(m['username']) and 
                                         get_grupo_por_responsavel(m['username']).name == nome_grupo]
                    
                    collaborator_names = ', '.join(m['fullName'] for m in membros_do_grupo)
                    primeiro_membro = membros_do_grupo[0] if membros_do_grupo else None
                    
                    if primeiro_membro:
                        task_status = self.get_task_status_for_collaborator(card, primeiro_membro['username'], lists)
                        days_late = self.calculate_days_late_for_collaborator(card, primeiro_membro['username'], lists)
                        due_date_str = self._format_due_date(card.get('due'))
                        
                        reports.append(TaskReport(
                            task_id=card.get('id', ''),
                            collaborator_name=collaborator_names,
                            task_name=card.get('name', ''),
                            list_name=list_name,
                            due_date=due_date_str,
                            created_at=card.get('dateLastActivity', ''),
                            completed_at=card.get('dateLastActivity', '') if task_status == 'Concluída' else None,
                            status=task_status,
                            days_late=days_late,
                            observations=card.get('desc', '') or list_name,
                            grupo=grupo.name,
                            etapa_atual=get_etapa_atual(list_name),
                            finalizada_para_flavia=is_finalizada_para_flavia(list_name, grupo),
                            feita=is_feita(list_name, grupo),
                            em_revisao=is_em_revisao(list_name)
                        ))
                        
                        logger.info(f"✅ Adicionado card para {grupo.name}: \"{card.get('name')}\" - Colaboradores: {collaborator_names}")
                
                # Criar entradas individuais para membros sem grupo
                for member in membros_sem_grupo:
                    task_status = self.get_task_status_for_collaborator(card, member['username'], lists)
                    days_late = self.calculate_days_late_for_collaborator(card, member['username'], lists)
                    due_date_str = self._format_due_date(card.get('due'))
                    
                    reports.append(TaskReport(
                        task_id=card.get('id', ''),
                        collaborator_name=member['fullName'],
                        task_name=card.get('name', ''),
                        list_name=list_name,
                        due_date=due_date_str,
                        created_at=card.get('dateLastActivity', ''),
                        completed_at=card.get('dateLastActivity', '') if task_status == 'Concluída' else None,
                        status=task_status,
                        days_late=days_late,
                        observations=card.get('desc', '') or list_name,
                        grupo=None,
                        etapa_atual=get_etapa_atual(list_name),
                        finalizada_para_flavia=False,
                        feita=False,
                        em_revisao=is_em_revisao(list_name)
                    ))
                    
                    logger.info(f"✅ Adicionado card para membro sem grupo: \"{card.get('name')}\" - Colaborador: {member['fullName']}")
        
        logger.info(f"=== TOTAL DE REPORTS GERADOS: {len(reports)} ===")
        
        # Debug: mostrar breakdown de reports por grupo
        reports_por_grupo = {}
        for report in reports:
            grupo = report.grupo or 'Sem Grupo'
            reports_por_grupo[grupo] = reports_por_grupo.get(grupo, 0) + 1
            
        logger.info('📊 Breakdown de reports por grupo:')
        for grupo, count in reports_por_grupo.items():
            logger.info(f"  {grupo}: {count} reports")
            
        return reports
    
    def generate_report_summary(self, task_reports: List[TaskReport]) -> ReportSummary:
        """
        Gera resumo do relatório incluindo 4 grupos.
        
        Args:
            task_reports: Lista de relatórios de tarefas
            
        Returns:
            Resumo do relatório
        """
        logger.info('=== GERAÇÃO DE RESUMO DO RELATÓRIO ===')
        logger.info(f'Total de task reports para resumo: {len(task_reports)}')
        
        # Deduplicate tasks by task_id to avoid counting the same task multiple times
        unique_tasks_map = {}
        for task in task_reports:
            if task.task_id not in unique_tasks_map:
                unique_tasks_map[task.task_id] = task
        
        unique_tasks = list(unique_tasks_map.values())
        logger.info(f'Total de tarefas únicas para resumo: {len(unique_tasks)}')
        
        total_tasks = len(unique_tasks)
        completed_tasks = len([t for t in unique_tasks if t.status == 'Concluída'])
        in_progress_tasks = len([t for t in unique_tasks if t.status == 'Em Andamento'])
        late_tasks = len([t for t in unique_tasks if t.status == 'Atrasada'])
        overdue_tasks = late_tasks  # Atrasadas são as mesmas que em atraso
        blocked_tasks = len([t for t in unique_tasks if t.status == 'Bloqueada'])
        
        # Contar colaboradores únicos (deduplicar colaboradores agrupados)
        unique_collaborators = set()
        for task in unique_tasks:
            if ',' in task.collaborator_name:
                # Se for colaborador agrupado, adicionar cada nome individualmente
                for name in task.collaborator_name.split(','):
                    unique_collaborators.add(name.strip())
            else:
                unique_collaborators.add(task.collaborator_name)
                
        total_collaborators = len(unique_collaborators)
        
        # Resumo por grupo - incluindo todos os 4 grupos
        group_summaries = []
        
        for grupo_obj in GRUPOS_MARKETING:
            grupo = grupo_obj.name
            responsaveis = [r.nome for r in grupo_obj.responsaveis]
            group_tasks = [t for t in task_reports if t.grupo == grupo]
            
            # Deduplicate group tasks by task_id to avoid counting the same task multiple times
            unique_group_tasks_map = {}
            for task in group_tasks:
                if task.task_id not in unique_group_tasks_map:
                    unique_group_tasks_map[task.task_id] = task
            unique_group_tasks = list(unique_group_tasks_map.values())
            
            completed = len([t for t in unique_group_tasks if t.status == 'Concluída'])
            in_progress = len([t for t in unique_group_tasks if t.status == 'Em Andamento'])
            late = len([t for t in unique_group_tasks if t.status == 'Atrasada'])
            blocked = len([t for t in unique_group_tasks if t.status == 'Bloqueada'])
            
            completed_with_due = [t for t in unique_group_tasks if t.status == 'Concluída' and t.due_date != 'Não definida']
            on_time = len([t for t in completed_with_due if t.days_late == 0])
            late_deliv = len([t for t in completed_with_due if t.days_late > 0])
            
            logger.info(f"📊 {grupo}: {len(unique_group_tasks)} tarefas únicas ({completed} concluídas, {in_progress} em andamento, {late} atrasadas)")
            
            group_summaries.append(GroupReportSummary(
                grupo=grupo,
                responsaveis=responsaveis,
                total_tasks=len(unique_group_tasks),
                completed_tasks=completed,
                in_progress_tasks=in_progress,
                late_tasks=late,
                blocked_tasks=blocked,
                on_time_deliveries=on_time,
                late_deliveries=late_deliv
            ))
        
        # Adicionar grupo "Sem Grupo" se houver tarefas sem grupo
        sem_grupo_tasks = [t for t in task_reports if not t.grupo]
        if sem_grupo_tasks:
            # Deduplicate sem grupo tasks by task_id to avoid counting the same task multiple times
            unique_sem_grupo_tasks_map = {}
            for task in sem_grupo_tasks:
                if task.task_id not in unique_sem_grupo_tasks_map:
                    unique_sem_grupo_tasks_map[task.task_id] = task
            unique_sem_grupo_tasks = list(unique_sem_grupo_tasks_map.values())
            
            completed = len([t for t in unique_sem_grupo_tasks if t.status == 'Concluída'])
            in_progress = len([t for t in unique_sem_grupo_tasks if t.status == 'Em Andamento'])
            late = len([t for t in unique_sem_grupo_tasks if t.status == 'Atrasada'])
            blocked = len([t for t in unique_sem_grupo_tasks if t.status == 'Bloqueada'])
            
            completed_with_due = [t for t in unique_sem_grupo_tasks if t.status == 'Concluída' and t.due_date != 'Não definida']
            on_time = len([t for t in completed_with_due if t.days_late == 0])
            late_deliv = len([t for t in completed_with_due if t.days_late > 0])
            
            logger.info(f"📊 Sem Grupo: {len(unique_sem_grupo_tasks)} tarefas únicas ({completed} concluídas, {in_progress} em andamento, {late} atrasadas)")
            
            group_summaries.append(GroupReportSummary(
                grupo='Sem Grupo',
                responsaveis=[],
                total_tasks=len(unique_sem_grupo_tasks),
                completed_tasks=completed,
                in_progress_tasks=in_progress,
                late_tasks=late,
                blocked_tasks=blocked,
                on_time_deliveries=on_time,
                late_deliveries=late_deliv
            ))
        
        logger.info('==============================')
        
        return ReportSummary(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            in_progress_tasks=in_progress_tasks,
            late_tasks=late_tasks,
            overdue_tasks=overdue_tasks,
            blocked_tasks=blocked_tasks,
            total_collaborators=total_collaborators,
            group_summaries=group_summaries
        )
    
    def generate_collaborator_reports(self, task_reports: List[TaskReport]) -> List[CollaboratorReport]:
        """
        Gera relatórios individuais por colaborador evitando duplicações.
        
        Args:
            task_reports: Lista de relatórios de tarefas
            
        Returns:
            Lista de relatórios de colaboradores
        """
        collaborator_map = {}
        
        logger.info('=== GERAÇÃO DE RELATÓRIOS DE COLABORADORES ===')
        logger.info(f'Total de task reports: {len(task_reports)}')
        
        # Agrupar tarefas por colaborador único (sem duplicar)
        for task in task_reports:
            collaborator = task.collaborator_name
            
            # Se é um colaborador agregado (com vírgulas), dividir e atribuir proporcionalmente
            if ',' in collaborator:
                nomes = [nome.strip() for nome in collaborator.split(',')]
                
                # Para colaboradores agrupados, criar uma entrada para cada um com a tarefa completa
                for nome in nomes:
                    if nome not in collaborator_map:
                        collaborator_map[nome] = []
                        
                    # Criar uma cópia da task para cada colaborador individual
                    task_copy = TaskReport(
                        task_id=task.task_id,
                        collaborator_name=nome,
                        task_name=task.task_name,
                        list_name=task.list_name,
                        due_date=task.due_date,
                        created_at=task.created_at,
                        completed_at=task.completed_at,
                        status=task.status,
                        days_late=task.days_late,
                        observations=task.observations,
                        grupo=task.grupo,
                        etapa_atual=task.etapa_atual,
                        finalizada_para_flavia=task.finalizada_para_flavia,
                        feita=task.feita,
                        em_revisao=task.em_revisao
                    )
                    collaborator_map[nome].append(task_copy)
            else:
                # Colaborador individual
                if collaborator not in collaborator_map:
                    collaborator_map[collaborator] = []
                collaborator_map[collaborator].append(task)
        
        logger.info(f'Colaboradores únicos identificados: {len(collaborator_map)}')
        
        # Gerar relatório para cada colaborador
        reports = []
        
        for collaborator_name, tasks in collaborator_map.items():
            # Deduplicate tasks by task name + group to avoid counting the same task multiple times
            unique_tasks_map = {}
            for task in tasks:
                key = f"{task.task_name}-{task.grupo or 'no-group'}"
                if key not in unique_tasks_map:
                    unique_tasks_map[key] = task
                    
            unique_tasks = list(unique_tasks_map.values())
            
            total_tasks = len(unique_tasks)
            completed_tasks = len([t for t in unique_tasks if t.status == 'Concluída'])
            in_progress_tasks = len([t for t in unique_tasks if t.status == 'Em Andamento'])
            late_tasks = len([t for t in unique_tasks if t.status == 'Atrasada'])
            blocked_tasks = len([t for t in unique_tasks if t.status == 'Bloqueada'])
            pending_tasks = total_tasks - completed_tasks
            
            # Taxa de conclusão em percentual (0-100)
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Média de atraso apenas para tarefas que estão realmente atrasadas (não concluídas)
            late_days = [t.days_late for t in unique_tasks if t.days_late > 0 and t.status in ['Atrasada', 'Em Andamento']]
            average_days_late = (sum(late_days) / len(late_days)) if late_days else 0
            
            logger.info(f"👤 {collaborator_name}: {total_tasks} tarefas únicas ({completed_tasks} concluídas - {(completion_rate * 100):.1f}%)")
            
            # Ordenar tarefas por status (atrasadas primeiro, depois concluídas, depois outras) e depois por nome
            sorted_tasks = sorted(unique_tasks, key=lambda t: (
                0 if t.status == 'Atrasada' else 1 if t.status == 'Concluída' else 2,
                t.task_name
            ))
            
            reports.append(CollaboratorReport(
                collaborator_name=collaborator_name,
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                in_progress_tasks=in_progress_tasks,
                pending_tasks=pending_tasks,
                late_tasks=late_tasks,
                blocked_tasks=blocked_tasks,
                completion_rate=completion_rate,
                average_days_late=round(average_days_late),
                tasks=sorted_tasks
            ))
        
        # Ordenar por taxa de conclusão
        reports.sort(key=lambda r: r.completion_rate, reverse=True)
        
        logger.info('=== RELATÓRIOS DE COLABORADORES GERADOS ===')
        
        return reports
    
    def _format_due_date(self, due_date_str: Optional[str]) -> str:
        """Formata data de vencimento para exibição."""
        if not due_date_str:
            return 'Não definida'
            
        try:
            if due_date_str.endswith('Z'):
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            else:
                due_date = datetime.fromisoformat(due_date_str)
                
            return due_date.strftime('%d/%m/%Y')
            
        except (ValueError, TypeError):
            return 'Não definida'
