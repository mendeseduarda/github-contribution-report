import json
from pathlib import Path
import subprocess
from collections import defaultdict

arquivo_autores = Path("config/autores.json")

if arquivo_autores.exists():
    with arquivo_autores.open("r", encoding="utf-8") as arquivo:
        autores = json.load(arquivo)
else:
    autores = {}


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
        "removidas": 0
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
        partes = linha.split("\t")

        if len(partes) != 3:
            continue

        adicionadas, removidas, arquivo = partes

        # Arquivos binários podem aparecer como "-"
        if adicionadas.isdigit():
            contribuicoes[pessoa_atual]["adicionadas"] += int(adicionadas)

        if removidas.isdigit():
            contribuicoes[pessoa_atual]["removidas"] += int(removidas)

print("Relatório de contribuições:\n")

for pessoa, dados in contribuicoes.items():
    print(f"{pessoa}")
    print(f"  Commits: {dados['commits']}")
    print(f"  Linhas adicionadas: {dados['adicionadas']}")
    print(f"  Linhas removidas: {dados['removidas']}")
    print()