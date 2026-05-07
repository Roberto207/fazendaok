# Plataforma FazendaOk 🌱

Bem-vindo à **FazendaOk**, uma plataforma completa de diagnóstico de conformidade ambiental para propriedades rurais brasileiras. Ela foi desenvolvida para ajudar produtores a verificarem instantaneamente se suas propriedades estão aptas para obter crédito rural (regras MCR 2.9 / CMN 5.268).

Este guia tem tudo que você precisa saber para subir todo o ecossistema (banco de dados, filas assíncronas, API backend e interface frontend).

---

## 🏗 Arquitetura do Sistema

O projeto é dividido em múltiplas frentes, conteinerizadas via Docker para facilidade de deploy:
1. **Frontend (React)**: Onde o usuário informa o CAR (Cadastro Ambiental Rural) ou coordenadas e interage visualmente.
2. **Backend API (FastAPI)**: O cérebro da operação. Recebe os pedidos do Frontend, conecta a APIs externas (SICAR, Anthropic, AWS S3) e devolve respostas.
3. **Celery Worker**: Trabalhador assíncrono. Como processar polígonos e falar com IA demora alguns segundos, o Celery roda essas tarefas em *background* sem travar a API.
4. **Redis**: Banco de dados em memória que atua como *Message Broker* (filas de mensagens para o Celery) e também como cache de respostas.
5. **PostgreSQL + PostGIS**: Banco de dados robusto otimizado para lidar com dados espaciais (GeoJSON e shapefiles).

---

## 🚀 Como Rodar o Projeto (Passo a Passo)

### Passo 1: Preparando o ambiente (Configuração das variáveis)
Antes de rodar qualquer código, os serviços precisam de algumas senhas e chaves de API para funcionarem corretamente.

1. **Backend**:
   - Vá na raiz do projeto (`/dev/fazendaok/`).
   - Você verá um arquivo chamado `.env` (se não existir, crie-o usando o conteúdo do `.env.example`).
   - Certifique-se de que no mínimo a chave do Anthropic (`ANTHROPIC_API_KEY`) esteja presente. A conexão com o banco de dados e o redis já estão prontas para o Docker.

2. **Frontend**:
   - Vá para a pasta do frontend (`/dev/fazendaok/frontend/`).
   - Crie o arquivo `.env` (ou utilize o `.env.example`).
   - Insira o seguinte conteúdo (necessário para ele achar a API e carregar o Google Maps se necessário):
     ```env
     VITE_API_URL=http://localhost:8000/api/v1
     VITE_GOOGLE_MAPS_API_KEY=sua_chave_do_google_maps_aqui
     ```

### Passo 2: Subindo a Infraestrutura do Backend (Docker)
Deixamos toda a complexidade de banco de dados, filas e pacotes do Python resolvidas dentro de containers Docker.

1. Abra o terminal na **raiz do projeto** (`/dev/fazendaok`).
2. Rode o comando que constrói e sobe os containers em segundo plano (modo daemon `-d`):
   ```bash
   docker compose up -d --build
   ```
3. O Docker fará o download das imagens (Postgres, Redis, Python 3.12) e iniciará os seguintes serviços:
   - `fazendaok_db`: O banco de dados PostGIS rodando na porta 5432.
   - `fazendaok_redis`: O broker na porta 6379.
   - `fazendaok_api`: A API principal respondendo em `http://localhost:8000`.
   - `fazendaok_worker`: O trabalhador responsável pela análise de geoprocessamento.

> **Dica:** Para ver os logs da API em tempo real (ex: ver o diagnóstico acontecendo) use:  
> `docker logs -f fazendaok_api` e `docker logs -f fazendaok_worker`.

### Passo 3: Iniciando o Frontend
Com o backend já respondendo na porta 8000, agora iniciamos a interface visual (React).

1. Abra um **novo terminal** e vá para a pasta do frontend:
   ```bash
   cd /home/robertocaetano207/dev/fazendaok/frontend
   ```
2. Instale as dependências (necessário apenas na primeira vez):
   ```bash
   npm install
   ```
3. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```
4. O terminal mostrará um link (geralmente `http://localhost:5173`). Abra isso no seu navegador!

---

## 🎮 Testando na Prática (Fluxo do Usuário)

1. **Acessando**: No seu navegador (`http://localhost:5173`), você verá a Landing Page.
2. **Localização**: Clique em "Analisar Agora". Insira um número CAR (pode ser o CAR de teste) ou insira coordenadas. E envie algumas fotos se desejar (opcional).
3. **Análise Assíncrona**: Você verá a tela de "Processando...". O que está acontecendo por baixo dos panos?
   - O Frontend mandou para o FastAPI (`fazendaok_api`).
   - A API guardou no Postgres e mandou a missão para a fila do Redis.
   - O `fazendaok_worker` pegou a missão, calculou as sobreposições de área, pediu um parecer da inteligência artificial, e gerou o diagnóstico oficial em PDF.
   - Enquanto isso o frontend fica fazendo *polling* na API a cada 2 segundos perguntando "Já acabou?".
4. **Resultado**: Quando finalizado, você será redirecionado para o resultado da fazenda, mostrando o Risco, Badge, dados de hectares, parecer técnico da IA, e um botão que permite o download do laudo PDF oficial gerado na nuvem.
5. **Histórico**: Acessando a aba "Meu Histórico", você pode inserir o número do CAR e ver todos os diagnósticos atrelados a ele gravados no banco de dados.

---

## 🛠 Comandos Úteis do Dia a Dia

**Derrubar os serviços do backend:**
```bash
docker compose down
```

**Ver o banco de dados sendo preenchido no terminal:**
```bash
docker exec -it fazendaok_db psql -U postgres -d fazendaok
# Uma vez dentro do banco:
SELECT * FROM diagnosticos;
```

**Rodar migrações do banco (se criar novas tabelas no Python)**:
O Alembic garante que as tabelas estejam criadas automaticamente ao subir o sistema (configurado no código). Caso precise rodar manualmente de dentro do container:
```bash
docker exec -it fazendaok_api alembic upgrade head
```
