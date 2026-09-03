# Guia — Subir o CaixaLivre no GitHub

> Passo a passo para o CP1, escrito para quem nunca usou Git/GitHub.
> Cada passo tem **o comando**, **o que ele faz** e **como saber que deu certo**.
>
> A ordem importa. Não pule a Parte 3 (`.gitignore`) — ela vem antes do primeiro
> commit por um motivo sério, explicado lá.

---

## Como usar este guia em outro chat

Abra um chat novo e cole o bloco abaixo como **primeira mensagem**. Ele dá ao
assistente todo o contexto necessário, para você não ter que reexplicar nada.

```
Sou estudante da FIAP e estou entregando o CP1 de um projeto de backend.
Nunca usei Git nem GitHub de verdade e QUERO APRENDER FAZENDO — então me
guie um passo de cada vez, esperando eu confirmar antes de seguir.
Não me dê o guia inteiro de uma vez.

Meu ambiente (já verificado, não precisa checar de novo):
- Windows 11, terminal PowerShell
- Git 2.53.0 instalado
- user.name = Vitoriinoo | user.email = vtvitoriinoo@gmail.com (já configurados)
- Git Credential Manager instalado
- Python 3.14.3
- GitHub CLI (gh) NÃO instalado
- Sem chave SSH
- A pasta do projeto AINDA NÃO é um repositório git

Pasta do projeto (tem espaços e acento — sempre usar aspas):
C:\Users\vitor\OneDrive\FIAP\CPs\Python\CF - CP Léo

Dentro dela existe só uma pasta docs/ com 4 arquivos .md.
O código do backend (Python + FastAPI + PostgreSQL) ainda será escrito.

Vou te mandar o guia que estou seguindo. Me ajude a executar a Parte X.
Quando eu colar um erro, me explique o que ele significa antes de dar a solução.
```

Depois disso, cole o guia (ou só a parte que você está fazendo) e diga:
*"vamos para a Parte 1"*.

---

## O que já está pronto na sua máquina

Verificado em 03/09/2026 — não precisa refazer nada disto.

| Item | Situação |
|---|---|
| Git | ✅ instalado (2.53.0) |
| Nome e e-mail do Git | ✅ configurados |
| Git Credential Manager | ✅ instalado (é ele que faz o login pelo navegador) |
| Python | ✅ 3.14.3 |
| GitHub CLI (`gh`) | ❌ não instalado — **não é obrigatório**, este guia não usa |
| Chave SSH | ❌ não existe — **não é obrigatório**, vamos usar HTTPS |
| Repositório git na pasta | ❌ ainda não existe — é a Parte 2 |

---

## Sete conceitos, em uma linha cada

Leia uma vez. O resto do guia faz mais sentido depois.

- **Repositório (repo)** — uma pasta que o Git vigia. Ele guarda o histórico de tudo que muda dentro dela.
- **Commit** — uma foto do projeto num instante, com uma mensagem explicando o que mudou. É a unidade do histórico.
- **Staging (`git add`)** — a mesa onde você separa o que vai entrar no próximo commit. Nem tudo que você alterou precisa entrar junto.
- **Remote (`origin`)** — o endereço do repositório no GitHub. `origin` é só o apelido padrão dele.
- **Push** — mandar seus commits da máquina para o GitHub. **Pull** — trazer os commits dos outros para a sua máquina.
- **Branch** — uma linha de trabalho paralela. Você mexe nela sem quebrar a `main`.
- **Pull Request (PR)** — o pedido de juntar sua branch na `main`, com espaço para outra pessoa revisar antes.

---

## Cinco regras de ouro

1. **`.env` nunca vai para o GitHub.** Ele guarda a senha do banco. Repositório do CP1 é público — senha commitada é senha vazada. E apagar depois não resolve: fica no histórico.
2. **Commit pequeno e frequente**, com mensagem que diga o que mudou. `"CRUD de contas"` é útil; `"att"` não é.
3. **`git pull` antes de começar a trabalhar**, todo dia. Evita 90% dos conflitos.
4. **Nunca use `git push --force`.** Ele apaga o trabalho dos outros no servidor.
5. **Na dúvida, `git status`.** Ele é gratuito, não muda nada e quase sempre já responde a sua pergunta.

---

## Parte 0 — Dois ajustes, uma vez só

```bash
git config --global init.defaultBranch main
```

**O que faz:** manda o Git chamar a primeira branch de `main`. Sem isso ele usa
`master`, enquanto o GitHub espera `main` — e você acaba com duas branches
diferentes e um push que não sobe.

