# Guia de Implantação no AWS Academy Sandbox

Este documento fornece um passo a passo prático e simplificado para executar a aplicação de **Middleware ORB** no ambiente **AWS Academy Sandbox / Learner Lab** (acessível via *Módulos > Sandbox > Ambiente de sandbox*).

---

## 🎯 Por que usar EC2 + Docker Compose na AWS Academy?

No ambiente Sandbox da AWS Academy, os alunos possuem permissões limitadas para criar roles de IAM ou VPCs personalizadas. **Usar uma instância EC2 rodando Docker Compose** é a estratégia mais recomendada por ser:
1. **100% suportada** no limite de créditos da AWS Academy.
2. **Idêntica ao ambiente local**, garantindo que não haverá erros de compatibilidade.
3. **Rápida de configurar** (leva menos de 5 minutos).

---

## 🚀 Passo a Passo de Execução

### Passo 1: Iniciar o Sandbox na AWS Academy
1. Acesse o AVA (Canvas/Moodle) da sua instituição.
2. Vá em **Módulos** > **Sandbox** > **Ambiente de sandbox** (ou *Learner Lab*).
3. Clique no botão **Start Lab** (aguarde o indicador de status ficar verde `● AWS`).
4. Clique em **AWS** (ao lado do indicador verde) para abrir o Console de Gerenciamento da AWS em uma nova aba.

---

### Passo 2: Criar a Instância EC2
1. No Console AWS, busque por **EC2** na barra de pesquisa superior.
2. Clique em **Executar Instância** (*Launch Instance*).
3. Configure os campos com os seguintes valores:
   * **Nome da Instância:** `ORB-Biblioteca-SD`
   * **Imagem (AMI):** `Ubuntu Server 24.04 LTS` (Elegível para o nível gratuito).
   * **Tipo de Instância:** `t2.micro` ou `t3.micro`.
   * **Par de Chaves (Key Pair):** Selecione *Continuar sem um par de chaves* (*Proceed without a key pair*).
4. **Configurações de Rede (Security Group):**
   * Clique em **Editar** ao lado de *Configurações de rede*.
   * Mantenha a regra padrão de SSH (Porta 22).
   * Adicione as 4 regras de entrada (*Inbound Security Group Rules*) abaixo:

| Tipo | Protocolo | Intervalo de Portas | Origem | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| TCP Personalizado | TCP | `8765` | `0.0.0.0/0` | Registry Service (Naming) |
| TCP Personalizado | TCP | `9001` | `0.0.0.0/0` | Nó 1 de Servidor ORB |
| TCP Personalizado | TCP | `9002` | `0.0.0.0/0` | Nó 2 de Servidor ORB |
| TCP Personalizado | TCP | `8000` | `0.0.0.0/0` | API Administrativa (Swagger) |

5. Clique em **Executar Instância** (*Launch Instance*).

---

### Passo 3: Conectar à Instância EC2
1. Vá para o painel de **Instâncias** no EC2.
2. Selecione a instância `ORB-Biblioteca-SD` recém-criada.
3. Clique em **Conectar** (*Connect*) no menu superior.
4. Selecione a opção **EC2 Instance Connect** e clique em **Conectar**. Um terminal Linux será aberto diretamente no navegador.

---

### Passo 4: Instalar Docker e Clonar o Projeto
No terminal do navegador na EC2, execute os comandos abaixo:

```bash
# 1. Atualizar os pacotes do sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar Git, Docker e Docker Compose
sudo apt install -y git docker.io docker-compose

# 3. Adicionar o usuário 'ubuntu' ao grupo do docker
sudo usermod -aG docker ubuntu

# 4. Iniciar o serviço do Docker
sudo systemctl enable --now docker
```

Em seguida, clone o seu repositório Git ou baixe os arquivos da aplicação:

```bash
# Substitua com a URL do seu repositório no GitHub
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git atividade_SD1
cd atividade_SD1
```

---

### Passo 5: Subir a Aplicação com Docker Compose
Dentro da pasta do projeto na EC2, configure o IP público da instância e suba os contêineres:

```bash
# 1. Configurar o IP público da EC2 para o Registry divulgar o nó correto
echo "PUBLIC_HOST=$(curl -s ifconfig.me)" > .env

# 2. Subir a aplicação
sudo docker compose up -d --build
```

Verifique se todos os contêineres subiram com sucesso:

```bash
sudo docker compose ps
```

---

### Passo 6: Testar e Demonstrar na Nuvem AWS

Copie o **Endereço IPv4 Público** da sua instância no painel EC2 da AWS (exemplo: `54.209.123.45`).

1. **Acessar a API Admin e Swagger no Navegador:**
   Abra no seu navegador:
   `http://<IP_PUBLICO_DA_EC2>:8000/docs`
   *(Você verá o Swagger da API Admin respondendo diretamente da nuvem AWS!)*

2. **Executar o Cliente Interativo (CLI) do seu computador conectando na AWS:**
   No seu terminal local (PowerShell ou Bash):
   ```powershell
   $env:REGISTRY_HOST="<IP_PUBLICO_DA_EC2>"
   python -m client.cli
   ```
   *(O seu computador se comunicará remotamente via TCP com os serviços rodando na AWS!)*

---

### 🛑 Passo 7: Encerrar o Lab (Ao finalizar)
Após apresentar o trabalho para o professor, volte à página da AWS Academy e clique em **End Lab** para encerrar a sessão e economizar os créditos do seu Sandbox.
