# Arquitetura base da aplicação

```bash
backend/
├── app/
│   ├── main.py               # Ponto de entrada da aplicação
│   ├── config.py             # Configurações gerais (ex.: conexão com BD, variáveis de ambiente)
│   ├── api/
│   │   └── endpoints/
│   │       ├── auth.py       # Endpoints de autenticação (login, logout, me)
│   │       └── teams.py      # Endpoints para gerenciamento de times (lista, criação, convite, remoção)
│   ├── core/
│   │   └── security.py       # Funções para hash, verificação de senha e criação/validação de tokens JWT
│   ├── crud/
│   │   ├── user.py           # Operações CRUD para usuários
│   │   └── team.py           # Operações CRUD para times
│   ├── db/
│   │   ├── base.py           # Base para os modelos SQLAlchemy
│   │   └── session.py        # Configuração da sessão do SQLAlchemy
│   ├── models/
│   │   ├── user.py           # Modelo User (inspirado na migração do Laravel)
│   │   └── team.py           # Modelo Team (idem)
│   └── schemas/
│       ├── auth.py           # Esquemas para autenticação (login, token)
│       ├── user.py           # Esquemas para usuários
│       └── team.py           # Esquemas para times
├── requirements.txt          # Dependências do projeto

```

# Para migrar executar esses comandos, de gerar nova versão, e subir a versão

```bash
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

# To copy the code in pieces slipt by the current folder
```sh
find ./app -name "*.py" -type f -print0 -o -name "*.md" -type f -print0 -o -name "*.txt" -type f -print0 -o -name "*.yaml" -type f -print0 -o -name "*.sh" -type f -print0 -o -name "*.env.example" -type f -print0 -o -name "*.Dockerfile" -type f -print0 | while IFS= read -r -d '' file; do echo "--- Conteúdo do arquivo: $file ---" >> todos-arquivos.mda; done
```