```bash
git config --global credential.helper manager
```

**O que faz:** liga o Git Credential Manager. É o que abre a janela do navegador
para você fazer login no GitHub no primeiro push, em vez de pedir senha no
terminal (senha no terminal, aliás, o GitHub não aceita mais).

**Como saber que deu certo:** rode `git config --global --list` e procure as duas
linhas `init.defaultbranch=main` e `credential.helper=manager`.

---

## Parte 1 — Criar o repositório no GitHub

Isto é no site, não no terminal.

1. Entre em [github.com](https://github.com) e faça login (ou crie a conta com o e-mail `vtvitoriinoo@gmail.com`).
2. Botão **+** no canto superior direito → **New repository**.
3. Preencha:
   - **Repository name:** `caixalivre-api`
   - **Description:** `Gestão financeira para autônomos, freelancers e MEIs — backend FastAPI (CP1)`
   - **Public** ✅ — o professor precisa abrir sem convite.
   - **Add a README file** ❌ **desmarque**
   - **Add .gitignore** ❌ **desmarque**
   - **Choose a license** ❌ deixe em None
4. **Create repository**.

> **Por que desmarcar tudo:** se o GitHub criar arquivos, o repositório de lá
> nasce com um commit que a sua máquina não tem. Aí o primeiro push é recusado
> com um erro (`rejected — fetch first`) que confunde muito quem está começando.
> Nascendo vazio, o push funciona de primeira.

Na tela seguinte o GitHub mostra uma URL parecida com:

```
https://github.com/SEU-USUARIO/caixalivre-api.git
```

**Copie essa URL.** Você vai usá-la na Parte 5.

---

## Parte 2 — Transformar a pasta em repositório

Abra o **PowerShell** e entre na pasta. As aspas são obrigatórias: o caminho tem
espaços e um acento em "Léo".

```bash
cd "C:\Users\vitor\OneDrive\FIAP\CPs\Python\CF - CP Léo"
```

```bash
git init
```

**O que faz:** cria uma pasta oculta `.git` dentro do projeto. É nela que mora
todo o histórico. A sua pasta continua igual; o Git só passa a observá-la.

**Como saber que deu certo:** aparece `Initialized empty Git repository in ...`.
Confirme com:

```bash
git status
```

Deve listar `docs/` em vermelho, sob **Untracked files** — arquivos que o Git
enxerga mas ainda não acompanha. É exatamente o esperado agora.

---

## Parte 3 — `.gitignore` (antes do primeiro commit)

**Esta parte vem antes do commit de propósito.** Uma vez que um arquivo entra num
commit, ele fica no histórico para sempre — apagar depois não o remove do
passado. É mais fácil impedir a entrada do que remover depois.

Crie um arquivo chamado `.gitignore` na **raiz** do projeto (não dentro de
`docs/`), com este conteúdo:

```
# Ambiente e segredos
.env
.env.local
*.env
!.env.example

# Ambiente virtual Python
venv/
.venv/
env/

# Cache do Python
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.mypy_cache/

# Banco local
*.db
*.sqlite3

# Editores
.vscode/
.idea/

# Sistema
Thumbs.db
desktop.ini
```

Duas linhas que merecem explicação:

- **`.env` bloqueado, `!.env.example` liberado.** O `!` é uma exceção: aquele
  arquivo específico *pode* subir. É a convenção — `.env.example` mostra ao
  professor e aos colegas **quais** variáveis existem, com valores falsos, sem
  entregar as reais. O barema pede "configuração das variáveis de ambiente" no
  README; é este arquivo que dá sentido àquela seção.
- **`desktop.ini`** é lixo que o OneDrive espalha pelas pastas. Sem essa linha
  ele aparece no `git status` e polui todo commit.

**Como saber que deu certo:** rode `git status`. O `.gitignore` deve aparecer na
lista, e nada de `venv/` ou `.env` deve estar lá.

---

## Parte 4 — Primeiro commit

```bash
git add .
```

**O que faz:** coloca na mesa (staging) todos os arquivos novos e modificados,
respeitando o `.gitignore`. O `.` significa "tudo desta pasta para baixo".

```bash
git status
```

**Confira antes de commitar.** Os arquivos agora aparecem em verde. Você deve ver
`.gitignore` e os 4 arquivos de `docs/`. **Se aparecer `.env` ou `venv/`, pare** —
o `.gitignore` está no lugar errado ou com erro de digitação. Resolva antes de
seguir.

```bash
git commit -m "Documentacao inicial: escopo, regras de negocio e planejamento"
```

**O que faz:** grava a foto do projeto com essa mensagem. O `-m` é a mensagem.

**Como saber que deu certo:** aparece algo como `[main (root-commit) a1b2c3d] ...`
com a contagem de arquivos. Rode `git log --oneline` e veja seu commit listado.

> **Neste commit você já resolve um problema real do CP1.** Seus documentos de
> escopo e regras de negócio valem 3,0 pontos do barema, mas hoje só existem no
> seu computador — o professor não avalia o que não consegue abrir. A partir do
> push da Parte 5, eles viram entregável.

---

## Parte 5 — Conectar ao GitHub e enviar

Use a URL que você copiou na Parte 1, trocando `SEU-USUARIO`:

```bash
git remote add origin https://github.com/SEU-USUARIO/caixalivre-api.git
```

**O que faz:** guarda o endereço do GitHub sob o apelido `origin`. Nada é enviado
ainda — é só o cadastro do destino.

**Confira:**

```bash
git remote -v
```

Deve mostrar a URL duas vezes, marcada `(fetch)` e `(push)`.

```bash
git push -u origin main
```

**O que faz:** envia seus commits para o GitHub. O `-u` cria o vínculo entre a sua
`main` local e a `main` do servidor — por causa dele, daqui para frente basta
`git push`, sem o resto.

**O login:** vai abrir uma janela do navegador pedindo autorização do GitHub.
Aceite. Isso acontece **uma vez só**; o Credential Manager guarda a credencial.
Se nenhuma janela abrir, veja a Parte 9.

**Como saber que deu certo:** recarregue a página do repositório no GitHub. A
pasta `docs/` está lá.

---

## Parte 6 — Adicionar a Thainá e o Silvio

No GitHub, dentro do repositório:

**Settings** → **Collaborators** → **Add people** → usuário do GitHub de cada um
→ eles recebem um convite por e-mail e **precisam aceitar**.

Sem aceitar o convite, eles conseguem baixar (o repo é público) mas **não
conseguem dar push**. Se alguém reclamar de `403` no push, é quase sempre isso.

Para eles baixarem o projeto pela primeira vez, na pasta onde quiserem guardar:

```bash
git clone https://github.com/SEU-USUARIO/caixalivre-api.git
```

`clone` é o `init` + `remote add` + download, tudo de uma vez. Só se faz uma vez
por máquina.

---

## Parte 7 — O ciclo do dia a dia

Estes quatro comandos são 95% do seu uso de Git. Decore este ciclo.

**Ao sentar para trabalhar:**

```bash
git pull
```

Traz o que a Thainá e o Silvio enviaram. Fazer isso *antes* de mexer em qualquer
coisa é o que evita conflito.

**Depois de trabalhar:**

```bash
git status
```

Mostra o que você mudou. Leia antes de adicionar — é o hábito que evita commitar
coisa errada.

```bash
git add .
git commit -m "CRUD de contas com validacao de saldo"
```

**Sobre a mensagem:** escreva o que mudou, no presente, sem ponto final.
`"Adiciona endpoint GET /resumo"` é bom. `"mudanças"`, `"att"`, `"teste"` não
ajudam ninguém — inclusive você daqui a três dias.

```bash
git push
```

Envia. Curto assim porque o `-u` da Parte 5 já vinculou a branch.

---

## Parte 8 — Branches e Pull Requests

Você pode entregar o CP1 commitando tudo direto na `main`. Funciona. Mas com três
pessoas mexendo no mesmo backend, uma branch por tarefa evita que o código
quebrado de um derrube o dos outros — e o PR dá ao professor uma evidência
visível de revisão cruzada, que é justamente a regra que vocês escreveram no
`docs/TRELLO.md`.

**Criar uma branch para a tarefa:**

```bash
git checkout -b feature/crud-contas
```

**O que faz:** cria a branch e já muda para ela (`-b` = *branch*, criar). O nome
`feature/` na frente é convenção, não obrigação.

Trabalhe normalmente: `git add`, `git commit`. Para enviar a branch nova pela
primeira vez:

```bash
git push -u origin feature/crud-contas
```

**Abrir o PR:** vá ao repositório no GitHub. Aparece uma faixa amarela
*"Compare & pull request"*. Clique, escreva o que a branch faz, e **Create pull
request**. Peça a um colega para revisar e clicar em **Merge**.

**Depois do merge, volte para a main e atualize:**

```bash
git checkout main
git pull
```

**Comandos úteis de branch:**

```bash
git branch          # lista as branches; a atual tem um *
git checkout main   # muda para a main
```

---

## Parte 9 — Erros comuns

| Erro que aparece | O que significa | O que fazer |
|---|---|---|
| `fatal: not a git repository` | Você não está na pasta do projeto | `cd "C:\Users\vitor\OneDrive\FIAP\CPs\Python\CF - CP Léo"` |
| `Updates were rejected... fetch first` | Alguém enviou algo que você não tem | `git pull` e depois `git push`. **Nunca** `--force` |
| `Authentication failed` | Login não passou | `git config --global credential.helper manager` e tente o push de novo |
| `Please tell me who you are` | Nome/e-mail não configurados | Já estão na sua máquina — só acontece em máquina nova |
| `src refspec main does not match any` | Você ainda não fez nenhum commit | Faça a Parte 4 antes do push |
| `error: failed to push some refs` | Quase sempre o mesmo caso do `fetch first` | `git pull` primeiro |
| `CONFLICT (content): Merge conflict in X` | Você e outra pessoa mudaram a mesma linha | Veja o quadro abaixo |
| Nada acontece / trava numa tela estranha | Abriu o editor `vim` pedindo mensagem | Tecle `Esc`, digite `:wq` e `Enter`. Para evitar, sempre use `-m "mensagem"` |

**Resolvendo um conflito.** O Git marca o arquivo assim:

```
<<<<<<< HEAD
o que está na SUA versão
=======
o que veio do GitHub
>>>>>>> main
```

Abra o arquivo, decida qual texto fica (ou junte os dois), **apague as três linhas
de marcação** `<<<<<<<`, `=======` e `>>>>>>>`, salve. Depois:

```bash
git add .
git commit -m "Resolve conflito em X"
git push
```

Não tem mágica nem comando especial: conflito se resolve editando o arquivo à mão.

---

## Parte 10 — Antes de entregar

Faça isto no dia 07/09, não no dia 08.

- [ ] O repositório abre em aba anônima do navegador (ou seja: está mesmo público)
- [ ] `.env` **não** aparece na listagem de arquivos do GitHub
- [ ] `.env.example` **aparece**, com as variáveis e valores falsos
- [ ] `README.md` na raiz, com os 14 itens que o professor pediu
- [ ] Link do Swagger e link do Trello dentro do README
- [ ] `docs/` com escopo, regras de negócio e DER
- [ ] Os três integrantes aparecem em **Insights → Contributors** com commits próprios
- [ ] `git status` responde `nothing to commit, working tree clean`
- [ ] Você clonou o repo numa pasta nova e conseguiu subir o projeto só seguindo o README

O último item é o mais importante e o mais esquecido: **é literalmente o que o
professor vai fazer.** Se não subir seguindo só o README, o README está errado.

---

## Dois avisos sobre a sua máquina

**1. O projeto está dentro do OneDrive.** Git e OneDrive sincronizando a mesma
pasta `.git` às vezes brigam. Para um projeto pequeno de 5 dias, na prática
funciona. Mas se aparecer erro esquisito de arquivo travado ou `.git/index.lock`,
pause a sincronização do OneDrive (ícone da nuvem na barra de tarefas → engrenagem
→ Pausar sincronização), rode o comando de novo e retome depois.

**2. Você está no Python 3.14.3, mas o `docs/TRELLO.md` planejou 3.12.** Nada a
ver com Git, mas pode travar vocês na hora de instalar as dependências: pacotes
com código compilado — `psycopg2-binary` é o suspeito de sempre — costumam
demorar a publicar versão para um Python recém-lançado. Se o `pip install` falhar
com erro de compilação, troque para `psycopg[binary]` ou instale o Python 3.12 ao
lado. Vale testar isso **hoje**, não no dia 7.

---

## Cola de comandos

```bash
git status                      # o que mudou (use o tempo todo)
git add .                       # separa tudo para o commit
git commit -m "mensagem"        # grava a foto
git push                        # envia para o GitHub
git pull                        # traz o dos outros
git log --oneline               # histórico resumido
git branch                      # lista branches
git checkout -b nome            # cria e entra numa branch
git checkout main               # volta para a main
git remote -v                   # mostra o endereço do GitHub
git diff                        # mostra linha a linha o que você mudou
```
