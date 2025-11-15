\subsubsection{Estudo de Caso 3: Decisão Familiar entre Modelos Versáteis}
Este estudo de caso simula a situação de uma família, composta por um casal e dois filhos, que busca um novo veículo para uso diário e viagens ocasionais. Suas prioridades incluem segurança, espaço interno adequado para a família e bagagem, boa economia de combustível e um nível razoável de tecnologia e conforto, tudo dentro de uma faixa de preço acessível para um veículo seminovo ou de entrada. Após uma pesquisa inicial, eles se encontram indecisos entre dois modelos populares no mercado que se encaixam em suas necessidades gerais: o Chevrolet Tracker e o Hyundai Creta. A dificuldade reside em comparar objetivamente as características de cada um, que muitas vezes são apresentadas de forma dispersa em diferentes fontes, dificultando uma tomada de decisão eficiente.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Imagens/fig_caso_3_carros.png}
    \caption{Seleção inicial do Chevrolet Tracker e Hyundai Creta.}
    \label{fig:caso3_versoes_iniciais}
\end{figure}

O sistema desenvolvido foi utilizado para auxiliar a família nessa decisão. Inicialmente, foram inseridos os dados dos dois modelos em versões equivalentes de entrada (por exemplo, Tracker \textbf{TA/A-6} e \textbf{Creta Comfort/A-6}), permitindo uma visualização lado a lado de suas especificações técnicas, dados de consumo do PBEV (Programa Brasileiro de Etiquetagem Veicular). A interface intuitiva do sistema facilitou a comparação direta de métricas como o consumo energético, a autonomia (km/l), o preço (puxado da FIPE API), o tipo de combustível e os principais poluentes. Adicionalmente, o resumo inteligente gerado pela integração com a API da OpenAI sintetizou as principais vantagens e desvantagens de cada modelo, traduzindo dados técnicos complexos em insights de fácil compreensão para a família.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Imagens/fig_caso_3_comparativo.png}
    \caption{Tabela comparativa entre Chevrolet Tracker e Hyundai Creta.}
    \label{fig:caso3_comparativo}
\end{figure}
\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Imagens/fig_caso_3_resumo.png}
    \caption{Resumo comparativo gerado pela IA para os modelos iniciais.}
    \label{fig:caso3_resumo}
\end{figure}

\paragraph{Transição para Análise de Versões Específicas:} A partir da comparação inicial entre o Chevrolet Tracker e o Hyundai Creta, a família pôde identificar o modelo que melhor se alinhava às suas prioridades gerais. Contudo, o sistema oferece um nível de detalhe ainda maior, permitindo que, uma vez decidido o modelo principal (por exemplo, o Chevrolet Tracker), a família possa comparar entre diferentes versões disponíveis (ex: Tracker \textbf{TA/A-6} vs. Tracker \textbf{12TARS/A-6}). Essa funcionalidade é crucial, pois as nuances em motorização e eficiência energética entre versões de um mesmo veículo podem ser tão significativas quanto as diferenças entre modelos distintos, impactando diretamente o custo-benefício e a adequação às expectativas específicas da família.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Imagens/fig_caso_3_mesmo_carro.png}
    \caption{Comparação entre diferentes versões do mesmo modelo (Chevrolet Tracker).}
    \label{fig:caso3_mesmo_carro}
\end{figure}

\paragraph{Conclusão do Estudo de Caso:} Este estudo de caso ilustra a capacidade da ferramenta em apoiar famílias na complexa jornada de escolha veicular. Indo além de uma comparação superficial, o sistema permite uma análise aprofundada que começa na seleção entre modelos versáteis e se estende à minuciosa avaliação de suas respectivas versões. A combinação da visualização detalhada de dados técnicos e ambientais com resumos inteligentes e customizáveis capacita os usuários a discernir as sutilezas entre as opções, garantindo uma decisão que não apenas atenda às necessidades práticas, mas também otimize o investimento e se alinhe com as expectativas de longo prazo da família.