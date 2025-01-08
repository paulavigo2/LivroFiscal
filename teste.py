import streamlit as st
import re
import pandas as pd
import io

st.set_page_config(
    layout="wide",
    page_icon="🏢",
    page_title="Enterprise Fiscal Management System",
    initial_sidebar_state="expanded"
)

@st.cache_data
def processar_dados(df_pegasus, df_nbs):
    numeros_pegasus = df_pegasus['B'].astype(str).apply(lambda x: re.sub(r'[^0-9]', '', x))
    numeros_nbs = df_nbs.iloc[:, 3].astype(str).str.strip().str.rstrip('0').str.rstrip('.')

    numeros_nbs = numeros_nbs[numeros_nbs.str.strip() != 'nan']
    numeros_nbs = numeros_nbs[numeros_nbs.str.strip() != '']
    numeros_nbs = numeros_nbs.reset_index(drop=True)

    dados_exibicao = []
    for pegasus_valor in numeros_pegasus:
        if pegasus_valor in numeros_nbs.values:
            try:
                nbs_index = numeros_nbs[numeros_nbs == pegasus_valor].index[0]
                nbs_correspondente = numeros_nbs.iloc[nbs_index]
                status = "OK"
            except IndexError:
                nbs_correspondente = ""
                status = "Divergente"
        else:
            nbs_correspondente = ""
            status = "Divergente"
        dados_exibicao.append([pegasus_valor, nbs_correspondente, status])

    df_exibicao = pd.DataFrame(dados_exibicao, columns=['PEGASUS', 'NBS', 'STATUS'])
    
    return df_exibicao
cfop_variations = {
    "1102": ["5101", "5102"],
    "1556": ["5101", "5102", "5117"],
    "1551": ["5101", "5102", "5117"],
    "1403": ["5401", "5403", "5405"],
    "2152": ["6152"],
    "1152": ["5152"],
    "1653": ["5929", "5656", "5101", "5102"],
    "2653": ["6929", "6656", "6101", "6102"],
    "2102": ["6101", "6102"],
    "2556": ["6101", "6102"],
    "2551": ["6101", "6102"],
    "1407": ["5404", "5403", "5405", "5117"],
    "2407": ["6401", "6403", "6404"],
    "1353": ["5353"],
    "2353": ["6353"],
    "1253": ["5253"],
    "1406": ["5401", "5403", "5405", "5117"],
    "2406": ["6401", "6403", "6404"],
    "1922": ["5922"],
    "2922": ["6922"],
    "1912": ["5912"],
    "2912": ["6912"],
    "1913": ["5913"],
    "2913": ["6913"],
    "1914": ["5914"],
    "2914": ["6914"],
    "1916": ["5916"],
    "2916": ["6916"],
    "1949": ["5949", "1949"],
    "2949": ["6949", "2949"],
    "1923": ["5923"],
    "2923": ["6923"],
    "1910": ["5910"],
    "2910": ["6910"],
    "1908": ["5908"],
    "2908": ["6908"],
    "1202": ["5202", "1202"],
    "2202": ["6202", "2202"],
    "1411": ["5411", "5113", "1411"],
    "2411": ["6411", "2411"],
    "1661": ["5661", "5662", "1661"],
    "2661": ["6661", "6662", "2661"],
    "1409": ["5409"],
    "2409": ["6409"],
    "1152": ["5152"],
    "2152": ["6152"],
    "1659": ["5659"],
    "2659": ["6659"],
    "1552": ["5552"],
    "2552": ["6552"],
    "1602": ["5602"],
    "1605": ["5605"],
    "2403": ["6401", "6403", "6404", "6405"],
    "1652": ["5652", "5655"],
    "2652": ["6652", "6655"],
    "1303": ["5303"],
    "2303": ["6303"],
    "1933": ["5933"],
    "2933": ["5933", "6933"]
}

@st.cache_data
def processar_cfop(df_pegasus, df_nbs, cfop_variations, conciliador_numeros):
    if df_nbs.shape[1] < 9 or df_pegasus.shape[1] < 10:
        raise ValueError("Os arquivos não possuem a quantidade mínima de colunas.")

    cfop_nbs = df_nbs.iloc[:, 8].astype(str).str.extract('(\d+)', expand=False).dropna().reset_index(drop=True)
    cfop_pegasus = df_pegasus.iloc[1:, 9].astype(str).str.extract('(\d+)', expand=False).dropna().reset_index(drop=True)

    dados_exibicao = []
    for idx, nbs_valor in enumerate(cfop_nbs):
        correspondente = None
        pegasus_valor = cfop_pegasus.iloc[idx] if idx < len(cfop_pegasus) else ""
        variacoes_conciliadas = []
        if nbs_valor == pegasus_valor or pegasus_valor in cfop_variations.get(nbs_valor, []):
            correspondente = nbs_valor
            variacoes_conciliadas.append(pegasus_valor)
        status = "OK" if correspondente else "Divergente"
        numero_conciliador = (
            conciliador_numeros.iloc[idx, 0]
            if idx < len(conciliador_numeros)
            else ""
        )
        dados_exibicao.append([numero_conciliador, pegasus_valor, nbs_valor, ', '.join(variacoes_conciliadas) if variacoes_conciliadas else "", status])

    df_exibicao = pd.DataFrame(dados_exibicao, columns=['NÚMERO', 'PEGASUS', 'NBS', 'CORRESPONDENTE', 'STATUS'])

    return df_exibicao
