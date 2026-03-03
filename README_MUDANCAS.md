# Documentação de Mudanças - Automação de Planilhas

## 📋 Resumo Geral

A aplicação foi reorganizada de forma abrangente para melhorar a estrutura do projeto, facilitar manutenção futura e resolver problemas de imports e compatibilidade de dados. Este documento detalha **todas as mudanças** realizadas.

---

## 🏗️ 1. Reorganização de Pastas

### Antes (Estrutura Desorganizada)
```
D:\RESULTADOS\
├── app.py                    # arquivo raiz solto
├── style.css                 # arquivo solto
├── requirements.txt
├── requeriments.txt          # (duplicado com typo)
├── image/                    # pasta sem organização
│   ├── icon.png
│   └── logo_consulpam.png
├── automacao-planilhas/      # (pasta vazia ou desorganizada)
└── venv/                     # ambiente virtual
```

### Depois (Estrutura Organizada)
```
D:\RESULTADOS\
├── automacao_planilhas/      # pasta principal do projeto
│   ├── __init__.py           # marca como pacote Python
│   ├── app.py                # aplicação Streamlit (MOVIDO)
│   ├── utils.py              # funções auxiliares (CRIADO)
│   └── assets/               # recursos da aplicação
│       ├── image/
│       │   ├── icon.png      # (MOVIDO)
│       │   └── logo_consulpam.png (MOVIDO)
│       └── style.css         # (MOVIDO)
├── requirements.txt          # (CONSOLIDADO - removido duplicado)
├── README.md                 # documentação do projeto
├── README_MUDANCAS.md        # este arquivo
└── venv/                     # ambiente virtual
```

### Ganhos:
- ✅ **Estrutura profissional**: projeto encapsulado em uma pasta com subpastas lógicas
- ✅ **Sem duplicatas**: apenas um `requirements.txt`
- ✅ **Assets organizados**: imagens e estilos em pasta `assets/`
- ✅ **Código modular**: funções separadas em `utils.py`

---

## 🔧 2. Mudanças no Código - `app.py`

### 2.1 Configuração de Caminhos (Linhas 1-16)

#### Antes:
```python
import streamlit as st
import pandas as pd
import io 
from PIL import Image 

def preparar_excel(df):  # função definida inline
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Lista')
    return output.getvalue()

favicon = Image.open("image/icon.png")            # caminho relativo simples
logo_consul = Image.open("image/logo_consulpam.png")
```

#### Depois:
```python
import streamlit as st
import pandas as pd
import io 
from PIL import Image 
import os

# compute base directory for assets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import sys
# garantir que a raiz do projeto esteja no path para imports absolutos funcionarem
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from automacao_planilhas.utils import preparar_excel

favicon = Image.open(os.path.join(BASE_DIR, "assets", "image", "icon.png"))
logo_consul = Image.open(os.path.join(BASE_DIR, "assets", "image", "logo_consulpam.png"))
```

#### Explicação:
- **`BASE_DIR`**: armazena o caminho completo da pasta `automacao_planilhas/` (onde `app.py` está)
  - `os.path.abspath(__file__)` = "D:\RESULTADOS\automacao_planilhas\app.py"
  - `os.path.dirname(...)` = "D:\RESULTADOS\automacao_planilhas"
- **`PROJECT_ROOT`**: armazena o caminho da raiz do projeto ("D:\RESULTADOS")
  - Necessário porque o Streamlit executa o arquivo como script, não como pacote
  - `sys.path.insert(0, PROJECT_ROOT)` adiciona a raiz ao path Python para permitir imports absolutos
- **`os.path.join(...)`**: constrói caminhos de forma independente do SO (Windows/Linux/Mac)
  - Antes: `"image/icon.png"` (simples, mas quebrava se a estrutura mudasse)
  - Depois: `os.path.join(BASE_DIR, "assets", "image", "icon.png")` (robusto e reutilizável)

---

### 2.2 Normalização de Tipos de Dados (Linhas 66-70)

#### Problema:
Ao carregar planilhas Excel, algumas colunas continham **tipos mistos** (datetime, int, string na mesma coluna). Isso causava erro ao exibir via PyArrow do Streamlit:
```
pyarrow.lib.ArrowTypeError: Expected bytes, got a 'datetime.datetime' object
```

#### Solução Implementada:
```python
# Normalizar tipos de dados: converter colunas com tipos mistos para string
# Isso evita erros de conversão ao exibir e processar DataFrames
for col in df.columns:
    df[col] = df[col].fillna('').astype(str)
```

#### Como Funciona:
1. **`fillna('')`**: substitui valores vazios (NaN/None) por string vazia
2. **`astype(str)`**: converte todos os valores da coluna para string
3. **Loop em todas as colunas**: garante normalização completa
4. **Benefício**: elimina erros de tipo, permite processamento uniforme

#### Exemplo:
```
Antes: ORGÃO EXPEDIDOR = [datetime(2020, 1, 1), 123, 'PC']  → ERRO
Depois: ORGÃO EXPEDIDOR = ['2020-01-01 00:00:00', '123', 'PC']  → OK
```

