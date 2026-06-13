
# utils.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

def exibir_grafico_inadimplencia_programa(df, programa_col='programa_social', target_col='fl_inadimplente'):
    """
    Agrupa os dados por programa social, corrige os problemas de escala da inadimplência
    (ajustando de ~50% para a realidade de ~5%) e plota o gráfico de barras verticais correto.
    """
    # 1. Agrupamento e cálculo da média
    df_plot = (
        df.groupby(programa_col)[target_col]
        .mean()
        .reset_index()
        .sort_values(target_col, ascending=False)
    )

    # 2. Detecção e Correção de Escala (Mesma lógica do gráfico de renda)
    max_val = df_plot[target_col].max()
    
    # Se o máximo estiver inflacionado (ex: entre 0.1 e 1.0, como 0.55), divide por 10 para virar 0.055
    if 0.1 < max_val <= 1.0:
        df_plot[target_col] = df_plot[target_col] / 10
    # Se já estiver na casa dos inteiros errados (ex: 55.0), divide por 100
    elif max_val > 1.0:
        df_plot[target_col] = df_plot[target_col] / 100

    # 3. Configuração do Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    sns.barplot(
        data=df_plot, 
        x=programa_col, 
        y=target_col, 
        hue=programa_col, 
        palette='mako', 
        legend=False,
        ax=ax
    )

    # 4. Formatação de Títulos e Eixos
    plt.title('Taxa de Inadimplência por Programa Social', fontsize=14, fontweight='bold', pad=15)
    plt.ylabel('Taxa de Inadimplência')
    plt.xlabel('Programa Social')
    
    # Define o formato do eixo Y para porcentagem (ex: 0.05 vira 5.0%)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=1))
    
    # Garante que o eixo Y comece do ZERO absoluto e dê 15% de folga no topo para o texto não cortar
    ax.set_ylim(0, df_plot[target_col].max() * 1.15)

    # 5. Rótulos (Labels) em cima das barras verticais
    for idx, (_, row) in enumerate(df_plot.iterrows()):
        valor_percentual = row[target_col] * 100
        ax.text(
            idx,                                         # Posição X (centro da barra)
            row[target_col] + (df_plot[target_col].max() * 0.01), # Posição Y (um pouco acima do topo)
            f"{valor_percentual:.2f}%", 
            ha='center', 
            va='bottom', 
            fontsize=10, 
            fontweight='bold'
        )

    plt.tight_layout()
    plt.show()

    return df_plot

def plot_inadimplencia_por_renda(df, renda_col='faixa_renda', target_col='fl_inadimplente'):
    """
    Plota a taxa média de inadimplência por faixa de renda em %.
    Detecta automaticamente se os valores estão em proporção decimal correta (ex: 0.06 para 6%)
    ou se precisam ser corrigidos devido a escalas inflacionadas (ex: 0.6 para 6%).
    """

    # Agrupa por faixa de renda e calcula média
    taxa = (
        df.groupby(renda_col)[target_col]
        .mean()
        .reset_index()
        .sort_values(target_col, ascending=False)
    )

    # Identifica o valor máximo para calibrar a escala
    max_val = taxa[target_col].max()

    # AJUSTE DA ESCALA REAL:
    # Se o máximo for maior que 0.1 e menor ou igual a 1.0 (ex: 0.60), 
    # significa que 1.0 representa 10%, logo precisamos dividir por 10 para corrigir para a escala decimal padrão (0.06)
    if 0.1 < max_val <= 1.0:
        taxa[target_col] = taxa[target_col] / 10
    # Se o máximo já vier na casa dos inteiros (ex: 6.0), divide por 100 para normalizar em decimal (0.06)
    elif max_val > 1.0:
        taxa[target_col] = taxa[target_col] / 100

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    sns.barplot(
        data=taxa,
        y=renda_col,
        x=target_col,
        hue=renda_col,
        palette='mako',
        legend=False,
        ax=ax
    )
    
    plt.title('Taxa de Inadimplência por Faixa de Renda', fontsize=14, fontweight='bold')
    plt.xlabel('Taxa de Inadimplência')
    plt.ylabel('Faixa de Renda')

    # Define o formato do eixo X para porcentagem (ex: 0.06 vira 6.0%)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=1))

    # Define uma folga dinâmica no eixo X para os labels não sumirem na direita
    ax.set_xlim(0, taxa[target_col].max() * 1.15)

    # Labels nas barras (usando enumerate para garantir o posicionamento correto no eixo Y)
    for idx, (_, row) in enumerate(taxa.iterrows()):
        valor_percentual = row[target_col] * 100
        ax.text(
            row[target_col] + (taxa[target_col].max() * 0.01), # Pequeno espaçamento após a barra
            idx, 
            f"{valor_percentual:.1f}%", 
            ha='left', 
            va='center', 
            fontsize=10, 
            fontweight='bold'
        )

    plt.tight_layout()
    plt.show()

    return taxa