@st.cache_data
def processar_serie(df_pegasus, df_nbs, conciliador_numeros):
    series_pegasus = df_pegasus['C'].astype(str).apply(lambda x: x.split('.')[0].strip())
    series_nbs = df_nbs.iloc[:, 2].astype(str).str.strip()

    series_nbs = series_nbs[series_nbs.str.strip() != 'nan']
    series_nbs = series_nbs[series_nbs.str.strip() != '']
    series_nbs = series_nbs.reset_index(drop=True)

    dados_exibicao = []
    for idx, pegasus_valor in enumerate(series_pegasus):
        numero_conciliador = (
            conciliador_numeros.iloc[idx, 0]
            if idx < len(conciliador_numeros)
            else ""
        )
        if pegasus_valor in series_nbs.values:
            try:
                nbs_index = series_nbs[series_nbs == pegasus_valor].index[0]
                nbs_correspondente = series_nbs.iloc[nbs_index]
                status = "OK"
            except IndexError:
                nbs_correspondente = ""
                status = "Divergente"
        else:
            nbs_correspondente = ""
            status = "Divergente"
        dados_exibicao.append([numero_conciliador, pegasus_valor, nbs_correspondente, status])

    df_exibicao = pd.DataFrame(dados_exibicao, columns=['NÚMERO', 'PEGASUS', 'NBS', 'STATUS'])
    
    return df_exibicao

@st.cache_data
def processar_cnpj(df_pegasus, df_nbs, conciliador_numeros):
    cnpjs_pegasus = df_pegasus['E'].astype(str).apply(lambda x: re.sub(r'[^0-9]', '', x))
    cnpjs_nbs = df_nbs.iloc[:, 5].astype(str).apply(lambda x: re.sub(r'[^0-9]', '', x))

    cnpjs_nbs = cnpjs_nbs[cnpjs_nbs.str.strip() != 'nan']
    cnpjs_nbs = cnpjs_nbs[cnpjs_nbs.str.strip() != '']
    cnpjs_nbs = cnpjs_nbs.reset_index(drop=True)

    dados_exibicao = []
    for idx, pegasus_valor in enumerate(cnpjs_pegasus):
        numero_conciliador = (
            conciliador_numeros.iloc[idx, 0]
            if idx < len(conciliador_numeros)
            else ""
        )
        if pegasus_valor in cnpjs_nbs.values:
            try:
                nbs_index = cnpjs_nbs[cnpjs_nbs == pegasus_valor].index[0]
                nbs_correspondente = cnpjs_nbs.iloc[nbs_index]
                status = "OK"
            except IndexError:
                nbs_correspondente = ""
                status = "Divergente"
        else:
            nbs_correspondente = ""
            status = "Divergente"
        dados_exibicao.append([numero_conciliador, pegasus_valor, nbs_correspondente, status])

    df_exibicao = pd.DataFrame(dados_exibicao, columns=['NÚMERO', 'CNPJ EMITENTE (PEGASUS)', 'CNPJ EMITENTE (NBS)', 'STATUS'])
    
    return df_exibicao
@st.cache_data
def processar_data_emissao(df_pegasus, df_nbs, conciliador_numeros):
    datas_pegasus = df_pegasus['G'].astype(str).str.strip()
    datas_nbs = df_nbs.iloc[:, 4].astype(str).str.strip()

    datas_nbs = datas_nbs[datas_nbs.str.strip() != 'nan']
    datas_nbs = datas_nbs[datas_nbs.str.strip() != '']
    datas_nbs = datas_nbs.reset_index(drop=True)

    dados_exibicao = []
    for idx, pegasus_valor in enumerate(datas_pegasus):
        numero_conciliador = (
            conciliador_numeros.iloc[idx, 0]
            if idx < len(conciliador_numeros)
            else ""
        )
        if pegasus_valor in datas_nbs.values:
            try:
                nbs_index = datas_nbs[datas_nbs == pegasus_valor].index[0]
                nbs_correspondente = datas_nbs.iloc[nbs_index]
                status = "OK"
            except IndexError:
                nbs_correspondente = ""
                status = "Divergente"
        else:
            nbs_correspondente = ""
            status = "Divergente"
        dados_exibicao.append([numero_conciliador, pegasus_valor, nbs_correspondente, status])

    df_exibicao = pd.DataFrame(dados_exibicao, columns=['NÚMERO', 'DATA EMISSÃO (PEGASUS)', 'DATA EMISSÃO (NBS)', 'STATUS'])
    
    return df_exibicao

@st.cache_data
def processar_data_recepcao(df_pegasus, df_nbs, conciliador_numeros):
    datas_recepcao_pegasus = df_pegasus['H'].astype(str).str.strip()
    datas_recepcao_nbs = df_nbs.iloc[:, 0].astype(str).str.strip()

    datas_recepcao_nbs = datas_recepcao_nbs[datas_recepcao_nbs.str.strip() != 'nan']
    datas_recepcao_nbs = datas_recepcao_nbs[datas_recepcao_nbs.str.strip() != '']
    datas_recepcao_nbs = datas_recepcao_nbs.reset_index(drop=True)

    dados_exibicao = []
    for idx, pegasus_valor in enumerate(datas_recepcao_pegasus):
        numero_conciliador = (
            conciliador_numeros.iloc[idx, 0]
            if idx < len(conciliador_numeros)
            else ""
        )
        if pegasus_valor in datas_recepcao_nbs.values:
            try:
                nbs_index = datas_recepcao_nbs[datas_recepcao_nbs == pegasus_valor].index[0]
                nbs_correspondente = datas_recepcao_nbs.iloc[nbs_index]
                status = "OK"
            except IndexError:
                nbs_correspondente = ""
                status = "Divergente"
        else:
            nbs_correspondente = ""
            status = "Divergente"
        dados_exibicao.append([numero_conciliador, pegasus_valor, nbs_correspondente, status])

    df_exibicao = pd.DataFrame(dados_exibicao, columns=['NÚMERO', 'DATA RECEPÇÃO (PEGASUS)', 'DATA RECEPÇÃO (NBS)', 'STATUS'])
    
    return df_exibicao
