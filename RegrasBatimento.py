import pandas as pd
import openai
import streamlit as st
import os

# Função para sugerir a origem dos datasets usando a API GPT
def suggest_origin(data, dataset_name, api_key):
    # Montar uma descrição do dataset com as primeiras linhas e nomes de colunas
    description = (
        f"{dataset_name} possui as seguintes colunas:\n{', '.join(data.columns)}\n"
        f"Aqui estão alguns exemplos de registros:\n{data.head().to_string(index=False)}\n"
        "Sessão 1 - Análise dos Arquivos:"
        "Identificação da Origem do Arquivo"
        "Analise as colunas e os valores de cada arquivo para sugerir sua possível origem. Para isso, identifique: "
        "Sistema de Mercado: Qual é o possível sistema de mercado que gerou este arquivo? Exemplo: TOTVS Protheus."
        "Assunto Principal: Qual é o principal tema ou tipo de transação abordada neste arquivo? Exemplo: Transações de renda fixa."
        "Área da Empresa: Qual área de uma empresa, geralmente, utiliza este tipo de arquivo? Exemplo: Custódia - Renda Fixa."
        "Observação: Redija a descrição de cada arquivo de maneira sucinta, com no máximo 3 linhas para cada um."

        "Exemplo de Resposta"
        "Arquivo 1:"
        "Sistema de Mercado: TOTVS Protheus"
        "Assunto Principal: Transações de renda fixa"
        "Área da Empresa: Custódia - Renda Fixa"

    )
    
    openai.api_key = api_key

    try:
        # Faz a chamada à API corretamente
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Você é um assistente e engenheiro de dados."},
                        {"role": "user", "content": description}
                    ])
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Ocorreu um erro ao chamar a API: {e}"