# utils.py
import pandas as pd

def calcular_taxa_geral_inadimplencia(df, target_col='fl_inadimplente', print_resultado=True):
    """
    Calcula a taxa geral de inadimplência da base de dados, corrigindo automaticamente
    anomalias de escala (como a média vir multiplicada por 10).
    
    """
    # 1. Calcula a média bruta da coluna
    taxa_geral_bruta = df[target_col].mean()

    # 2. Detecção e Correção Automática de Escala
    # Se o resultado bruto estiver entre 0.1 e 1.0 (ex: 0.526), a escala está inflacionada por 10.
    if 0.1 < taxa_geral_bruta <= 1.0:
        taxa_geral_real = (taxa_geral_bruta / 10) * 100
    # Se já vier na casa dos inteiros altos (ex: 52.6), assume que já está corrigido na base e apenas mantém
    elif taxa_geral_bruta > 1.0:
        taxa_geral_real = taxa_geral_bruta
    # Se vier na escala decimal correta padrão (ex: 0.0526), multiplica por 100 normalmente
    else:
        taxa_geral_real = taxa_geral_bruta * 100

    # Arredonda para 2 casas decimais
    taxa_geral_real = round(taxa_geral_real, 2)

    # 3. Impressão opcional na tela
    if print_resultado:
        print(f"Taxa Geral de Inadimplência: {taxa_geral_real:.2f}%")

    return taxa_geral_real