@st.cache_data
def processar_valores_monetarios(df_pegasus, df_nbs, conciliador_numeros):
    def ajustar_valor(valor):
        if '.' in valor and len(valor.split('.')[1]) == 1:
            valor += '0'
        return valor

    valores_pegasus = df_pegasus['I'].astype(str).apply(ajustar_valor)
    valores_nbs = df_nbs.iloc[:, 7].astype(str)

    valores_nbs = valores_nbs[valores_nbs != 'nan']
    valores_nbs = valores_nbs[valores_nbs != '']
    valores_nbs = valores_nbs.reset_index(drop=True)

    valores_pegasus_normalizados = valores_pegasus.apply(lambda x: x.replace('.', '').replace(',', '')).tolist()
    valores_nbs_normalizados = valores_nbs.apply(lambda x: x.replace('.', '').replace(',', '')).tolist()

    dados_exibicao = []
    valores_nbs_usados = set()

    for idx, pegasus_valor in enumerate(valores_pegasus):
        pegasus_valor_norm = valores_pegasus_normalizados[idx]
        numero_conciliador = conciliador_numeros.iloc[idx, 0] if idx < len(conciliador_numeros) else ""
        nbs_correspondente = ""
        status = "Divergente"

        for jdx, nbs_valor_norm in enumerate(valores_nbs_normalizados):
            if pegasus_valor_norm == nbs_valor_norm and jdx not in valores_nbs_usados:
                nbs_correspondente = valores_nbs[jdx]
                status = "OK"
                valores_nbs_usados.add(jdx)
                break

        dados_exibicao.append([numero_conciliador, pegasus_valor, nbs_correspondente, status])

    for jdx, nbs_valor in enumerate(valores_nbs):
        if jdx not in valores_nbs_usados:
            dados_exibicao.append(["", "", nbs_valor, "Divergente"])

    df_exibicao = pd.DataFrame(dados_exibicao, columns=['NÚMERO', 'VALOR MONETÁRIO (PEGASUS)', 'VALOR MONETÁRIO (NBS)', 'STATUS'])

    return df_exibicao

@st.cache_data
def processar_vr_produto(df_pegasus, df_nbs, conciliador_numeros):
    def ajustar_valor(valor):
        if '.' in valor and len(valor.split('.')[1]) == 1:
            valor += '0'
        return valor

    def arredondar_valor(valor):
        try:
            return "{:.2f}".format(float(valor))
        except ValueError:
            return valor

    valores_produto_pegasus = df_pegasus['K'].astype(str).apply(ajustar_valor).apply(arredondar_valor)
    valores_produto_nbs = df_nbs.iloc[:, 10].astype(str)

    valores_produto_nbs = valores_produto_nbs[valores_produto_nbs != 'nan']
    valores_produto_nbs = valores_produto_nbs[valores_produto_nbs != '']
    valores_produto_nbs = valores_produto_nbs.reset_index(drop=True)

    valores_produto_pegasus_normalizados = valores_produto_pegasus.apply(lambda x: x.replace('.', '').replace(',', '')).tolist()
    valores_produto_nbs_normalizados = valores_produto_nbs.apply(lambda x: x.replace('.', '').replace(',', '')).tolist()

    dados_exibicao = []
    valores_produto_nbs_usados = set()

    for idx, pegasus_valor in enumerate(valores_produto_pegasus):
        pegasus_valor_norm = valores_produto_pegasus_normalizados[idx]
        numero_conciliador = conciliador_numeros.iloc[idx, 0] if idx < len(conciliador_numeros) else ""
        nbs_correspondente = ""
        status = "Divergente"

        for jdx, nbs_valor_norm in enumerate(valores_produto_nbs_normalizados):
            if pegasus_valor_norm == nbs_valor_norm and jdx not in valores_produto_nbs_usados:
                nbs_correspondente = valores_produto_nbs[jdx]
                status = "OK"
                valores_produto_nbs_usados.add(jdx)
                break

        dados_exibicao.append([numero_conciliador, pegasus_valor, nbs_correspondente, status])

    for jdx, nbs_valor in enumerate(valores_produto_nbs):
        if jdx not in valores_produto_nbs_usados:
            dados_exibicao.append(["", "", nbs_valor, "Divergente"])

    df_exibicao = pd.DataFrame(dados_exibicao, columns=['NÚMERO', 'VR PRODUTO (PEGASUS)', 'VR PRODUTO (NBS)', 'STATUS'])

    return df_exibicao
@st.cache_data
def processar_imposto(df_pegasus, df_nbs, conciliador_numeros):
    def arredondar_valor(valor):
        try:
            valor = valor.replace(',', '.')
            valor_float = float(valor)
            return "{:.2f}".format(valor_float)
        except ValueError:
            return valor

    impostos_pegasus = df_pegasus['M'].astype(str).replace('nan', '0').replace('', '0').apply(arredondar_valor)
    impostos_nbs = df_nbs.iloc[:, 12].astype(str).replace('nan', '0').replace('', '0').apply(arredondar_valor)

    impostos_nbs = impostos_nbs.reset_index(drop=True)

    dados_exibicao = []
    impostos_nbs_usados = set()

    for idx, pegasus_valor in enumerate(impostos_pegasus):
        numero_conciliador = conciliador_numeros.iloc[idx, 0] if idx < len(conciliador_numeros) else ""
        nbs_correspondente = ""
        status = "Divergente"

        if pegasus_valor and pegasus_valor != '0.00':
            for jdx, nbs_valor in enumerate(impostos_nbs):
                if pegasus_valor == nbs_valor and pegasus_valor != '0' and jdx not in impostos_nbs_usados:
                    nbs_correspondente = nbs_valor
                    status = "OK"
                    impostos_nbs_usados.add(jdx)
                    break

        dados_exibicao.append([numero_conciliador, pegasus_valor, nbs_correspondente, status])

    for jdx, nbs_valor in enumerate(impostos_nbs):
        if jdx not in impostos_nbs_usados and nbs_valor != '0.00':
            dados_exibicao.append(["", "", nbs_valor, "Divergente"])

    df_exibicao = pd.DataFrame(dados_exibicao, columns=['NÚMERO', 'IMPOSTO (PEGASUS)', 'IMPOSTO (NBS)', 'STATUS'])

    return df_exibicao