# Função para sugerir regras de batimento usando a API GPT
def suggest_match_rules(data_a, data_b, api_key):
    prompt = (
        f"Eu tenho dois datasets. O primeiro é:\n{data_a.head().to_string()}\n"
        f"O segundo é:\n{data_b.head().to_string()}\n"
        "Organize a resposta em sessões."
        
        "Sessão 2 - Colunas Potenciais. "
        "Poderia primeiramente identificar TODAS as colunas potenciais para serem conciliadas? "
        "Para garantir uma conciliação eficiente entre datasets, é importante seguir um processo bem estruturado para identificar as colunas mais apropriadas. Vou detalhar o escopo para que todos os campos potenciais que podem ser submetidos à conciliação sejam analisados corretamente."
        "1. Identificação de Colunas Potenciais para Conciliação. Objetivo: Mapear todas as colunas dos datasets que possuam potencial de uso no processo de conciliação, ou seja, aquelas que contêm dados relevantes que podem ser comparados entre os conjuntos de dados (datasets)."
        "Critérios: Durante essa etapa, cada coluna será avaliada de acordo com os seguintes aspectos: "
        "Valores Não Nulos: Colunas com uma grande quantidade de registros em branco (nulos) não são elegíveis para conciliação, pois isso prejudicaria a precisão e completude da correspondência entre os datasets."
        "Correspondência de Valores: Colunas que possuem muitos valores únicos ou valores que não têm correspondência direta no outro dataset também devem ser descartadas, pois dificultam a criação de um vínculo consistente entre os datasets."
        "Relevância dos Dados: Colunas com valores essenciais para a operação, como códigos, números de documentos (ex.: número de pedido, número de nota fiscal) ou datas importantes, são preferenciais, pois facilitam a criação de regras de batimento que realmente agregam valor ao processo de conciliação."
        "2. Critérios de Elegibilidade para Colunas"
        "A análise das colunas potenciais precisa considerar diversos critérios que vão garantir a eficácia e a eficiência do processo. Alguns dos principais pontos a serem considerados são: "
        "Tipo de Dado: O tipo de dado na coluna (numérico, texto, data) deve ser analisado para verificar se ele permite comparações diretas ou se será necessário algum tipo de transformação. "
        "Frequência de Valores Repetidos: Colunas com valores altamente repetitivos (ex.: status, categorias amplas) podem não ser boas opções para conciliação direta, pois não contribuem para a distinção entre registros. "
        "Granularidade dos Dados: Colunas que oferecem granularidade suficiente para diferenciar os registros, como números de pedido específicos, são ideais, enquanto colunas que agregam informações gerais (ex.: cidade, país) podem não ser adequadas."
        "Exclusividade dos Valores: Colunas que possuem identificadores únicos ou quase únicos (como ID de cliente ou SKU de produto) são preferenciais para conciliações, pois facilitam o pareamento direto entre os datasets."
        "3. Processo de Seleção das Colunas para Conciliação "
        "Passo 1: Identificação Inicial - Listar todas as colunas de cada dataset, nomeando e categorizando as colunas de acordo com seu tipo de dado e função no contexto de cada dataset (ex.: identificadores, datas, valores monetários, etc.)."
        "Passo 2: Verificação de Completeness (Completude) - Avaliar a quantidade de registros preenchidos em cada coluna. Colunas com um alto número de valores nulos ou ausentes devem ser descartadas."
        "Passo 3: Análise de Frequência e Distribuição - Examinar a frequência e distribuição dos valores nas colunas. Colunas com dados duplicados frequentes ou com uma distribuição altamente uniforme podem ser menos úteis para conciliações."
        "Passo 4: Teste de Correspondência Inicial - Realizar uma análise de batimento entre colunas dos dois datasets para identificar quais colunas têm maior chance de correspondência. Este teste preliminar ajudará a detectar colunas onde os valores são consistentes entre os datasets. "
        "4. Exemplos de Colunas Potenciais para Conciliação "
        "Identificadores Únicos: Número de Pedido, ID de Cliente, Número de Nota Fiscal, SKU do Produto. "
        "Informações Temporais: Datas de Emissão, Datas de Vencimento, Período (mês/ano). "
        "Valores Monetários: Valor do Pedido, Valor Pago, Valor de Imposto, Descontos. "
        "Outros Campos Específicos: Código de Produto, Código de Centro de Custo, Referência de Pagamento. "
        "5. Cuidados no Processo"
        "Evitar Exclusões Precipitadas: Durante o processo, é fundamental não descartar colunas potenciais sem uma análise cuidadosa, pois uma coluna que parece irrelevante à primeira vista pode, na verdade, agregar valor ao processo de conciliação."
        "Exploração de Dados Complementares: Em casos onde não há uma correspondência direta entre os datasets, pode-se explorar combinações de colunas (ex.: combinação entre ID de cliente + Data de Pedido) que podem aumentar a precisão do processo."
        
         "Sessão 3 - Ajustes nos dados. "
         "Identifique e aplique potenciais ajustes (preparações) nas colunas tais como retirada de espaços, "
         "fórmulas entre colunas a serem feitos nos dados para trazer o maior número possível de registros batidos."
        
         "Sessão 4 - Regras de Batimentos. "
         "Identificação e Sugestão de Regras de Batimento para Conciliação de Dados. "
         "Inicie o processo de criação de regras de batimento entre dois datasets aplicando o maior número de combinações de colunas possíveis, das mais fortes (usando várias colunas) até as mais simples (usando menos colunas), conforme as etapas detalhadas abaixo: "
         "Criação de Regras de Batimento de Múltiplas Colunas: "
         "Início pelas Regras Mais Fortes: Comece testando combinações de batimento que utilizem o maior número possível de colunas entre os datasets (não tente regras de 3 colunas x 3 colunas antes de garantir que não existem conciliações possíveis de 4 colunas x 4 colunas - isto geraria um problema de integridade). "
         "Verificação de Tipos e Formatos: Certifique-se de que cada coluna selecionada para o batimento tenha o mesmo tipo e formato nos dois datasets. Registros só batem entre si se: "
         "As colunas de datas forem do mesmo tipo e coincidirem em valor. "
         "Códigos alfanuméricos coincidirem em ambos os datasets. "
         "Valores numéricos coincidirem ou tenham correspondência em módulo (positivo/negativo), aplicável para estornos. "
         "Regras de Estorno (Sinal Oposto): "
         "Considere uma regra de estorno onde o valor numérico em um dataset é igual em módulo ao valor do outro dataset, mas com sinal oposto (ex.: R$100 no dataset A e -R$100 no dataset B). Essa regra é indicada para identificar lançamentos de ajuste, como cancelamentos ou devoluções. "
         "Configuração dos Modelos de Batimento (1x1, 1xN, Nx1 e NxN): "

         "Aplique os modelos de batimento a seguir para explorar todas as possibilidades de correspondência: "
         "1x1: Um registro de um dataset corresponde a um registro exato no outro dataset. "
         "1xN: Um registro em um dataset corresponde a vários registros consolidados (somados) no outro (ex.: uma fatura única que abrange várias transações (que somadas batem com a fatura única) ). "
         "Nx1: Vários registros consolidados (somados) em um dataset correspondem a um único no outro (ex.: várias vendas parceladas em um sistema). "
         "NxN: Múltiplos registros em ambos os datasets se correspondem (se somados). Este modelo pode incluir regras agregadas, como somas"
          "Critério de Exclusão de Regras: "

         "Se uma regra de batimento não gera ao menos um registro conciliado em cada dataset (A e B), descarte-a para garantir que apenas regras úteis sejam mantidas. "
         "Cálculo e Exibição dos Resultados: "

         "Porcentagem de Registros Conciliados: Calcule a porcentagem de registros conciliados para cada regra de batimento aplicada. Indique claramente a taxa de conciliação para os datasets A e B. "
         "Indicador Visual do Modelo de Batimento: Para cada regra, indique visualmente o modelo (1x1, 1xN, Nx1 ou NxN). "
         "Número de Registros Batidos: Mostre a quantidade de registros batidos para cada regra em cada dataset. "
         "Amostra de Registros Conciliados: Apresente uma amostra de até 5 registros do dataset A e seus correspondentes no dataset B, com os valores de cada coluna usada na regra. "
         "Exemplo de Aplicação Prática: "

         "Dado um cenário com datasets A e B e as colunas Data, Código e Valor: "

         "Regras de Batimento com Todas as Colunas: Para cada par de registros em A e B: "
         "Se Data, Código e Valor (ou valor em módulo para estornos) coincidem entre os datasets, considere uma correspondência. "
         "Exemplo de Correspondência 1x1: "
         "Dataset A: Data = 2024-10-01, Código = ABC123, Valor = 100 "
         "Dataset B: Data = 2024-10-01, Código = ABC123, Valor = -100 (sinal oposto, aplicável para estorno) "
         
         "Regra de Batimento 1xN: Teste uma regra onde Data e Código coincidam e o valor em um dataset corresponda à soma dos valores no outro dataset. "
         "Exemplo de Correspondência 1xN: "
         "Dataset A: Data = 2024-10-01, Código = ABC123, Valor = 300 "
         "Dataset B: Data = 2024-10-01, Código = ABC123, Valor = 100, Valor = 100, Valor = 100 (a soma no dataset B corresponde ao valor no dataset A) "
         "Exibição Visual da Regra Aplicada: "

         "Tipo de Batimento: 1xN"
         "Número de Registros Batidos: Dataset A: 1 registro; Dataset B: 3 registros. "
         "Amostra Visual: "
         "Dataset A: Data = 2024-10-01, Código = ABC123, Valor = 300 "
         "Dataset B: Data = 2024-10-01, Código = ABC123, Valor = 100, Valor = 100, Valor = 100"
     
         "Por favor, sugira todas as regras de batimento de dados possíveis para conciliar o maior número de registros possível entre os dois datasets. "
         #"Retorne as regras em um formato que o Python possa interpretar diretamente, como instruções de código. "
         "Retorne as regras em um formato bem amigável para leitura. As regras identificadas com mais colunas de ambos os lados, devem aparecer inicialmente."
         "Cada regra deve indicar as colunas a serem comparadas e seus tipos, número de colunas de cada lado, se houver necessidade de algum ajuste nos dados (como remoção de espaços, mudança de sinais, etc.) e o tipo de batimento (1x1, 1xN, Nx1, NxN). "
         "Para cada regra, os campos numéricos devem ser considerados correspondentes se eles tiverem valores iguais com sinais diferentes ou não. Exemplo: 100 = 100 ou 100 = -100 (neste caso deve ser informado que é uma regra com valor invertido)."
    )

    openai.api_key = api_key

    try:
        # Faz a chamada à API corretamente
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Você é um assistente de dados."},
                        {"role": "user", "content": prompt}
                    ])
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Ocorreu um erro ao chamar a API: {e}"
        
        
        

