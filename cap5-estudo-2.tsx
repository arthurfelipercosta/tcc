\subsection{Estudo de Caso 2: A comparação rápida de SUVs em trânsito}

\paragraph{Cenário e Objetivo do Usuário:} Este estudo de caso simula um usuário que, estando em trânsito ou precisando de uma decisão rápida, deseja comparar dois modelos específicos de SUV – o Jeep Renegade e o Hyundai Creta. O objetivo é obter uma análise comparativa concisa sobre as emissões de poluentes e o impacto ambiental, utilizando a conveniência de um assistente conversacional via celular.

\paragraph{Ferramenta Escolhida e Justificativa:} Para este cenário, o \textbf{assistente via WhatsApp} é a ferramenta ideal. Sua natureza móvel e interface conversacional permitem ao usuário interagir de forma rápida e intuitiva, obtendo informações cruciais sem a necessidade de um computador ou de navegar por menus complexos. O bot é otimizado para responder a comparações diretas, fornecendo dados essenciais para uma tomada de decisão ágil, mesmo em movimento.

\paragraph{Execução do Estudo de Caso:}
O fluxo de interação do usuário se inicia com o envio de mensagens ao bot via WhatsApp, informando sequencialmente os dados dos dois veículos para comparação: 'JEEP', 'RENEGADE' e a versão desejada, seguido por 'HYUNDAI', 'CRETA' e sua respectiva versão. A Figura \ref{fig:fluxo_whats} ilustra a arquitetura geral do workflow no N8N que orquestra essa comunicação e processamento.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Imagens/fig_fluxo_whats.png}
    \caption{Visão geral do workflow do assistente no N8N.}
    \label{fig:fluxo_whats}
\end{figure}

Após o usuário fornecer as informações, o nó 'Code' do N8N captura e armazena essas respostas internamente, consolidando os dados dos dois carros. A \textbf{Figura \ref{fig:informacoes}} demonstra o registro dessas informações, como 'brand1', 'model1', 'version1', 'brand2', 'model2', 'version2', no contexto da conversa.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Imagens/fig_informacoes.png}
    \caption{Informações dos veículos coletadas pelo nó 'Code' do N8N.}
    \label{fig:informacoes}
\end{figure}

Em seguida, o sistema realiza chamadas para a API de backend para obter as listas de versões disponíveis para cada modelo, garantindo que as versões informadas pelo usuário são válidas. As \textbf{Figuras \ref{fig:versoes_carro_1}} e \textbf{\ref{fig:versoes_carro_2}} exibem os dados de versão retornados para o Jeep Renegade e o Hyundai Creta, respectivamente.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.6\linewidth]{Imagens/fig_versoes_carro_1.png}
    \caption{Versões disponíveis para o Jeep Renegade, retornadas pela API.}
    \label{fig:versoes_carro_1}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.6\linewidth]{Imagens/fig_versoes_carro_2.png}
    \caption{Versões disponíveis para o Hyundai Creta, retornadas pela API.}
    \label{fig:versoes_carro_2}
\end{figure}

Com os dados de ambos os veículos validados, o workflow do N8N aciona o 'HTTP Request IA chat', que por sua vez consulta a API do backend (`/api/dados_para_ia`) para obter um contexto estruturado com as especificações detalhadas dos carros. Este contexto é então passado para o nó 'AI Agent' (\textbf{Figura \ref{fig:node_chatbot}}), que utiliza o 'Google Gemini Chat Model' para gerar uma resposta inteligente e comparativa com base nas informações fornecidas.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Imagens/fig_node_chatbot.png}
    \caption{Nós 'AI Agent' e 'Google Gemini Chat Model' no workflow do N8N.}
    \label{fig:node_chatbot}
\end{figure}

O resultado do processamento da IA é uma mensagem de texto comparativa, pronta para ser enviada ao usuário. A \textbf{Figura \ref{fig:resposta}} mostra o output gerado, que neste caso compara o impacto ambiental do Hyundai Creta e do Jeep Renegade.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Imagens/fig_resposta.png}
    \caption{Resposta comparativa gerada pela IA, pronta para envio via WhatsApp.}
    \label{fig:resposta}
\end{figure}

O histórico de execuções do N8N, como ilustrado na \textbf{Figura \ref{fig:lista_requisicoes}}, confirma que todas as etapas do workflow foram executadas com sucesso, culminando na geração da resposta pela IA.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.5\linewidth]{Imagens/fig_lista_requisicoes.png}
    \caption{Lista de execuções bem-sucedidas do workflow no N8N.}
    \label{fig:lista_requisicoes}
\end{figure}

\paragraph{Conclusão do Estudo de Caso:} Este estudo de caso demonstra a capacidade do assistente conversacional via WhatsApp em processar comparações diretas de veículos. Ao coletar entradas do usuário, interagir com a API de backend para validação e obtenção de dados detalhados, e utilizar a inteligência artificial para gerar respostas comparativas, o sistema valida sua funcionalidade central. A geração bem-sucedida da mensagem pela IA, confirmada pelos outputs do N8N, atesta que o sistema é capaz de fornecer análises inteligentes e concisas para usuários móveis, destacando a agilidade do canal para tomadas de decisão rápidas.