@st.cache_data
def processar_vripi(df_pegasus, df_nbs, conciliador_numeros):
    def extrair_valor_vripi(text):
        match = re.search(r'VRIPI=([\d,]+)', text)
        if match:
            return match.group(1).replace(',', '.')
        return '0.00'

    def arredondar_valor(valor):
        try:
            return "{:.2f}".format(float(valor))
        except ValueError:
            return valor

    vripi_pegasus = df_pegasus['P'].astype(str).replace('nan', '0').replace('', '0').apply(arredondar_valor)
    vripi_nbs = df_nbs.iloc[:, 11].astype(str).apply(extrair_valor_vripi).apply(arredondar_valor)

    vripi_nbs = vripi_nbs.reset_index(drop=True)

    dados_exibicao = []
    vripi_nbs_usados = set()

    for idx, pegasus_valor in enumerate(vripi_pegasus):
        numero_conciliador = conciliador_numeros.iloc[idx, 0] if idx < len(conciliador_numeros) else ""
        nbs_correspondente = ""
        status = "Divergente"

        if pegasus_valor and pegasus_valor != '0.00':
            for jdx, nbs_valor in enumerate(vripi_nbs):
                if pegasus_valor == nbs_valor and jdx not in vripi_nbs_usados:
                    nbs_correspondente = nbs_valor
                    status = "OK"
                    vripi_nbs_usados.add(jdx)
                    break

        dados_exibicao.append([numero_conciliador, pegasus_valor, nbs_correspondente, status])

    for jdx, nbs_valor in enumerate(vripi_nbs):
        if jdx not in vripi_nbs_usados and nbs_valor != '0.00':
            dados_exibicao.append(["", "", nbs_valor, "Divergente"])

    df_exibicao = pd.DataFrame(dados_exibicao, columns=['NÚMERO', 'VRIPI (PEGASUS)', 'VRIPI (NBS)', 'STATUS'])

    return df_exibicao
@st.cache_data
def processar_bcst(df_pegasus, df_nbs, conciliador_numeros):
    def extrair_valor_bcst(text):
        matches = re.findall(r'BCST=(\d+(?:,\d{1,2})?)', text)
        valores = [match.replace(',', '.') for match in matches]
        return valores if valores else []

    def formatar_valor(valor):
        try:
            valor_float = float(valor)
            return "{:.2f}".format(valor_float).rstrip('0').rstrip('.')
        except ValueError:
            return valor

    bcst_pegasus = df_pegasus['N'].astype(str).replace('nan', '0').replace('', '0').apply(formatar_valor)

    bcst_nbs = []
    for index, row in df_nbs.iterrows():
        valores_l = extrair_valor_bcst(str(row.iloc[11]))
        valores_o = extrair_valor_bcst(str(row.iloc[14]))

        bcst_nbs.extend(valores_l)
        bcst_nbs.extend(valores_o)

    bcst_nbs = pd.Series(bcst_nbs)

    dados_exibicao = []
    bcst_nbs_usados = set()

    for idx, pegasus_valor in enumerate(bcst_pegasus):
        numero_conciliador = conciliador_numeros.iloc[idx, 0] if idx < len(conciliador_numeros) else ""
        nbs_correspondente = ""
        status = "Divergente"

        if pegasus_valor and pegasus_valor != '0.00':
            for jdx, nbs_valor in enumerate(bcst_nbs):
                if pegasus_valor == nbs_valor and pegasus_valor != '0' and jdx not in bcst_nbs_usados:
                    nbs_correspondente = nbs_valor
                    status = "OK"
                    bcst_nbs_usados.add(jdx)
                    break

        dados_exibicao.append([numero_conciliador, pegasus_valor, nbs_correspondente, status])

    for jdx, nbs_valor in enumerate(bcst_nbs):
        if jdx not in bcst_nbs_usados and nbs_valor != '0.00' and nbs_valor != '0':
            dados_exibicao.append(["", "", nbs_valor, "Divergente"])

    df_exibicao = pd.DataFrame(dados_exibicao, columns=['NÚMERO', 'BCST (PEGASUS)', 'BCST (NBS)', 'STATUS'])

    return df_exibicao