def execute_matching_rules(data_a, data_b, match_rules_code):
    match_rules_code = (
        "def clean_cpf_cnpj(column):\n"
        "    return column.astype(str).str.replace(r'\\D', '', regex=True)\n"
        + match_rules_code
    )

    # Limpeza do código recebido para manter apenas linhas de conciliação
    code_lines = match_rules_code.splitlines()
    cleaned_code_lines = [line for line in code_lines if line.strip() and ("data_a" in line or "data_b" in line or "pd." in line)]

    clean_code = "\n".join(cleaned_code_lines)
    clean_code = balance_parentheses_and_brackets(clean_code)

    # Processa as colunas de cada DataFrame
    for df in [data_a, data_b]:
        for col in df.columns:
            # Identifica colunas que podem conter CPF/CNPJ e converte se necessário
            if 'cpf' in col.lower() or 'cnpj' in col.lower() or 'doc' in col.lower():
                df[col] = clean_cpf_cnpj(df[col])
            elif pd.api.types.is_numeric_dtype(df[col]):
                # Converte valores numéricos para absolutos, quando necessário
                df[col] = df[col].abs()
            elif 'data' in col.lower() or 'date' in col.lower():
                # Converte colunas de data
                df[col] = pd.to_datetime(df[col], errors='coerce')

    # Exibe o código limpo e ajustado recebido do GPT para revisão
    st.write("Código de regras de batimento (limpo e ajustado) recebido do GPT:")
    st.code(clean_code)

    try:
        local_vars = {"data_a": data_a, "data_b": data_b}
        exec(clean_code, globals(), local_vars)
        merged_data = local_vars.get("merged_data")
        
        if merged_data is None:
            st.write("Erro ao executar as regras de batimento. Verifique as instruções fornecidas.")
            return

        # Cálculo das métricas de batimento
        total_a = len(data_a)
        total_b = len(data_b)
        matched_a = len(merged_data.drop_duplicates(subset=data_a.columns))
        matched_b = len(merged_data.drop_duplicates(subset=data_b.columns))
        percentage_a = (matched_a / total_a) * 100 if total_a > 0 else 0
        percentage_b = (matched_b / total_b) * 100 if total_b > 0 else 0

        # Exibir os resultados
        st.write("**Resultados da Conciliação**")
        st.write(f"**Arquivo 1:**")
        st.write(f"- Total de registros: {total_a}")
        st.write(f"- Total batidos com as regras: {matched_a}")
        st.write(f"- % de batimento: {percentage_a:.2f}%")
        
        st.write(f"**Arquivo 2:**")
        st.write(f"- Total de registros: {total_b}")
        st.write(f"- Total batidos com as regras: {matched_b}")
        st.write(f"- % de batimento: {percentage_b:.2f}%")

        st.write("**Amostra dos Registros Conciliados:**")
        st.write(merged_data.head(5))

    except SyntaxError as e:
        st.write("Erro de sintaxe no código recebido do GPT:", e)
    except Exception as e:
        st.write(f"Ocorreu um erro ao aplicar as regras de batimento: {e}")




