# Trelliq Web App - Sistema de Relatórios Trello

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

## 🌐 Acesso Online

Este é um **web app completo** que roda na nuvem. Você pode acessar diretamente pelo navegador sem precisar instalar nada!

### 🚀 Deploy Automático

**Opção 1: Streamlit Community Cloud (Recomendado)**
1. Faça push deste código para GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte seu repositório GitHub
4. Deploy automático em segundos!

**Opção 2: Railway**
1. Conecte seu GitHub ao [Railway](https://railway.app)
2. Deploy com um clique
3. URL personalizada disponível

**Opção 3: Heroku**
```bash
# Deploy via Heroku CLI
heroku create seu-app-trelliq
git push heroku main
```

## 📱 Funcionalidades Web

- ✅ **100% Web-based**: Não precisa instalar nada
- ✅ **Responsivo**: Funciona em mobile, tablet e desktop  
- ✅ **Upload de Arquivos**: Arraste e solte arquivos JSON
- ✅ **Download Direto**: Baixe relatórios Excel/CSV
- ✅ **Compartilhável**: Envie o link para sua equipe
- ✅ **Sempre Atualizado**: Atualizações automáticas

## 🛠️ Tecnologias

- Python 3.9
- Streamlit 1.28.0
- Pandas 2.1.0
- Plotly 5.17.0
- OpenPyXL 3.1.2

## 🎯 Como Usar Online

1. **Acesse o link do app** (após deploy)
2. **Faça upload do JSON do Trello** 
3. **Visualize relatórios em tempo real**
4. **Baixe os resultados** 
5. **Compartilhe com a equipe**

## 📊 Recursos do Web App

### Interface Moderna
- Dashboard interativo com métricas
- Gráficos dinâmicos e responsivos
- Tema profissional customizável

### Processamento Inteligente
- Eliminação automática de duplicatas
- Suporte aos 4 grupos de marketing
- Análise de colaboradores em tempo real

### Exportação Profissional
- Relatórios Excel formatados
- CSVs para análise externa
- JSONs para integração

## 🔧 Configuração para Deploy

### Arquivos de Configuração Web
- `Procfile` - Configuração do servidor
- `.streamlit/config.toml` - Tema e settings
- `runtime.txt` - Versão Python
- `requirements.txt` - Dependências

## 📁 Estrutura do Projeto

```
trelliq-python/
├── app.py                    # Aplicação principal Streamlit
├── requirements.txt          # Dependências Python
├── Procfile                  # Configuração do servidor web
├── runtime.txt              # Versão Python para deploy
├── .streamlit/
│   └── config.toml          # Configurações do Streamlit
├── src/
│   ├── data_processor.py    # Processamento de dados
│   ├── config.py           # Configurações dos grupos
│   └── utils.py            # Utilitários gerais
└── data/
    └── samples/            # Dados de exemplo
```

## 🔧 Configuração dos Grupos

Os 4 grupos de marketing são configuráveis através do arquivo `src/config.py`:

- **Grupo 1**: Criadores de Conteúdo
- **Grupo 2**: Social Media  
- **Grupo 3**: Análise e Relatórios
- **Grupo 4**: Flávia + Coordenação

## 📊 Relatórios Gerados

- Relatório de Tarefas por Grupo
- Análise de Colaboradores
- Distribuição de Status
- Métricas Avançadas
- Tendências Temporais

## 🌟 Vantagens do Web App

1. **Acesso Universal**: Qualquer pessoa com o link pode usar
2. **Zero Instalação**: Funciona direto no navegador
3. **Sempre Online**: Disponível 24/7
4. **Auto-scaling**: Suporta múltiplos usuários
5. **Atualizações Automáticas**: Sempre na versão mais recente

## 📱 Compatibilidade

- ✅ Chrome, Firefox, Safari, Edge
- ✅ Mobile (iOS/Android)
- ✅ Tablets e iPads
- ✅ Todas as resoluções

## 🚀 Performance

- Carregamento rápido (< 3s)
- Processamento eficiente com pandas
- Cache inteligente para dados
- Otimizado para web

## 🐛 Solução de Problemas

Este sistema foi desenvolvido para resolver problemas de duplicação encontrados na versão TypeScript anterior, utilizando pandas para processamento eficiente de dados.

---

**🎉 Pronto para usar! Deploy seu web app em minutos e tenha acesso aos relatórios Trello de qualquer lugar!**