@st.cache_data
def processar_vrst(df_pegasus, df_nbs, conciliador_numeros):
    def extrair_valor_vrst(text):
        matches = re.findall(r'VRST=(\d+(?:,\d{1,2})?)', text)
        valores = [match.replace(',', '.') for match in matches]
        return valores if valores else []

    def formatar_valor(valor):
        try:
            valor_float = float(valor)
            return "{:.2f}".format(valor_float).rstrip('0').rstrip('.')
        except ValueError:
            return valor

    vrst_pegasus = df_pegasus['O'].astype(str).replace('nan', '0').replace('', '0').apply(formatar_valor)

    vrst_nbs = []
    for index, row in df_nbs.iterrows():
        valores_o = extrair_valor_vrst(str(row.iloc[14]))

        vrst_nbs.extend(valores_o)

    vrst_nbs = pd.Series(vrst_nbs)

    dados_exibicao = []
    vrst_nbs_usados = set()

    for idx, pegasus_valor in enumerate(vrst_pegasus):
        numero_conciliador = conciliador_numeros.iloc[idx, 0] if idx < len(conciliador_numeros) else ""
        nbs_correspondente = ""
        status = "Divergente"

        if pegasus_valor and pegasus_valor != '0.00':
            for jdx, nbs_valor in enumerate(vrst_nbs):
                if pegasus_valor == nbs_valor and pegasus_valor != '0' and jdx not in vrst_nbs_usados:
                    nbs_correspondente = nbs_valor
                    status = "OK"
                    vrst_nbs_usados.add(jdx)
                    break

        dados_exibicao.append([numero_conciliador, pegasus_valor, nbs_correspondente, status])

    for jdx, nbs_valor in enumerate(vrst_nbs):
        if jdx not in vrst_nbs_usados and nbs_valor != '0.00' and nbs_valor != '0':
            dados_exibicao.append(["", "", nbs_valor, "Divergente"])

    df_exibicao = pd.DataFrame(dados_exibicao, columns=['NÚMERO', 'VRST (PEGASUS)', 'VRST (NBS)', 'STATUS'])

    return df_exibicao
def highlight_status(val):
    color = 'white'
    if val == 'OK':
        color = 'green'
    elif val == 'Divergente':
        color = 'red'
    return f'background-color: {color}; color: white;'

def aplicar_filtros(df, status_selecionado):
    if status_selecionado:
        df = df[df['STATUS'].isin(status_selecionado)]
    return df

