# Introdução
Nesse trabalho foi implementado um sistema peer-to-peer de acordo com a
especificação passada. O sistema implementa o cliente que informa os IDs dos arquivos
de vídeo desejados e o peer responsável por repassar a busca, informar o cliente os arquivos
que possui dentre os desejados e enviar os arquivos solicitados através do protocolo UDP sem
verificação de falhas, já que se pode assumir que não se perde pacotes. Foram executados
testes no mininet de confirmar o desempenho esperado com sucesso.

# Arquitetura
Como falado antes, o sistema foi implementado em Python 3 fazendo uso de
apenas as bibliotecas básicas listadas abaixo que não exigem instalação:
* socket – utilizada para transmissão de dados via protocolo UDP.
* os – utilizada para ler o tamanho de cada chunk.
* sys – utilizada para ler os argumentos da chamada do sistema.

Na implementação optou-se por nomear as variáveis e funções da maneira mais
descritiva possível mesmo que os nomes ficassem grandes de maneira a facilitar o
entendimento do código e diminuir a necessidade de comentários, que ainda podem
ser encontrados no código tentou-se aplicar muitos dos conceitos de código limpo.
Não foram utilizadas aqui os conceitos de programação orientada a objeto e o código
está dividido em 3 arquivos (common.py, cliente.py e peer.py) que são examinados
abaixo.

# common.py
Responsável pela declaração das constantes e das funções auxiliares utilizadas pelo
cliente e pelo peer, todas as funções possuem dotstrings com um breve resumo do
seu funcionamento e são listadas abaixo:
* encript_message(*args) - Responsável por receber um conjunto de variáveis
que podem ser do tipo inteiro ou array de bytes contidos em listas ou não e
retornar um array de bytes com essas informações concatenadas. Todos os
valores inteiros recebidos são convertidos para 2 bytes.
* get_type_of_message(message) - Essa função recebe uma mensagem e
retorna o tipo dela de acordo com o dicionário MESSAGES onde cada
mensagem pode ser do tipo HELLO, QUERY, CHUNK INFO, GET e
RESPONSE.
* decode_position(message, position) - Essa função decodifica uma posição da
mensagem com 2 bytes para um valor inteiro que é retornado. A função
assume que 0 corresponde ao início da mensagem e anda de 2 em 2 de
maneira que o valor 1 corresponde ao valor 2 na mensagem, o valor 2 à
posição 4 e assim por diante.
* generate_chunk_array_info(message, id_list) - Essa é uma função utilizada
apelas pelo peer para, diante de uma mensagem do tipo HELLO ou QUERY,
gerar uma lista com os ids que o peer possui que foram solicitados pelo cliente.
* convert_address_to_byte_list(address) - Essa função é utilizada apenas pelo
peer para auxiliá-lo a montar a QUERY após ter recebido uma mensagem do
tipo HELLO. Essa função recebe uma tupla com o ip e porto do cliente e
converte para um array de bytes onde o ip tem tamanho 4 e a porta tem
tamanho 2.
* extract_client_address_from_query(message) - Outra função utilizada apenas
pelo peer ao receber uma QUERY, essa função extrai o IP e porto do cliente e
o retorna como uma tupla.
* get_ttl_and_update_message(message) - Função também utilizada pelo peer
ao receber uma QUERY, responsável por decrementar em um o TTL da
mensagem e retornar o valor do TTL atualizado junto com a nova mensagem.

# cliente.py
O cliente utiliza as bibliotecas sys e socket citadas anteriormente além das funções e
constantes declaradas em common.py. A sua chamada tem o formato abaixo:

python3 <path>/cliente.py <peer ip>:<peer port> <chunk ids>

Como no exemplo abaixo:

python3 ~/tp/cliente.py 10.0.0.1:5001 1,3,5,8

Inicialmente o cliente irá processar as entradas que devem estar de acordo com o
padrão citado acima, cria um socket UDP e então envia uma mensagem de HELLO
para o peer informado na sua chamada. Na sequência ele aguarda todos CHUNKS
INFOS esvaziando o chunks_needed_list à medida que recebe essas informações e
salvando as informações necessárias para solicitar os chunks posteriormente em
chunks_to_ask. O cliente não envia nenhum GET enquanto não receber todos o
CHUNK INFO ou o atingir o timeout de 5 segundos do socket.

Em seguida o cliente envia todas as solicitações do tipo GET para os devidos
peers e finalmente aguarda todas as mensagens de RESPONSE e salva cada arquivo
recebido com o nome Chunk_received_<ID>.m4s. À medida que recebe as respostas,
as devidas informações (<peer ip>:<porto> - <id>) são salvas no arquivo output-
<IP>.log com as informações dos arquivos faltantes ao final. Todos os arquivos são
salvos na pasta corrente da chamada do sistema.

# peer.py
O peer começa a ser executado de maneira semelhante ao cliente, utiliza as
bibliotecas sys, os e socket citadas anteriormente além das funções e constantes
declaradas em common.py. A sua chamada tem o formato abaixo:

python3 <path>/cliente.py <peer ip>:<peer port> <key values files file>
<known peers address>

Como no exemplo abaixo:

python3 ~/tp/peer.py 10.0.0.1:5001 key-values-files_peer1 10.0.0.2:5002
10.0.0.3:5003

Após processar os parâmetros fornecidos na chamada que deve estar no formato
acima o peer cria um socket UDP sem timeout e fica aguardando alguma mensagem
e tem a reação listada abaixo para cada tipo de mensagem.
* HELLO – Inicialmente o gera a mensagem de QUERY e a encaminha para os
clientes conhecidos e então verifica se possui ao menos um dos chunks
desejados pelo cliente para assim enviar par o mesmo uma mensagem do tipo
CHUNK INFO.
* QUERY – Primeiro ´e gerada uma nova mensagem com o TTL decrementado
e, caso seja maior que 0, essa nova mensagem é enviada para todos os peers
conhecidos à exceção daquele que lhe enviou essa mensagem. Por fim verifica
se possui ao menos um dos chunks desejados pelo cliente para assim enviar
par o mesmo uma mensagem do tipo CHUNK INFO.
* GET – Nesse caso o peer verifica a quantidade de chunks solicitados, localiza
cada um e os envia para o cliente.

# Conclusão
Nesse trabalho foi possível aprender muito sobre como fazer um sistema na camada
de aplicação e o uso das camadas inferiores.O sistema foi executado no mininet de
acordo com o exemplo exibido na especificação que conforme o exemplo mostrado
na especificação do trabalho cuja chamada é exibida no apêndice ao final deste
documento. O resultado ocorreu conforme esperado e os arquivos de log de cada
cliente foram listados também no apêndice. Por falta de tempo não foi possível
implementar o tratamento de erros tanto de entrada quanto de ausência de resposta
ao HELLO e GET, apesar de saber o conceito como implementá-los
