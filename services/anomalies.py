import numpy as np
import pandas as pd

def detectar_anomalias_no_dataframe(df: pd.DataFrame):
    """
    Detecta anomalias numéricas em um DataFrame usando o critério de desvio padrão.
    """
    anomalias = []
    if df.empty:
        return ["Nenhum dado para analisar."]

    # Analisa campos numéricos para outliers
    for campo in ["valor_principal_numerico", "prazo_total_meses", "taxa_juros_anual_numerica"]:
        if campo in df.columns:
            # Converte a coluna para numérico, ignorando erros
            serie = pd.to_numeric(df[campo], errors="coerce").dropna()
            if len(serie) > 1:
                media, std = serie.mean(), serie.std()
                # Define limites como 2 desvios padrão da média
                limite_sup, limite_inf = media + 2 * std, media - 2 * std
                outliers = df[(pd.to_numeric(df[campo], errors='coerce') > limite_sup) | (pd.to_numeric(df[campo], errors='coerce') < limite_inf)]
                for _, row in outliers.iterrows():
                    anomalias.append(
                        f"⚠️ **Anomalia em `{row['arquivo_fonte']}`**: O campo `{campo}` tem valor `{row[campo]}`, que está fora da média de {media:.2f} (± {2*std:.2f})."
                    )
    if not anomalias:
        return ["Nenhuma anomalia numérica significativa foi detectada."]
    return anomalias
