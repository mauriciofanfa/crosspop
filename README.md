# 📊 Analisador de Pesquisas — Crosstables e Heatmaps

Este projeto automatiza a análise de pesquisas realizadas em formulários (ex.: Google Forms).  

Ele gera tabelas cruzadas (**crosstables**), gráficos de calor (**heatmaps**) e notas para facilitar a compreensão das relações entre as respostas.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23376034.svg)](https://doi.org/10.5281/zenodo.23376034)

## ⚠️🚨 Importante

Este material tem **fins exclusivamente didáticos**. As análises automatizadas tem uso em contexto pedagógico. As análises devem ser revisadas.

Este material **não substitui análises estatísticas profissionais** e pode conter ou cometer erros.

Não recomendo utilizar para análise de dados fora de contextos educacionais. Procure softwares especializados (ex: PSPP).

## Desenvolvimento assistido por IA

Este script foi desenvolvido com apoio do modelo GPT-4o que auxiliou na concepção, implementação e documentação do código.

O usuário é responsável por revisar, validar e interpretar os resultados, levando em conta que a ferramenta oferece **apoio analítico e não substitui o julgamento humano**.

## Problemas conhecidos

Coluna inicial é ignorada: a primeira coluna do arquivo é desconsiderada (normalmente ID/data). Se seu arquivo não tiver essa coluna, você vai perder uma variável.

Faltantes não são “Não”: respostas em branco/ausentes não significam “não”. Misturar as duas coisas distorce percentuais e testes. Ideal: tratar “Sem resposta” como categoria separada ou remover faltantes antes de rodar.

Categorias com um único valor: se todo mundo respondeu a mesma coisa numa pergunta, os cruzamentos com essa pergunta viram “Não aplicável” (não dá pra testar associação).

Teste Qui-quadrado: o script usa Qui-quadrado para verificar associação entre duas perguntas categóricas. Esse teste pressupõe pelo menos 2 linhas e 2 colunas na tabela e frequências esperadas razoáveis (tipicamente ≥5).

Tabelas pequenas (2×2) com poucas contagens: resultados podem ser instáveis. O script não troca automaticamente para o teste exato de Fisher; trate resultados de 2×2 com muitas células pequenas com cautela.

Múltiplas comparações: como muitos pares são testados, o script ajusta os p-valores pelo método Benjamini–Hochberg (controle de FDR). Ainda assim, com muitos cruzamentos, alguns “significativos” podem aparecer ao acaso.

Tamanho de efeito (V de Cramér): é mostrado junto do p-valor. O V depende do nº de categorias; rótulos “fraco/moderado/forte” são aproximações, não verdades absolutas. Em amostras pequenas, o V pode parecer maior do que é.

Ordem das categorias ignorada: tudo é tratado como nominal. Se suas categorias têm ordem (ex.: “Baixo < Médio < Alto”), isso não é considerado nem nos testes nem na visualização.

Significância ≠ importância prática: p-valor baixo indica associação estatística, não causalidade. Use o V de Cramér e o contexto para julgar relevância.

Percentuais dos heatmaps: há três visões (total, por linha, por coluna). Confira o título/legenda para saber de que universo é o percentual — é comum confundir.

“Não aplicável” não é erro: aparece quando não há variação suficiente para testar (ex.: pergunta com uma única resposta).

Muitos arquivos: o número de cruzamentos cresce rápido (≈ n·(n−1)/2). Com muitas perguntas, espere centenas/milhares de imagens e um Excel grande. Reserve tempo e espaço em disco.

Tempo de execução: tabelas grandes ou muitas categorias tornam a execução mais lenta.

Cruzamentos inválidos podem causar incoerências: em casos com perguntas “constantes”, alguns resultados podem não ser calculados; se notar valores estranhos (por ex., título sem números, p-valor sem sentido), reexecute e verifique se há perguntas com uma única categoria.

Ordem/rotulagem das categorias: os heatmaps podem ordenar categorias alfabeticamente; se isso confundir, reorganize seus dados para impor a ordem desejada antes de rodar.

Limpe faltantes (ou rotule como “Sem resposta”).

Verifique se cada pergunta tem pelo menos duas categorias com contagens razoáveis.

Se o objetivo for tendência/ordem, considere análises específicas (não cobertas por este script).

---

## 🎓 Contexto acadêmico

Este projeto foi desenvolvido por Mauricio de Souza Fanfa em 2025/1 para analisar dados de questionários (surveys) produzidos pelos discentes da disciplina de **Pesquisa de Opinião Pública** do **Curso de Comunicação Social da Universidade Federal de Santa Maria (UFSM)**.

---

## 🚀 O que o script faz

Para cada arquivo CSV de pesquisa:

1. **Cria uma subpasta exclusiva** dentro de `resultados_crosstables/` com o nome da pesquisa.
2. **Gera um arquivo Excel** com tabelas cruzadas de todas as perguntas.
3. **Produz três tipos de heatmaps** para cada cruzamento de perguntas:
   - **Total** → porcentagens em relação ao total de respostas.  
   - **Linha** → porcentagens normalizadas por linha (cada linha = 100%).  
   - **Coluna** → porcentagens normalizadas por coluna (cada coluna = 100%).  
4. **Calcula estatísticas de associação**:
   - **Qui-quadrado de Pearson** → verifica se há associação entre duas perguntas.
   - **p-ajustado (Benjamini-Hochberg)** → controla o risco de falsos positivos.
   - **V de Cramer** → mede a força da associação (0 a 1).
5. **Gera um resumo consolidado** com recomendações interpretativas automáticas.

---

## 📂 Estrutura das pastas de saída

```
resultados_crosstables/
  Pesquisa_X/
    Pesquisa_X_crosstables.xlsx
    Pesquisa_X_resumo_consolidado.xlsx
    heatmaps_total/
    heatmaps_linha/
    heatmaps_coluna/
```

- **`*_crosstables.xlsx`** → contém todas as tabelas cruzadas com formatação condicional.
- **`*_resumo_consolidado.xlsx`** → resumo geral com estatísticas e recomendações.
- **`heatmaps_*`** → pastas com gráficos de calor para cada cruzamento de perguntas.

---

## 📘 Como rodar

1. Instale as dependências (preferencialmente em um ambiente virtual Anaconda):

```bash
pip install pandas numpy scipy matplotlib seaborn statsmodels xlsxwriter
```

2. Coloque seus arquivos CSV de pesquisas na pasta `csv/`.

3. Execute o script:

```bash
python crosspop.py
```

4. Veja os resultados na pasta `resultados_crosstables/`.

---

## 📊 Como interpretar os resultados

### 1. Excel de Crosstables

Cada aba do Excel corresponde ao cruzamento de duas perguntas.  
As células mostram **quantidade absoluta e percentual** de respostas.

#### 🟩 Formatação condicional
- **Verde escuro** → Associação estatisticamente significativa **moderada ou forte**  
- **Verde claro** → Associação estatisticamente significativa **fraca**  
- **Sem cor** → Não significativo (p-aj ≥ 0.05)  

---

### 2. Heatmaps

Cada gráfico mostra visualmente como as respostas se distribuem.

- **Heatmaps Total** → intensidade azul proporcional ao percentual geral.
- **Heatmaps Linha** → cada linha soma 100%. Útil para ver **tendências dentro de um grupo**.
- **Heatmaps Coluna** → cada coluna soma 100%. Útil para ver **como grupos se distribuem em cada resposta**.

#### 🔹 Informações no título:
```
Pergunta A / Pergunta B
N=256 | V de Cramer=0.32 (Moderada) | Qui²=35.6, gl=6, p-aj=0.002 (Sim)
```

- **N=256** → número total de respostas usadas.  
- **V de Cramer=0.32 (Moderada)** → força da associação.  
- **Qui²=35.6, gl=6, p-aj=0.002 (Sim)** → teste estatístico de associação.  
  - `gl` = graus de liberdade.  
  - `p-aj` = p-ajustado (se < 0.05 → significativo).  

---

### 3. Resumo Consolidado

Arquivo **`*_resumo_consolidado.xlsx`** contém todas as combinações analisadas.  
Colunas explicadas:

| Coluna           | Significado                                                                 |
|------------------|-----------------------------------------------------------------------------|
| Pergunta 1       | Primeira pergunta cruzada                                                   |
| Pergunta 2       | Segunda pergunta cruzada                                                    |
| N                | Número de respostas válidas                                                 |
| Qui²             | Estatística do teste Qui-quadrado                                           |
| gl               | Graus de liberdade                                                          |
| p-aj (Qui²)      | p-valor ajustado (Benjamini-Hochberg)                                       |
| V de Cramer      | Medida de força da associação                                               |
| Força            | Classificação: Fraca, Moderada, Forte, Muito forte                         |
| Significância    | "Sim" se p-aj < 0.05, senão "Não"                                           |
| Recomendação     | Texto interpretativo (ex.: "Destacar na análise", "Sem associação relevante")|

---

## 📐 Como interpretar as medidas estatísticas

- **Qui-quadrado**:  
  Mede se há relação entre duas perguntas.  
  - Valor alto → maior chance de associação.  
- **p-ajustado (p-aj)**:  
  Controla o risco de encontrar associações por acaso.  
  - `< 0.05` → associação estatisticamente significativa.  
- **V de Cramer (0 a 1)**:  
  Mede a **força da associação**.  
  - 0.00–0.09 → Desprezível  
  - 0.10–0.29 → Fraca  
  - 0.30–0.49 → Moderada  
  - 0.50–0.69 → Forte  
  - ≥0.70 → Muito forte  

---

## 📚 Glossário

📊 Qui-quadrado de Pearson

Imagine que você tem várias caixinhas de brinquedos e quer saber se a cor dos brinquedos depende da caixa em que estão. O teste do qui-quadrado conta quantos brinquedos estão em cada caixa e vê se a distribuição parece “normal” (o que esperaríamos por acaso) ou se há algo especial acontecendo. Se o resultado for grande o bastante, quer dizer que a cor e a caixa provavelmente estão relacionadas. "Essas caixas estão organizadas por cor!"

📉 p-valor

O p-valor é como um alarme de “isso pode ter acontecido por acaso”. Se ele é bem pequeno (menor que 0,05, ou seja, 5%), o alarme diz: “Olha, isso dificilmente foi sorte, tem uma relação real aqui”. Se for maior, quer dizer que pode ser só coincidência.

🧮 Correção de múltiplas comparações (Benjamini-Hochberg)

Pense em jogar várias vezes uma moeda e torcer para dar cara. Quanto mais vezes você joga, maior a chance de dar cara só por sorte. Essa correção ajusta os resultados quando fazemos muitos testes ao mesmo tempo, para que não caiamos na armadilha de pensar que algo é especial quando foi só sorte.

🔗 V de Cramer

É como uma régua que mede o quão forte duas coisas estão conectadas. Vai de 0 a 1:

0 quer dizer que não há conexão.

1 quer dizer que estão totalmente ligadas.
Então, se der 0,30, por exemplo, é como dizer “existe uma conexão moderada entre elas”.

🏷️ Graus de liberdade (gl)

Imagine que você está montando uma tabela de combinações, como “meninos/meninas” e “gostam/não gostam de pizza”. O número de escolhas livres que você pode fazer antes de ficar sem opções é o que chamamos de graus de liberdade. Ele ajuda a calcular o quão confiável é o resultado do qui-quadrado.

📦 Amostra (N)

É o número de pessoas que realmente responderam à pesquisa. Quanto maior esse número, mais confiável é o que descobrimos. Se só 5 pessoas responderam, é como perguntar só para a sua família. Se 500 responderam, você tem uma visão muito mais clara.

---

## ✅ Exemplo de recomendação automática

```
Pergunta 1: Qual seu centro?
Pergunta 2: Você acha que o tema deve ser debatido?

N = 245 | Qui² = 38.7, gl = 6, p-aj = 0.001
V de Cramer = 0.33 (Moderada)

Recomendação:
"Associação significativa moderada — vale explorar em gráficos e texto"
```

---

## ⚠ Notas importantes

- Se **N < 30**, as recomendações vêm acompanhadas de ⚠ (alerta) indicando que a amostra é pequena.  
- Associações **fracas** só devem ser interpretadas se fizerem sentido teórico.  
- **Não significativo** → provavelmente é fruto do acaso.  

---

## 📌 Boas práticas para interpretação

1. **Olhe sempre o contexto teórico**  
   - Uma associação fraca pode ser relevante se fizer sentido na realidade estudada.  
   - Evite tirar conclusões apenas pela cor do heatmap ou pelo valor de V de Cramer.

2. **Dê mais peso às associações moderadas e fortes**  
   - Associações com V de Cramer ≥ 0.30 e p-aj < 0.05 merecem destaque.  
   - Associações fracas devem ser interpretadas com cautela.

3. **Considere o tamanho da amostra (N)**  
   - Amostras pequenas podem inflar correlações ou gerar resultados instáveis.  
   - Sempre verifique se N ≥ 30 antes de dar destaque.

4. **Não confunda associação com causalidade**  
   - O script mostra se variáveis estão relacionadas, mas não diz qual causa qual.  

5. **Use as três visões dos heatmaps**  
   - **Total** para ver o panorama geral.  
   - **Linha** para identificar padrões por grupo.  
   - **Coluna** para ver como categorias se distribuem em cada resposta.

6. **Valide os resultados mais importantes**  
   - Ao encontrar associações fortes, confira se fazem sentido com o que já se sabe.  
   - Se parecer contraintuitivo, pode valer investigar mais antes de concluir.

7. **Priorize clareza ao comunicar**  
   - Prefira destacar resultados fortes e significativos.  
   - Evite sobrecarregar leitores com dezenas de cruzamentos irrelevantes.

---

## 📌 Conclusão

Este script transforma dados brutos de pesquisas em relatórios ricos e gráficos intuitivos, combinando:

- **Facilidade de leitura (heatmaps e Excel)**
- **Rigor estatístico (Qui², p-aj, V de Cramer)**
- **Interpretação automática (coluna Recomendação)**

Assim, você consegue identificar rapidamente quais relações entre respostas **merecem atenção** e quais **podem ser descartadas**.
