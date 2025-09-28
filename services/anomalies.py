import numpy as np
import pandas as pd

def detectar_anomalias_no_dataframe(df: pd.DataFrame):
    anomalias = []
    if df.empty:
        return ["Nenhum dado para analisar."]

    # Campos numéricos
    for campo in ["valor_principal_numerico", "prazo_total_meses", "taxa_juros_anual_numerica"]:
        if campo in df.columns:
            serie = pd.to_numeric(df[campo], errors="coerce").dropna()
            if len(serie) > 1:
                media, std = serie.mean(), serie.std()
                limite_sup, limite_inf = media + 2*std, media - 2*std
                outliers = df[(df[campo] > limite_sup) | (df[campo] < limite_inf)]
                for _, row in outliers.iterrows():
                    anomalias.append(
                        f"⚠️ Anomalia: `{campo}` em {row['arquivo_fonte']} = {row[campo]} (média {media:.2f} ± {2*std:.2f})"
                    )
    if not anomalias:
        return ["Nenhuma anomalia significativa."]
    return anomalias
