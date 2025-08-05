#!/usr/bin/env python3
from src.data_processor import TrelloDataProcessor
from src.config import GRUPOS_MARKETING
from datetime import date, timedelta

# Dados de teste
test_data = {
    'name': 'Test Board',
    'cards': [
        {
            'id': 'card1',
            'name': 'Tarefa Concluída',
            'idList': 'list2',
            'idMembers': ['member1'],
            'due': '2024-12-01T12:00:00.000Z',
            'dateLastActivity': '2024-12-15T10:30:00.000Z',
            'closed': False
        },
        {
            'id': 'card2', 
            'name': 'Tarefa Atrasada',
            'idList': 'list1',
            'idMembers': ['member1'],
            'due': '2024-11-01T12:00:00.000Z',
            'dateLastActivity': '2024-12-15T10:30:00.000Z',
            'closed': False
        }
    ],
    'lists': [
        {'id': 'list1', 'name': 'EM PROCESSO DE CONTEÚDO'},
        {'id': 'list2', 'name': 'FEITOS'}
    ],
    'members': [
        {'id': 'member1', 'username': 'jamillyfreitass', 'fullName': 'Jamily Freitas'}
    ]
}

processor = TrelloDataProcessor()
start_date = date(2024, 11, 1)
end_date = date(2024, 12, 31)

task_reports = processor.generate_task_reports(test_data, start_date, end_date)
collab_reports = processor.generate_collaborator_reports(task_reports)

print('=== TESTE DE CÁLCULOS ===')
for collab in collab_reports:
    print(f'Colaborador: {collab.collaborator_name}')
    print(f'Total: {collab.total_tasks}')
    print(f'Concluídas: {collab.completed_tasks}')
    print(f'Taxa: {collab.completion_rate:.1f}%')
    print(f'Média atraso: {collab.average_days_late} dias')
    print('---')