def exibir_estatisticas(total_conciliados, total_divergentes):
    st.markdown(
        f"""
        <div class="dashboard-grid" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
            <div class="metric-card" style="font-size: 0.8rem; padding: 0.5rem;">
                <h3 style="font-size: 1rem; margin: 0;">Total Conciliados</h3>
                <p style="font-size: 0.9rem; margin: 0;">{total_conciliados}</p>
            </div>
            <div class="metric-card" style="font-size: 0.8rem; padding: 0.5rem;">
                <h3 style="font-size: 1rem; margin: 0;">Total Divergentes</h3>
                <p style="font-size: 0.9rem; margin: 0;">{total_divergentes}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Sidebar aprimorado
with st.sidebar:
    st.image("https://via.placeholder.com/200x80?text=Enterprise", use_container_width=True)

    with st.expander("🔍 Filtros Avançados", expanded=True):
        status_selecionado = st.multiselect("Status", ["OK", "Divergente"])

    with st.expander("⚙️ Configurações", expanded=True):
        modo_detalhado = st.checkbox("Modo Detalhado", value=True)
        exibir_graficos = st.checkbox("Exibir Gráficos", value=True)
        formato_exportacao = st.selectbox("Formato de Exportação", ["Excel", "PDF", "CSV"])

st.markdown(
    """
    <div class="enterprise-header">
        <h1 class="enterprise-title">🏢 Enterprise Fiscal Management System</h1>
    </div>
    """,
    unsafe_allow_html=True
)
# Inicialize os estados da sessão no início do script
# Inicialize os estados da sessão no início do script
if "show_numero" not in st.session_state:
    st.session_state.show_numero = False

if "show_cfop" not in st.session_state:
    st.session_state.show_cfop = False

if "show_serie" not in st.session_state:
    st.session_state.show_serie = False

if "show_cnpj" not in st.session_state:
    st.session_state.show_cnpj = False

if "show_data_emissao" not in st.session_state:
    st.session_state.show_data_emissao = False

if "show_data_recepcao" not in st.session_state:
    st.session_state.show_data_recepcao = False

if "show_valores_monetarios" not in st.session_state:
    st.session_state.show_valores_monetarios = False

if "show_vr_produto" not in st.session_state:
    st.session_state.show_vr_produto = False

if "show_imposto" not in st.session_state:
    st.session_state.show_imposto = False

if "show_vripi" not in st.session_state:
    st.session_state.show_vripi = False

if "show_bcst" not in st.session_state:
    st.session_state.show_bcst = False

if "show_vrst" not in st.session_state:
    st.session_state.show_vrst = False

with st.container():
    st.markdown("<div class='main'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file_pegasus = st.file_uploader("Escolha o arquivo PEGASUS (xlsx)", type="xlsx", key="file_uploader_pegasus")
    with col2:
        uploaded_file_nbs = st.file_uploader("Escolha o arquivo NBS (xlsx)", type="xlsx", key="file_uploader_nbs")

    if uploaded_file_pegasus and uploaded_file_nbs:
        try:
            df_pegasus = pd.read_excel(uploaded_file_pegasus)
            df_nbs = pd.read_excel(uploaded_file_nbs)
            df_pegasus_b = pd.read_excel(uploaded_file_pegasus, skiprows=2, header=None, usecols="B")
            df_pegasus_b.columns = ['B']
            df_pegasus_c = pd.read_excel(uploaded_file_pegasus, skiprows=2, header=None, usecols="C")
            df_pegasus_c.columns = ['C']
            df_pegasus_e = pd.read_excel(uploaded_file_pegasus, skiprows=2, header=None, usecols="E")
            df_pegasus_e.columns = ['E']
            df_pegasus_g = pd.read_excel(uploaded_file_pegasus, skiprows=2, header=None, usecols="G")
            df_pegasus_g.columns = ['G']
            df_pegasus_h = pd.read_excel(uploaded_file_pegasus, skiprows=2, header=None, usecols="H")
            df_pegasus_h.columns = ['H']
            df_pegasus_i = pd.read_excel(uploaded_file_pegasus, skiprows=2, header=None, usecols="I")
            df_pegasus_i.columns = ['I']
            df_pegasus_k = pd.read_excel(uploaded_file_pegasus, skiprows=2, header=None, usecols="K")
            df_pegasus_k.columns = ['K']
            df_pegasus_m = pd.read_excel(uploaded_file_pegasus, skiprows=2, header=None, usecols="M")
            df_pegasus_m.columns = ['M']
            df_pegasus_n = pd.read_excel(uploaded_file_pegasus, skiprows=2, header=None, usecols="N")
            df_pegasus_n.columns = ['N']
            df_pegasus_o = pd.read_excel(uploaded_file_pegasus, skiprows=2, header=None, usecols="O")
            df_pegasus_o.columns = ['O']
            df_pegasus_p = pd.read_excel(uploaded_file_pegasus, skiprows=2, header=None, usecols="P")
            df_pegasus_p.columns = ['P']

            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)
            col5, col6 = st.columns(2)
            col7, col8 = st.columns(2)
            col9, col10 = st.columns(2)
            col11, col12 = st.columns(2)

            with col1:
                if st.button("Número", key="numero_button", use_container_width=True, help="Clique para ver número"):
                    st.session_state.show_numero = True

            with col2:
                if st.button("CFOP", key="cfop_button", use_container_width=True, help="Clique para ver CFOP"):
                    st.session_state.show_cfop = True

            with col3:
                if st.button("Série", key="serie_button", use_container_width=True, help="Clique para ver série"):
                    st.session_state.show_serie = True

            with col4:
                if st.button("CNPJ EMITENTE", key="cnpj_button", use_container_width=True, help="Clique para ver CNPJ"):
                    st.session_state.show_cnpj = True

            with col5:
                if st.button("Data de Emissão", key="data_emissao_button", use_container_width=True, help="Clique para ver data de emissão"):
                    st.session_state.show_data_emissao = True

            with col6:
                if st.button("Data de Recepção", key="data_recepcao_button", use_container_width=True, help="Clique para ver data de recepção"):
                    st.session_state.show_data_recepcao = True

            with col7:
                if st.button("Total NFE", key="valores_monetarios_button", use_container_width=True, help="Clique para ver valores monetários"):
                    st.session_state.show_valores_monetarios = True

            with col8:
                if st.button("VR PRODUTO", key="vr_produto_button", use_container_width=True, help="Clique para ver VR produto"):
                    st.session_state.show_vr_produto = True

            with col9:
                if st.button("IMPOSTO", key="imposto_button", use_container_width=True, help="Clique para ver imposto"):
                    st.session_state.show_imposto = True

            with col10:
                if st.button("VRIPI", key="vripi_button", use_container_width=True, help="Clique para ver VRIPI"):
                    st.session_state.show_vripi = True

            with col11:
                if st.button("BCST", key="bcst_button", use_container_width=True, help="Clique para ver BCST"):
                    st.session_state.show_bcst = True

            with col12:
                if st.button("VRST", key="vrst_button", use_container_width=True, help="Clique para ver VRST"):
                    st.session_state.show_vrst = True

            result_col1, result_col2 = st.columns(2)
            result_col3, result_col4 = st.columns(2)
            result_col5, result_col6 = st.columns(2)
            result_col7, result_col8 = st.columns(2)
            result_col9, result_col10 = st.columns(2)
            result_col11, result_col12 = st.columns(2)

        except ValueError as ve:
            st.error(f"Erro ao processar os arquivos: {ve}. Verifique se os arquivos estão no formato .xlsx e se as planilhas estão corretas.")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}. Contate o suporte.")

    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.show_numero:
    if df_pegasus_b.shape[1] == 1 and df_nbs.shape[1] >= 4:
        df_exibicao = processar_dados(df_pegasus_b, df_nbs)

        # Aplicando filtro de status
        df_exibicao = aplicar_filtros(df_exibicao, status_selecionado)

        with result_col1:
            st.subheader("Conciliação Número")

            status_counts = df_exibicao['STATUS'].value_counts()
            total_conciliados = status_counts.get('OK', 0)
            total_divergentes = status_counts.get('Divergente', 0)

            exibir_estatisticas(total_conciliados, total_divergentes)
            df_exibicao.insert(0, 'NÚMERO', range(1, len(df_exibicao) + 1))
            st.dataframe(df_exibicao.style.applymap(highlight_status, subset=['STATUS']), key="todos")

            opcao_exportar_excel = st.checkbox("Exportar para Excel", key="exportar_excel")
            if opcao_exportar_excel and not df_exibicao.empty:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_exibicao.to_excel(writer, sheet_name='Conciliação', index=False)
                st.download_button(
                    label="Download Excel",
                    data=buffer,
                    file_name='conciliacao_fiscal.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
    else:
        st.error(f"O arquivo PEGASUS deve ter apenas a coluna B e o NBS deve ter pelo menos 4 colunas. (PEGASUS: {df_pegasus_b.shape[1]} colunas, NBS: {df_nbs.shape[1]} colunas).")

if st.session_state.show_cfop:
    df_exibicao_cfop = processar_cfop(df_pegasus, df_nbs, cfop_variations, df_pegasus_b)

    # Aplicando filtro de status
    df_exibicao_cfop = aplicar_filtros(df_exibicao_cfop, status_selecionado)

    with result_col2:
        st.subheader("Conciliação CFOP")

        status_counts = df_exibicao_cfop['STATUS'].value_counts()
        total_conciliados = status_counts.get('OK', 0)
        total_divergentes = status_counts.get('Divergente', 0)

        exibir_estatisticas(total_conciliados, total_divergentes)
        st.dataframe(df_exibicao_cfop.style.applymap(highlight_status, subset=['STATUS']), key="cfop")

        opcao_exportar_excel_cfop = st.checkbox("Exportar para Excel", key="exportar_excel_cfop")
        if opcao_exportar_excel_cfop and not df_exibicao_cfop.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_exibicao_cfop.to_excel(writer, sheet_name='Conciliação_CFOP', index=False)
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name='conciliacao_fiscal_cfop.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

if st.session_state.show_serie:
    df_exibicao_serie = processar_serie(df_pegasus_c, df_nbs, df_pegasus_b)

    # Aplicando filtro de status
    df_exibicao_serie = aplicar_filtros(df_exibicao_serie, status_selecionado)

    with result_col3:
        st.subheader("Conciliação Série")

        status_counts = df_exibicao_serie['STATUS'].value_counts()
        total_conciliados = status_counts.get('OK', 0)
        total_divergentes = status_counts.get('Divergente', 0)

        exibir_estatisticas(total_conciliados, total_divergentes)
        st.dataframe(df_exibicao_serie.style.applymap(highlight_status, subset=['STATUS']), key="serie")

        opcao_exportar_excel_serie = st.checkbox("Exportar para Excel", key="exportar_excel_serie")
        if opcao_exportar_excel_serie and not df_exibicao_serie.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_exibicao_serie.to_excel(writer, sheet_name='Conciliação_Série', index=False)
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name='conciliacao_fiscal_serie.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

if st.session_state.show_cnpj:
    df_exibicao_cnpj = processar_cnpj(df_pegasus_e, df_nbs, df_pegasus_b)

    # Aplicando filtro de status
    df_exibicao_cnpj = aplicar_filtros(df_exibicao_cnpj, status_selecionado)

    with result_col4:
        st.subheader("Conciliação CNPJ EMITENTE")

        status_counts = df_exibicao_cnpj['STATUS'].value_counts()
        total_conciliados = status_counts.get('OK', 0)
        total_divergentes = status_counts.get('Divergente', 0)

        exibir_estatisticas(total_conciliados, total_divergentes)
        st.dataframe(df_exibicao_cnpj.style.applymap(highlight_status, subset=['STATUS']), key="cnpj")

        opcao_exportar_excel_cnpj = st.checkbox("Exportar para Excel", key="exportar_excel_cnpj")
        if opcao_exportar_excel_cnpj and not df_exibicao_cnpj.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_exibicao_cnpj.to_excel(writer, sheet_name='Conciliação_CNPJ', index=False)
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name='conciliacao_fiscal_cnpj.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
if st.session_state.show_data_emissao:
    df_exibicao_data_emissao = processar_data_emissao(df_pegasus_g, df_nbs, df_pegasus_b)

    # Aplicando filtro de status
    df_exibicao_data_emissao = aplicar_filtros(df_exibicao_data_emissao, status_selecionado)

    with result_col5:
        st.subheader("Conciliação Data de Emissão")

        status_counts = df_exibicao_data_emissao['STATUS'].value_counts()
        total_conciliados = status_counts.get('OK', 0)
        total_divergentes = status_counts.get('Divergente', 0)

        exibir_estatisticas(total_conciliados, total_divergentes)
        st.dataframe(df_exibicao_data_emissao.style.applymap(highlight_status, subset=['STATUS']), key="data_emissao")

        opcao_exportar_excel_data_emissao = st.checkbox("Exportar para Excel", key="exportar_excel_data_emissao")
        if opcao_exportar_excel_data_emissao and not df_exibicao_data_emissao.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_exibicao_data_emissao.to_excel(writer, sheet_name='Conciliação_Data_Emissão', index=False)
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name='conciliacao_fiscal_data_emissao.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

if st.session_state.show_data_recepcao:
    df_exibicao_data_recepcao = processar_data_recepcao(df_pegasus_h, df_nbs, df_pegasus_b)

    # Aplicando filtro de status
    df_exibicao_data_recepcao = aplicar_filtros(df_exibicao_data_recepcao, status_selecionado)

    with result_col6:
        st.subheader("Conciliação Data de Recepção")

        status_counts = df_exibicao_data_recepcao['STATUS'].value_counts()
        total_conciliados = status_counts.get('OK', 0)
        total_divergentes = status_counts.get('Divergente', 0)

        exibir_estatisticas(total_conciliados, total_divergentes)
        st.dataframe(df_exibicao_data_recepcao.style.applymap(highlight_status, subset=['STATUS']), key="data_recepcao")

        opcao_exportar_excel_data_recepcao = st.checkbox("Exportar para Excel", key="exportar_excel_data_recepcao")
        if opcao_exportar_excel_data_recepcao and not df_exibicao_data_recepcao.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_exibicao_data_recepcao.to_excel(writer, sheet_name='Conciliação_Data_Recepção', index=False)
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name='conciliacao_fiscal_data_recepcao.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
if st.session_state.show_valores_monetarios:
    df_exibicao_valores_monetarios = processar_valores_monetarios(df_pegasus_i, df_nbs, df_pegasus_b)

    # Aplicando filtro de status
    df_exibicao_valores_monetarios = aplicar_filtros(df_exibicao_valores_monetarios, status_selecionado)

    with result_col7:
        st.subheader("Conciliação Valores Monetários")

        status_counts = df_exibicao_valores_monetarios['STATUS'].value_counts()
        total_conciliados = status_counts.get('OK', 0)
        total_divergentes = status_counts.get('Divergente', 0)

        exibir_estatisticas(total_conciliados, total_divergentes)
        st.dataframe(df_exibicao_valores_monetarios.style.applymap(highlight_status, subset=['STATUS']), key="valores_monetarios")

        opcao_exportar_excel_valores_monetarios = st.checkbox("Exportar para Excel", key="exportar_excel_valores_monetarios")
        if opcao_exportar_excel_valores_monetarios and not df_exibicao_valores_monetarios.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_exibicao_valores_monetarios.to_excel(writer, sheet_name='Conciliação_Valores_Monetários', index=False)
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name='conciliacao_fiscal_valores_monetarios.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

if st.session_state.show_vr_produto:
    df_exibicao_vr_produto = processar_vr_produto(df_pegasus_k, df_nbs, df_pegasus_b)

    # Aplicando filtro de status
    df_exibicao_vr_produto = aplicar_filtros(df_exibicao_vr_produto, status_selecionado)

    with result_col8:
        st.subheader("Conciliação VR PRODUTO")

        status_counts = df_exibicao_vr_produto['STATUS'].value_counts()
        total_conciliados = status_counts.get('OK', 0)
        total_divergentes = status_counts.get('Divergente', 0)

        exibir_estatisticas(total_conciliados, total_divergentes)
        st.dataframe(df_exibicao_vr_produto.style.applymap(highlight_status, subset=['STATUS']), key="vr_produto")

        opcao_exportar_excel_vr_produto = st.checkbox("Exportar para Excel", key="exportar_excel_vr_produto")
        if opcao_exportar_excel_vr_produto and not df_exibicao_vr_produto.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_exibicao_vr_produto.to_excel(writer, sheet_name='Conciliação_VR_PRODUTO', index=False)
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name='conciliacao_fiscal_vr_produto.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

if st.session_state.show_imposto:
    df_exibicao_imposto = processar_imposto(df_pegasus_m, df_nbs, df_pegasus_b)

    # Aplicando filtro de status
    df_exibicao_imposto = aplicar_filtros(df_exibicao_imposto, status_selecionado)

    with result_col9:
        st.subheader("Conciliação IMPOSTO")

        status_counts = df_exibicao_imposto['STATUS'].value_counts()
        total_conciliados = status_counts.get('OK', 0)
        total_divergentes = status_counts.get('Divergente', 0)

        exibir_estatisticas(total_conciliados, total_divergentes)
        st.dataframe(df_exibicao_imposto.style.applymap(highlight_status, subset=['STATUS']), key="imposto")

        opcao_exportar_excel_imposto = st.checkbox("Exportar para Excel", key="exportar_excel_imposto")
        if opcao_exportar_excel_imposto and not df_exibicao_imposto.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_exibicao_imposto.to_excel(writer, sheet_name='Conciliação_IMPOSTO', index=False)
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name='conciliacao_fiscal_imposto.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

if st.session_state.show_vripi:
    df_exibicao_vripi = processar_vripi(df_pegasus_p, df_nbs, df_pegasus_b)

    # Aplicando filtro de status
    df_exibicao_vripi = aplicar_filtros(df_exibicao_vripi, status_selecionado)

    with result_col10:
        st.subheader("Conciliação VRIPI")

        status_counts = df_exibicao_vripi['STATUS'].value_counts()
        total_conciliados = status_counts.get('OK', 0)
        total_divergentes = status_counts.get('Divergente', 0)

        exibir_estatisticas(total_conciliados, total_divergentes)
        st.dataframe(df_exibicao_vripi.style.applymap(highlight_status, subset=['STATUS']), key="vripi")

        opcao_exportar_excel_vripi = st.checkbox("Exportar para Excel", key="exportar_excel_vripi")
        if opcao_exportar_excel_vripi and not df_exibicao_vripi.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_exibicao_vripi.to_excel(writer, sheet_name='Conciliação_VRIPI', index=False)
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name='conciliacao_fiscal_vripi.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
if st.session_state.show_bcst:
    df_exibicao_bcst = processar_bcst(df_pegasus_n, df_nbs, df_pegasus_b)

    # Aplicando filtro de status
    df_exibicao_bcst = aplicar_filtros(df_exibicao_bcst, status_selecionado)

    with result_col11:
        st.subheader("Conciliação BCST")

        status_counts = df_exibicao_bcst['STATUS'].value_counts()
        total_conciliados = status_counts.get('OK', 0)
        total_divergentes = status_counts.get('Divergente', 0)

        exibir_estatisticas(total_conciliados, total_divergentes)
        st.dataframe(df_exibicao_bcst.style.applymap(highlight_status, subset=['STATUS']), key="bcst")

        opcao_exportar_excel_bcst = st.checkbox("Exportar para Excel", key="exportar_excel_bcst")
        if opcao_exportar_excel_bcst and not df_exibicao_bcst.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_exibicao_bcst.to_excel(writer, sheet_name='Conciliação_BCST', index=False)
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name='conciliacao_fiscal_bcst.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

if st.session_state.show_vrst:
    df_exibicao_vrst = processar_vrst(df_pegasus_o, df_nbs, df_pegasus_b)

    # Aplicando filtro de status
    df_exibicao_vrst = aplicar_filtros(df_exibicao_vrst, status_selecionado)

    with result_col12:
        st.subheader("Conciliação VRST")

        status_counts = df_exibicao_vrst['STATUS'].value_counts()
        total_conciliados = status_counts.get('OK', 0)
        total_divergentes = status_counts.get('Divergente', 0)

        exibir_estatisticas(total_conciliados, total_divergentes)
        st.dataframe(df_exibicao_vrst.style.applymap(highlight_status, subset=['STATUS']), key="vrst")

        opcao_exportar_excel_vrst = st.checkbox("Exportar para Excel", key="exportar_excel_vrst")
        if opcao_exportar_excel_vrst and not df_exibicao_vrst.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_exibicao_vrst.to_excel(writer, sheet_name='Conciliação_VRST', index=False)
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name='conciliacao_fiscal_vrst.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
import os
os.system('pause')
