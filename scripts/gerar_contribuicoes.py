import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path

import requests
from dotenv import load_dotenv
load_dotenv()

arquivo_autores = Path("config/autores.json")

if arquivo_autores.exists():
    with arquivo_autores.open("r", encoding="utf-8") as arquivo:
        autores = json.load(arquivo)
else:
    autores = {}


def buscar_pull_requests():
    repositorio = os.environ.get("GITHUB_REPOSITORY")

    if not repositorio:
        print("GITHUB_REPOSITORY não foi definido.")
        return []

    url = f"https://api.github.com/repos/{repositorio}/pulls"

    resposta = requests.get(
        url,
        params={
            "state": "all",
            "per_page": 100
        },
        timeout=30
    )

    resposta.raise_for_status()

    return resposta.json()

def buscar_issues():
    repositorio = os.environ.get("GITHUB_REPOSITORY")

    if not repositorio:
        print("GITHUB_REPOSITORY não foi definido.")
        return []

    url = f"https://api.github.com/repos/{repositorio}/issues"

    resposta = requests.get(
        url,
        params={
            "state": "all",
            "per_page": 100
        },
        timeout=30
    )

    resposta.raise_for_status()

    return [
        issue
        for issue in resposta.json()
        if "pull_request" not in issue
    ]

resultado = subprocess.run(
    [
        "git",
        "log", #consulta o histórico de commits
        "--all", #todas as branchs
        "--format=AUTHOR|%an|%ae", #infos do commit 
        "--numstat" 
    ],
    capture_output=True,
    text=True,
    check=True
)

#print("Resultado recebido pelo Python:")
#print(resultado.stdout)


contribuicoes = defaultdict(
    lambda: {
        "commits": 0,
        "adicionadas": 0,
        "removidas": 0,
        "pull_requests": 0,
        "issues": 0
    }
)


pessoa_atual = None


for linha in resultado.stdout.splitlines():
    if linha.startswith("AUTHOR|"):
        partes = linha.split("|", maxsplit=2)

        nome = partes[1]
        email = partes[2]

        pessoa_atual = autores.get(email, nome)

        contribuicoes[pessoa_atual]["commits"] += 1

    elif pessoa_atual and linha.strip():
        partes = linha.split()

        if len(partes) < 3:
            continue

        adicionadas = partes[0]
        removidas = partes[1]

        if adicionadas.isdigit():
            contribuicoes[pessoa_atual]["adicionadas"] += int(adicionadas)

        if removidas.isdigit():
            contribuicoes[pessoa_atual]["removidas"] += int(removidas)


pull_requests = buscar_pull_requests()

for pull_request in pull_requests:
    autor = pull_request["user"]["login"]

    contribuicoes[autor]["pull_requests"] += 1

issues = buscar_issues()

for issue in issues:
    autor = issue["user"]["login"]
    contribuicoes[autor]["issues"] += 1


def atualizar_readme(contribuicoes):
    caminho_readme = Path("README.md")

    if not caminho_readme.exists():
        print("README.md não encontrado.")
        return

    inicio = "<!-- CONTRIBUTIONS_START -->"
    fim = "<!-- CONTRIBUTIONS_END -->"

    conteudo = caminho_readme.read_text(encoding="utf-8")

    if inicio not in conteudo or fim not in conteudo:
        print("Marcadores de contribuições não encontrados no README.md.")
        return

    linhas = [
        "| Pessoa | Commits | Adicionadas | Removidas | Pull Requests | Issues |",
        "|---|---:|---:|---:|---:|---:|"
    ]

    for pessoa, dados in contribuicoes.items():
        linhas.append(
            f"| {pessoa} | "
            f"{dados['commits']} | "
            f"{dados['adicionadas']} | "
            f"{dados['removidas']} | "
            f"{dados['pull_requests']} | "
            f"{dados['issues']} |"
        )

    tabela = "\n".join(linhas)

    antes = conteudo.split(inicio, maxsplit=1)[0]
    depois = conteudo.split(fim, maxsplit=1)[1]

    novo_conteudo = (
        antes
        + inicio
        + "\n"
        + tabela
        + "\n"
        + fim
        + depois
    )

    caminho_readme.write_text(novo_conteudo, encoding="utf-8")

atualizar_readme(contribuicoes)

print("Relatório de contribuições:\n")
for pessoa, dados in contribuicoes.items():
    print(pessoa)
    print(f"  Commits: {dados['commits']}")
    print(f"  Linhas adicionadas: {dados['adicionadas']}")
    print(f"  Linhas removidas: {dados['removidas']}")
    print(f"  Pull Requests: {dados['pull_requests']}")
    print(f"  Issues: {dados['issues']}")
    print()