import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
import itertools
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.multitest import multipletests

# ------------------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------------------

def limpar_nome_sheet(nome):
    """
    Ajusta o nome da aba no Excel para evitar caracteres inválidos.
    Mantém no máximo 31 caracteres (limite do Excel).
    """
    inval = '[]:*?/\\'
    for ch in inval:
        nome = nome.replace(ch, " ")
    return nome[:31]

def calcular_v_cramer(chi2, n, r, k):
    """
    Calcula o V de Cramer como medida de associação para tabelas de contingência.
    
    Parâmetros:
        chi2: valor do teste qui-quadrado
        n: tamanho total da amostra
        r: número de linhas da tabela
        k: número de colunas da tabela
    
    Retorna:
        v_cramer (float)
    """
    return np.sqrt(chi2 / (n * (min(r, k) - 1))) if min(r, k) > 1 else np.nan

def classificar_forca(v, categorias):
    """
    Classifica a força da associação com base no valor do V de Cramer
    e no número de categorias envolvidas.
    
    Retorna: string ("Fraca", "Moderada", "Forte", "Muito forte", "Não aplicável")
    """
    if np.isnan(v):
        return "Não aplicável"
    if categorias <= 2:
        limites = (0.10, 0.30, 0.50)
    elif categorias <= 4:
        limites = (0.07, 0.21, 0.35)
    else:
        limites = (0.06, 0.17, 0.29)

    if v < limites[0]:
        return "Fraca"
    elif v < limites[1]:
        return "Moderada"
    elif v < limites[2]:
        return "Forte"
    else:
        return "Muito forte"

def gerar_recomendacao(p_aj, v_cramer, n, linhas, colunas):
    """
    Gera um texto interpretativo de recomendação para cada cruzamento.
    Considera p-ajustado, V de Cramer, tamanho da amostra e número de categorias.
    """
    if np.isnan(v_cramer) or np.isnan(p_aj):
        return "Não aplicável (dados insuficientes)"
    if p_aj >= 0.05:
        return "Não significativo: sem associação relevante"

    categorias = min(linhas, colunas)
    if categorias <= 2:
        limite_fraco, limite_moderado, limite_forte = 0.10, 0.30, 0.50
    elif categorias <= 4:
        limite_fraco, limite_moderado, limite_forte = 0.07, 0.21, 0.35
    else:
        limite_fraco, limite_moderado, limite_forte = 0.06, 0.17, 0.29

    if v_cramer < limite_fraco:
        recomendacao = "Associação significativa, mas fraca"
    elif v_cramer < limite_moderado:
        recomendacao = "Associação significativa moderada — vale explorar em gráficos e texto"
    elif v_cramer < limite_forte:
        recomendacao = "Associação significativa forte — destacar na análise"
    else:
        recomendacao = "Associação muito forte — resultado chave para destaque"

    if n < 30:
        recomendacao += " ⚠ Amostra pequena, interpretar com cautela"

    return recomendacao