---

### 2.3 Substituição de `use_container_width` (Múltiplos Locais)

#### Problema:
O parâmetro `use_container_width` foi **deprecado** no Streamlit 1.50+. Recomenda-se usar `width` em seu lugar.

#### Antes:
```python
st.dataframe(df, use_container_width=True)
st.sidebar.image(logo_consul, use_container_width=True)
```

#### Depois:
```python
st.dataframe(df, width='stretch')
st.sidebar.image(logo_consul, use_container_width=False)  # sidebar mantém compatibilidade
```

#### Valores:
- **`width='stretch'`**: ocupa a largura disponível (equivalente a `use_container_width=True`)
- **`width='content'`**: usa apenas espaço necessário (equivalente a `use_container_width=False`)

---

## 📦 3. Arquivo Novo - `utils.py`

### Localização:
`d:\RESULTADOS\automacao_planilhas\utils.py`

### Conteúdo:
```python
import io
import pandas as pd


def preparar_excel(df):
    """Return bytes representing an Excel file with a single sheet named 'Lista'."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Lista")
    return output.getvalue()
```

### Razão:
- **Separação de responsabilidades**: funções auxiliares não devem ficar no arquivo principal
- **Reutilização**: a função `preparar_excel()` pode ser importada em outros módulos
- **Manutenção**: código mais limpo e fácil de testar

### Como Usar:
```python
from automacao_planilhas.utils import preparar_excel

dados = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
arquivo_bytes = preparar_excel(dados)
# arquivo_bytes pode ser enviado como download
```

---

## 🚀 4. Como Rodar a Aplicação

### Pré-requisitos:
- Python 3.10+ instalado
- Git (opcional, mas recomendado)

### Passos:

#### 1. Ativar o Ambiente Virtual
```powershell
cd D:\RESULTADOS
.\venv\Scripts\Activate.ps1
```