# Interface do Streamlit
st.title("GuiApp - Inteligência de Conciliação")

# Entrada para chave da API do GPT
api_key = os.getenv('OPENAI_API_KEY')

# Upload dos arquivos CSV ou Excel
uploaded_file_a = st.file_uploader("Envie o arquivo do dataset A", type=["csv", "xlsx"])
uploaded_file_b = st.file_uploader("Envie o arquivo do dataset B", type=["csv", "xlsx"])

if uploaded_file_a and uploaded_file_b and api_key:
    # Carregar datasets
    data_a = pd.read_csv(uploaded_file_a) if uploaded_file_a.name.endswith('.csv') else pd.read_excel(uploaded_file_a)
    data_b = pd.read_csv(uploaded_file_b) if uploaded_file_b.name.endswith('.csv') else pd.read_excel(uploaded_file_b)

    # Exibir os datasets
    st.write("Dataset A:")
    st.dataframe(data_a)
    st.write("Dataset B:")
    st.dataframe(data_b)



    # Botão para iniciar o processamento
    if st.button("Iniciar processamento"):
        # Identificação de origem usando GPT
        st.write("Analisando as origens dos datasets...")
        origin_a = suggest_origin(data_a, "Dataset A", api_key)
        origin_b = suggest_origin(data_b, "Dataset B", api_key)

        st.write("Origem do Dataset A:")
        st.write(origin_a)
        st.write("Origem do Dataset B:")
        st.write(origin_b)
    
        st.write("Analisando os datasets e sugerindo regras de batimento via GPT...")
        match_rules_code = suggest_match_rules(data_a, data_b, api_key)
        st.write("Código sugerido pelo GPT para regras de batimento:")
        st.write(match_rules_code)

        # Executar as regras de batimento e exibir as métricas finais
        #execute_matching_rules(data_a, data_b, match_rules_code)     