def gerar_heatmap(tabela_percentual, combinada_str, pasta_saida, col1, col2, n_total, v_cramer, forca, chi2, dof, p_chi_aj, significancia):
    """
    Gera e salva um heatmap baseado em percentuais.
    
    Parâmetros:
        tabela_percentual: DataFrame com percentuais
        combinada_str: DataFrame com strings formatadas (N + %)
        pasta_saida: caminho para salvar a imagem
        col1, col2: perguntas cruzadas
        n_total: total de respostas
        v_cramer, forca, chi2, dof, p_chi_aj, significancia: estatísticas para subtítulo
    """
    plt.figure(figsize=(max(8, len(tabela_percentual.columns) * 1.2), 
                        max(6, len(tabela_percentual.index) * 0.7)))
    sns.heatmap(tabela_percentual, annot=combinada_str, fmt="", cmap="Blues",
                cbar_kws={'label': '%'}, linewidths=1, linecolor="grey", annot_kws={"fontsize":9})
    
    plt.title(f"{col1} / {col2}\n"
              f"N={n_total} | V de Cramer={v_cramer:.2f} ({forca}) | "
              f"Qui²={chi2:.1f}, gl={dof}, p-aj={p_chi_aj:.3g} ({significancia})",
              fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, f"{limpar_nome_sheet(col1[:15]+'_'+col2[:15])}.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

# ------------------------------------------------------------------
# Função principal
# ------------------------------------------------------------------

def gerar_crosstables(path_csv, pasta_saida="resultados_crosstables"):
    """
    Para cada CSV:
      - Cria subpasta específica da pesquisa
      - Gera crosstables em Excel com formatação condicional
      - Produz 3 versões de heatmaps (total, linha, coluna)
      - Gera resumo consolidado em Excel com estatísticas e recomendações
    """
    nome_base = os.path.splitext(os.path.basename(path_csv))[0]
    pasta_pesquisa = os.path.join(pasta_saida, nome_base)
    os.makedirs(pasta_pesquisa, exist_ok=True)

    df = pd.read_csv(path_csv)
    df = df.iloc[:, 1:]  # Ignorar primeira coluna (carimbo de data/hora)

    # Criar subpastas para heatmaps
    pasta_total = os.path.join(pasta_pesquisa, "heatmaps_total")
    pasta_linha = os.path.join(pasta_pesquisa, "heatmaps_linha")
    pasta_coluna = os.path.join(pasta_pesquisa, "heatmaps_coluna")
    os.makedirs(pasta_total, exist_ok=True)
    os.makedirs(pasta_linha, exist_ok=True)
    os.makedirs(pasta_coluna, exist_ok=True)

    # Preparar arquivo Excel
    output_path = os.path.join(pasta_pesquisa, f"{nome_base}_crosstables.xlsx")
    writer = pd.ExcelWriter(output_path, engine="xlsxwriter")
    workbook = writer.book
    formato_verde = workbook.add_format({'bg_color': '#92D050'})
    formato_verde_claro = workbook.add_format({'bg_color': '#C6EFCE'})

    resultados_consolidados = []
    p_vals_chi2, info_chi2 = [], []

    # 1. Coletar estatísticas Qui² para cada par de perguntas
    for col1, col2 in itertools.combinations(df.columns, 2):
        tabela = pd.crosstab(df[col1], df[col2], margins=False)
        if tabela.size > 0:
            chi2, p_chi, dof, _ = chi2_contingency(tabela)
            p_vals_chi2.append(p_chi)
            info_chi2.append((col1, col2, tabela, chi2, p_chi, dof))

    # 2. Correção múltipla BH (Benjamini-Hochberg) para Qui²
    if p_vals_chi2:
        _, p_adj_chi2, _, _ = multipletests(p_vals_chi2, alpha=0.05, method="fdr_bh")
    else:
        p_adj_chi2 = []

    idx_c = 0
    # 3. Processar cada combinação de perguntas
    for col1, col2 in itertools.combinations(df.columns, 2):
        tabela = pd.crosstab(df[col1], df[col2], margins=False)

        # Criar tabelas de percentuais: total, por linha e por coluna
        tabela_total = (tabela / tabela.sum().sum()) * 100
        tabela_linha = tabela.div(tabela.sum(axis=1), axis=0) * 100
        tabela_coluna = tabela.div(tabela.sum(axis=0), axis=1) * 100

        # Strings formatadas para exibição (N + %)
        combinada_str_total = pd.DataFrame(index=tabela.index, columns=tabela.columns)
        combinada_str_linha = pd.DataFrame(index=tabela.index, columns=tabela.columns)
        combinada_str_coluna = pd.DataFrame(index=tabela.index, columns=tabela.columns)

        for i, idx in enumerate(tabela.index):
            for j, col in enumerate(tabela.columns):
                valor_abs = tabela.loc[idx, col]
                combinada_str_total.iloc[i, j] = f"{valor_abs} ({tabela_total.loc[idx, col]:.2f}%)"
                combinada_str_linha.iloc[i, j] = f"{valor_abs} ({tabela_linha.loc[idx, col]:.2f}%)"
                combinada_str_coluna.iloc[i, j] = f"{valor_abs} ({tabela_coluna.loc[idx, col]:.2f}%)"

        # Estatísticas
        if idx_c < len(info_chi2):
            info = info_chi2[idx_c]
            chi2, p_chi, dof = info[3], info[4], info[5]
            p_chi_aj = p_adj_chi2[idx_c]
            n_total = tabela.sum().sum()
            v_cramer = calcular_v_cramer(chi2, n_total, tabela.shape[0], tabela.shape[1])
            forca = classificar_forca(v_cramer, min(tabela.shape))
            recomendacao = gerar_recomendacao(p_chi_aj, v_cramer, n_total, tabela.shape[0], tabela.shape[1])
            significancia = "Sim" if p_chi_aj < 0.05 else "Não"
            idx_c += 1

            resultados_consolidados.append([
                col1, col2, n_total, chi2, dof, p_chi_aj,
                v_cramer, forca, significancia, recomendacao
            ])

            # Gerar os três heatmaps
            gerar_heatmap(tabela_total, combinada_str_total, pasta_total, col1, col2, n_total, v_cramer, forca, chi2, dof, p_chi_aj, significancia)
            gerar_heatmap(tabela_linha, combinada_str_linha, pasta_linha, col1, col2, n_total, v_cramer, forca, chi2, dof, p_chi_aj, significancia)
            gerar_heatmap(tabela_coluna, combinada_str_coluna, pasta_coluna, col1, col2, n_total, v_cramer, forca, chi2, dof, p_chi_aj, significancia)

        # 4. Escrever aba Excel com formatação condicional
        sheet_name = limpar_nome_sheet(f"{col1[:15]}_{col2[:15]}")
        combinada_str_total.to_excel(writer, sheet_name=sheet_name)
        worksheet = writer.sheets[sheet_name]
        worksheet.write(0, 0, f"{col1} / {col2}")

        for i in range(1, len(combinada_str_total.index) + 1):
            for j in range(1, len(combinada_str_total.columns) + 1):
                cell_value = combinada_str_total.iloc[i-1, j-1]
                try:
                    if significancia == "Sim":
                        if forca in ["Moderada", "Forte", "Muito forte"]:
                            fmt = formato_verde
                        elif forca == "Fraca":
                            fmt = formato_verde_claro
                        else:
                            fmt = None
                    else:
                        fmt = None
                    worksheet.write(i, j, cell_value, fmt)
                except:
                    worksheet.write(i, j, cell_value)

    # 5. Gerar resumo consolidado em Excel
    resumo_df = pd.DataFrame(resultados_consolidados,
                             columns=["Pergunta 1", "Pergunta 2", "N", "Qui²", "gl", 
                                      "p-aj (Qui²)", "V de Cramer", "Força", 
                                      "Significância", "Recomendação"])
    resumo_path_xlsx = os.path.join(pasta_pesquisa, f"{nome_base}_resumo_consolidado.xlsx")
    resumo_df.to_excel(resumo_path_xlsx, index=False)

    writer.close()
    print(f"✅ Heatmaps salvos em {pasta_total}, {pasta_linha}, {pasta_coluna}")
    print(f"✅ Resumo consolidado salvo em {resumo_path_xlsx}")

# ------------------------------------------------------------------
# Execução para todos os CSVs da pasta "csv"
# ------------------------------------------------------------------
for arquivo in glob.glob("csv/*.csv"):
    gerar_crosstables(arquivo)