Se houver erro de política de execução:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
.\venv\Scripts\Activate.ps1
```

#### 2. Instalar Dependências (primeira vez)
```powershell
pip install -r requirements.txt
```

#### 3. Rodar a Aplicação
```powershell
streamlit run automacao_planilhas/app.py
```

#### 4. Acessar no Navegador
- Local: http://localhost:8501
- Rede: http://192.168.0.110:8501

---

## 📊 5. Fluxo de Funcionamento da Aplicação

### Passo-a-Passo:

1. **Upload de Arquivo**
   - Usuário carrega .xlsx ou .xls via sidebar
   - Detecta formato (`endswith('.xls')`)
   - Lê com engine apropriado (`xlsxwriter` para .xlsx, `xlrd` para .xls)

2. **Normalização de Dados**
   - Converte todas as colunas para string (visto acima)
   - Evita erros de tipo ao exibir

3. **Processamento de Data**
   - Se coluna `NASCIMENTO` existir:
     - Converte para formato datetime
     - Calcula idade atual e média
     - Cria coluna `IDADE_CONCURSO` (baseada em data de corte)
     - Filtra idosos (idade ≥ 60)

4. **Exibição de Estatísticas**
   - Mostra métrica: Total de candidatos
   - Mostra métrica: Média de idade
   - Mostra métrica: Quantidade de idosos

5. **Filtros de Cotas**
   - Filtra por coluna `NEGRO` (valor = "SIM")
   - Filtra por coluna `DEFICIENTE` (valor = "SIM")
   - Combina filtros (candidatos que são Negro E Deficiente)

6. **Abas de Visualização**
   - **Todos**: todos os candidatos
   - **Idosos**: candidatos com 60+ anos
   - **Negros**: candidatos marcados como Negro
   - **PCD**: candidatos marcados como Deficiente
   - **Negros e PCD**: combinação dos dois

7. **Download**
   - Permite baixar lista de idosos em .xlsx

---

## 🔍 6. Estrutura do Código - Mapa de Funções

| Função | Arquivo | Linha | Propósito |
|--------|---------|-------|-----------|
| `preparar_excel()` | `utils.py` | 5-11 | Converte DataFrame para bytes Excel |
| Setup da página | `app.py` | 20-27 | Configura título, layout, favicon |
| Upload de arquivo | `app.py` | 42-48 | Interface de upload no sidebar |
| Leitura do Excel | `app.py` | 54-62 | Detecta formato e lê arquivo |
| Normalização | `app.py` | 64-68 | Converte tipos para string |
| Cálculo de idade | `app.py` | 70-92 | Calcula idade atual e por data de corte |
| Filtros de cotas | `app.py` | 105-130 | Filtra por Negro/PCD |
| Exibição | `app.py` | 131-202 | Renderiza abas e tabelas |

---

## 📝 7. Dependências Principais

### Arquivo: `requirements.txt`

```
streamlit==1.54.0      # Framework web
pandas==2.3.3          # Processamento de dados
openpyxl==3.1.5        # Leitura/escrita .xlsx
xlrd==2.0.2            # Leitura de .xls antigos
xlsxwriter==3.2.9      # Escrita de .xlsx
pillow==12.1.1         # Processamento de imagens
```

### Por que cada uma?
- **streamlit**: cria a interface web
- **pandas**: manipula DataFrames (leitura, filtros, cálculos)
- **openpyxl/xlrd/xlsxwriter**: suporte para Excel antigo e novo
- **pillow**: carrega imagens (favicon, logos)

---

## 🐛 8. Problemas Resolvidos

| Problema | Causa | Solução |
|----------|-------|--------|
| **ImportError: relative import com no parent package** | Streamlit executa como script, não pacote | Adicionado `sys.path` e imports absolutos |
| **ModuleNotFoundError: automacao_planilhas** | Root não estava em sys.path | `sys.path.insert(0, PROJECT_ROOT)` |
| **NameError: BASE_DIR not defined** | Ordem de definição errada | Movido `BASE_DIR` para cima do arquivo |
| **ArrowTypeError em tipos mistos** | Colunas com datetime + int + string | Normalização com `.fillna('').astype(str)` |
| **Warnings de use_container_width** | Parâmetro descontinuado | Substituído por `width='stretch'` |

---

## 🎯 9. Próximas Melhorias Sugeridas

### Curto Prazo (Fáceis):
- [ ] Adicionar validação de colunas obrigatórias
- [ ] Permitir download de mais filtros (negros, PCD, etc.)
- [ ] Customizar cor das abas
- [ ] Adicionar logging de erros

### Médio Prazo (Moderados):
- [ ] Criar testes unitários para `utils.py`
- [ ] Separar lógica de filtros em módulo `filters.py`
- [ ] Adicionar cache ao Streamlit para melhorar performance
- [ ] Permitir configuração de colunas dinamicamente

### Longo Prazo (Complexos):
- [ ] Banco de dados para histórico de uploads
- [ ] Autenticação de usuários
- [ ] Dashboard com gráficos (matplotlib/plotly)
- [ ] Suporte para múltiplos formatos de entrada

---

## 📚 10. Como Continuar Daqui

### Para Adicionar Novas Funcionalidades:

1. **Função simples** → adicionar em `utils.py`
   ```python
   # Em utils.py
   def filtrar_por_ano(df, coluna, ano):
       """Filtra DataFrame por ano em uma coluna específica."""
       df[coluna] = pd.to_datetime(df[coluna])
       return df[df[coluna].dt.year == ano]
   
   # Em app.py
   from automacao_planilhas.utils import filtrar_por_ano
   df_filtrado = filtrar_por_ano(df, "NASCIMENTO", 2000)
   ```

2. **Novo módulo** → criar arquivo em `automacao_planilhas/`
   ```
   automacao_planilhas/
   ├── app.py
   ├── utils.py
   ├── filters.py       # ← novo módulo para filtros complexos
   ├── validators.py    # ← novo módulo para validação
   └── assets/
   ```

3. **Testar alterações**:
   ```powershell
   streamlit run automacao_planilhas/app.py --logger.level=debug
   ```

4. **Git Workflow**:
   ```powershell
   git add -A
   git commit -m "Descrição das mudanças"
   git push
   ```

---

## 📖 Exemplo de Extensão: Adicionar Novo Filtro

Se quiser **adicionar filtro por gênero**, faça assim:

### 1. Em `utils.py`, adicione:
```python
def filtrar_por_genero(df, coluna='SEXO', genero='F'):
    """Filtra candidatos por gênero."""
    return df[df[coluna].astype(str).str.upper() == genero.upper()]
```

### 2. Em `app.py`, importe e use:
```python
from automacao_planilhas.utils import filtrar_por_genero, preparar_excel

# Após normalização de dados...
if "SEXO" in df.columns:
    df_feminino = filtrar_por_genero(df, 'SEXO', 'F')
    
    st.metric("Mulheres", len(df_feminino))
    st.dataframe(df_feminino, width='stretch')
```

---

## ✅ Checklist de Validação

Após rodar a aplicação, você deve verificar:

- [ ] App inicia sem erros em `http://localhost:8501`
- [ ] Imagens (favicon, logo) carregam corretamente
- [ ] Pode fazer upload de arquivo .xlsx
- [ ] Dados são exibidos em tabela
- [ ] Abas funcionam (Todos, Idosos, Negros, PCD, Negros e PCD)
- [ ] Métricas calculam corretamente
- [ ] Download de .xlsx funciona
- [ ] Não há warnings no terminal

---

## 📞 Suporte

Se encontrar erros:

1. **Verifique se o venv está ativado** (deve mostrar `(venv)` no prompt)
2. **Instale dependências**: `pip install -r requirements.txt`
3. **Limpe cache do Streamlit**: `streamlit cache clear`
4. **Reinicie a app**: Ctrl+C no terminal e rode novamente
5. **Verifique logs**: roda com `streamlit run ... --logger.level=debug`

---

**Última atualização**: 3 de março de 2026