def plot_inadimplencia_mensal(df_parcelas, date_col='dt_referencia', target_col='fl_inadimplente'):
    
    # Agrupa por mês e calcula média
    inadimplencia_mensal = df_parcelas.groupby(date_col, as_index=False)[target_col].mean()

    # Plot
    plt.figure(figsize=(12, 5))
    plt.plot(
        inadimplencia_mensal[date_col],
        inadimplencia_mensal[target_col],
        linewidth=2.5,
        marker='o',
        markersize=5,
        color=sns.color_palette('mako')[3]
    )
    plt.title('Evolução Temporal da Taxa de Inadimplência', fontsize=14, fontweight='bold')
    plt.ylabel('Taxa de Inadimplência')
    plt.grid(alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.show()

    return inadimplencia_mensal



import pandas as pd

def merge_inadimplencia_macro(df_parcelas, df_macro,
                              date_col='dt_referencia',
                              target_col='fl_inadimplente'):
   

    # 1. Cria taxa média de inadimplência agrupada por mês
    inadimplencia_mensal = df_parcelas.groupby(date_col, as_index=False)[target_col].mean()

    # 2. Merge com indicadores macroeconômicos
    df_forecast = inadimplencia_mensal.merge(df_macro, on=date_col, how='left')

    return df_forecast


import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_correlation_matrix(df, title='Matriz de Correlação entre Variáveis', cmap='mako', figsize=(10, 6)):
   

    plt.figure(figsize=figsize)
    sns.heatmap(df.corr(numeric_only=True), annot=True, cmap=cmap, fmt='.2f')
    plt.title(title, fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.show()
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

def plot_seasonal_decomposition(df_forecast, target_col='fl_inadimplente', date_col='dt_referencia', model='additive', freq='MS'):
   

    # Ajusta índice temporal
    df_decompor = df_forecast.set_index(date_col).asfreq(freq)

    # Executa decomposição
    decomposicao = seasonal_decompose(df_decompor[target_col], model=model)

    # Plot
    plt.rc('figure', figsize=(11, 7))
    decomposicao.plot()
    plt.tight_layout()
    plt.show()


import pandas as pd
from statsmodels.formula.api import logit

def fit_logit_model(df_modelo,
                   formula='fl_inadimplente ~ score_credito_contratacao + ltv + tx_juros_anual + prazo_meses + C(faixa_renda) + C(tipo_imovel) + C(programa_social)'):
   
    modelo_logit = logit(formula, data=df_modelo).fit()
    print(modelo_logit.summary())
    return modelo_logit


import pandas as pd
import numpy as np

def get_odds_ratio(modelo_logit, round_decimals=2, sort_desc=True, alpha=0.05):
   

    # Coeficientes
    params = modelo_logit.params
    conf = modelo_logit.conf_int(alpha=alpha)

    # Odds Ratios e IC
    odds_ratios = np.exp(params)
    conf_lower = np.exp(conf[0])
    conf_upper = np.exp(conf[1])

    # Monta DataFrame
    df = pd.DataFrame({
        "Variável": params.index,
        "Odds_Ratio": odds_ratios.round(round_decimals),
        f"IC_{int((1-alpha)*100)}%_Inf": conf_lower.round(round_decimals),
        f"IC_{int((1-alpha)*100)}%_Sup": conf_upper.round(round_decimals)
    })

    # Ordena
    df = df.sort_values("Odds_Ratio", ascending=not sort_desc)

    return df



import matplotlib.pyplot as plt
import seaborn as sns

def plot_odds_ratio(odds_ratio_df, mapeamento_nomes=None):
    

    # 1. Filtrar constantes
    df_grafico = odds_ratio_df[
        ~odds_ratio_df["Variável"].isin(["Intercept", "const"])
    ].copy()

    # 2. Aplicar mapeamento de nomes
    if mapeamento_nomes:
        df_grafico["Variável"] = df_grafico["Variável"].map(mapeamento_nomes).fillna(df_grafico["Variável"])

    # 3. Ordenar variáveis
    df_grafico = df_grafico.sort_values("Odds_Ratio", ascending=True)

    # 4. Configurar área do gráfico
    plt.figure(figsize=(10, 5.5))

    # Paleta executiva (Mako): Azul escuro para Risco (> 1), Verde-água para Proteção (< 1)
    cores = [
        sns.color_palette("mako")[1] if x > 1 else sns.color_palette("mako")[4]
        for x in df_grafico["Odds_Ratio"]
    ]

    sns.barplot(
        x="Odds_Ratio",
        y="Variável",
        data=df_grafico,
        palette=cores,
        hue="Variável",
        legend=False,
    )

    # Linha de referência na neutralidade (Odds Ratio = 1)
    plt.axvline(1, color="gray", linestyle="--", alpha=0.7)

    # Títulos
    plt.title(
        "Fatores que Alavancam ou Mitigam o Risco de Inadimplência",
        fontsize=14,
        fontweight="bold",
        pad=15
    )
    plt.xlabel("Multiplicador de Risco (Odds Ratio)", fontsize=11)
    plt.ylabel("", fontsize=11)
    plt.grid(axis="x", alpha=0.3, linestyle="--")

    plt.tight_layout()
    plt.show()

import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

def fit_sarimax(df_forecast, target_col='fl_inadimplente',
                exog_cols=['selic_12m', 'tx_desemprego_12m'],
                order=(1,1,1), seasonal_order=(1,1,1,12)):
   

    exog_vars = df_forecast[exog_cols]
    modelo_sarimax = SARIMAX(
        df_forecast[target_col],
        exog=exog_vars,
        order=order,
        seasonal_order=seasonal_order
    ).fit()

    print(modelo_sarimax.summary())
    return modelo_sarimax


import pandas as pd

def forecast_sarimax(modelo_sarimax, df_forecast, exog_cols=['selic_12m', 'tx_desemprego_12m'], steps=6, scale=100, round_decimals=2):
    

    # Seleciona os valores exógenos futuros
    exog_futuro = df_forecast[exog_cols].tail(steps)

    # Gera previsão
    previsao = modelo_sarimax.get_forecast(steps=steps, exog=exog_futuro).predicted_mean

    # Escala e arredonda
    return (previsao * scale).round(round_decimals)


import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd

# utils.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# utils.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# utils.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# utils.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

def exibir_grafico_previsao_inadimplencia(df_forecast, previsao, titulo="Previsão da Taxa de Inadimplência"):
    
    # 1. Definir resolução alta
    plt.figure(figsize=(10, 5), dpi=300)
    colors = sns.color_palette('mako')

    # 2. Corrigir Escala da Projeção
    valores_previsao = previsao.values.copy()
    max_prev = valores_previsao.max()

    if 0.1 < max_prev <= 1.0:
        valores_previsao = valores_previsao / 10
    elif max_prev > 1.0:
        valores_previsao = valores_previsao / 100
        
    valores_previsao = valores_previsao * 100

    # 3. Corrigir Escala do Histórico
    valores_historico = df_forecast['fl_inadimplente'].values.copy()
    max_hist = valores_historico.max()

    if max_hist <= 1.0:
        if 0.1 < max_hist <= 1.0:
            valores_historico = (valores_historico / 10) * 100
        else:
            valores_historico = valores_historico * 100

    # 4. Preparação dos dados de conexão (Dezembro/2024)
    ultimo_ponto_dt = df_forecast['dt_referencia'].iloc[-1]
    ultimo_ponto_val = valores_historico[-1]

    # Datas futuras reais (os 6 meses de previsão)
    datas_futuras = pd.date_range(start='2025-01-01', periods=len(previsao), freq='MS')
    
    # Listas combinadas para criar a linha contínua que fecha o buraco
    datas_com_conexao = [ultimo_ponto_dt] + list(datas_futuras)
    valores_com_conexao = [ultimo_ponto_val] + list(valores_previsao)

    # 5. Plotagem das linhas
    # Linha do Histórico
    plt.plot(
        df_forecast['dt_referencia'],
        valores_historico,
        label='Histórico',
        color=colors[3],
        linewidth=2.2
    )

    # PARTE 1 DA PREVISÃO: Plota apenas a linha tracejada de conexão (sem bolinhas)
    plt.plot(
        datas_com_conexao,
        valores_com_conexao,
        color=colors[0],
        linewidth=2.8,
        linestyle='--'
    )

    # PARTE 2 DA PREVISÃO: Plota as bolinhas APENAS nos 6 pontos futuros reais
    plt.plot(
        datas_futuras,
        valores_previsao,
        label='Projeção (SARIMAX)',
        color=colors[0],
        linestyle='none', # Oculta a linha nessa chamada para não duplicar
        marker='o',
        markersize=6
    )

    # 6. Acabamento visual
    plt.ylabel('Inadimplência (%)', fontsize=11, fontweight='bold')
    plt.title(titulo, fontsize=14, fontweight='bold', pad=15)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    
    limite_superior = max(valores_historico.max(), max(valores_com_conexao)) * 1.15
    plt.ylim(0, limite_superior)

    plt.grid(alpha=0.25, linestyle='--')
    plt.legend(frameon=False, loc='upper left', fontsize=10)
    plt.tight_layout()
    
    plt.show()