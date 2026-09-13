# serverbedrockADDOS

Eu fiz isto para ajudar a colocar num servidor os ADDONS PAIXE O SERVIDOR

https://www.minecraft.net/pt-br/download/server/bedrock

EU ACHEI MUITO LINDO OS DELA E DO NAMORADO DELA EM FIM TA I O LINK 

https://www.instagram.com/muranguete.oficiall/reels/

<img width="1845" height="903" alt="image" src="https://github.com/user-attachments/assets/58b39331-140a-4839-94de-79aea4abe5ea" />

🟩 Creeper Add-on Manager — Bedrock Server
O Creeper Add-on Manager é uma ferramenta gráfica em Python (Tkinter) desenvolvida para automatizar a gestão, ativação e remoção de Behavior Packs e Resource Packs em servidores de Minecraft Bedrock Edition.

<img width="1350" height="616" alt="Captura de tela de 2026-09-13 16-56-20" src="https://github.com/user-attachments/assets/4a6b4fa1-5f6e-41d0-b063-dfda89ca347f" />


A ferramenta lê dinamicamente os arquivos manifest.json das pastas de pacotes, extrai os UUIDs e versões corretas, e sincroniza as alterações tanto no índice global (valid_known_packs.json) quanto nas configurações do mundo (world_behavior_packs.json e world_resource_packs.json).

🚀 Funcionalidades
🎨 Interface Temática Terminal/Creeper: Estilo retrofuturista em preto e verde-limão com alertas integrados no mesmo tema.

🔍 Suporte a Busca por Coringa (*): Não precisa digitar o nome exato da pasta — selecione na lista ou digite termos parciais para localizar os pacotes.

📦 Modo Duplo (BP & RP): Ative ou remova Behavior Packs e Resource Packs simultaneamente ou individualmente.

📝 Manutenção Automática de UUID e Versão: Lê as metadados do manifest.json sem necessidade de edição manual de JSON.

⚙️ Contagem Exata de Arquivos Alterados: Ao adicionar ou remover um pacote, o gerenciador relata precisamente quantos arquivos de configuração do servidor foram atualizados no disco.

🗂️ Estrutura de Pastas Esperada
Para que a ferramenta funcione corretamente, execute o script na raiz da pasta do seu servidor Bedrock:

Plaintext
meu_servidor_bedrock/
├── conf.py
├── valid_known_packs.json
├── behavior_packs/
│   └── meu_behavior_pack/
│       └── manifest.json
├── resource_packs/
│   └── meu_resource_pack/
│       └── manifest.json
└── worlds/
    └── Bedrock level/
        ├── world_behavior_packs.json
        └── world_resource_packs.json
📦 Requisitos e Instalação
Python 3.8+

Módulo Tkinter (já incluído no instalador padrão do Python no Windows).

Não há necessidade de instalar dependências externas via pip.

💻 Como Usar
Execute o script:

Bash
python conf.py
Interface e Opções:

Pasta do Mundo: Digite o nome da pasta do seu mundo presente no diretório worlds/ (Padrão: Bedrock level).

Behavior Pack / Resource Pack: Selecione um pacote na caixa de seleção ou digite parte do nome da pasta.

[ + ] ADICIONAR / ATIVAR: Lê o manifest.json do pacote selecionado, insere o registro no valid_known_packs.json e ativa no mundo em world_*.json.

[ X ] REMOVER PACOTE: Desativa o pacote do mundo e remove suas referências do arquivo valid_known_packs.json.

🔄 RECARREGAR LISTA DE PASTAS: Atualiza as opções dos menus caso você tenha adicionado novas pastas ao servidor enquanto o programa estava aberto.

📜 Licença e Créditos
Desenvolvido por Amauri Bueno dos Santos com apoio da Gemini.

Repositório: github.com/Annabel369/2FA

Copyright: 2025-2026

serverbedrockADDOS Minecraft
