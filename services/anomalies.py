import numpy as np
import pandas as pd

def detectar_anomalias_no_dataframe(df: pd.DataFrame):
    """
    Detecta anomalias numéricas em um DataFrame dinamicamente, analisando todas as colunas
    que possam ser interpretadas como numéricas.
    """
    anomalias = []
    if df.empty:
        return ["Nenhum dado para analisar."]

    # Itera sobre todas as colunas, exceto a de referência 'arquivo_fonte'
    for campo in df.columns:
        if campo == 'arquivo_fonte':
            continue

        # Tenta converter a coluna para um tipo numérico, tratando erros
        serie_numerica = pd.to_numeric(df[campo], errors='coerce')
        
        # Procede com a análise se a coluna tiver pelo menos 2 valores numéricos
        if serie_numerica.notna().sum() > 1:
            serie_limpa = serie_numerica.dropna()
            media, std = serie_limpa.mean(), serie_limpa.std()

            # Evita divisão por zero se todos os valores forem idênticos
            if std == 0:
                continue

            limite_sup, limite_inf = media + 2 * std, media - 2 * std
            
            # Identifica os outliers no DataFrame original
            outliers_mask = (serie_numerica > limite_sup) | (serie_numerica < limite_inf)
            outliers_df = df[outliers_mask]

            for _, row in outliers_df.iterrows():
                anomalias.append(
                    f"⚠️ **Anomalia em `{row['arquivo_fonte']}`**: O campo `{campo}` tem valor `{row[campo]}`, que está fora da média de {media:.2f} (± {2*std:.2f})."
                )
                
    if not anomalias:
        return ["Nenhuma anomalia numérica significativa foi detectada nos campos extraídos."]
    return anomalias

