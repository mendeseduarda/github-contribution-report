import subprocess
from collections import Counter

resultado = subprocess.run(
    [
        "git",
        "log", #consulta o histórico de commits
        "--all", #todas as branchs
        "--format=%an|%ae|%H|%s" #infos do commit autor, email, hash e mensagem
    ],
    capture_output=True,
    text=True,
    check=True
)

commits_por_pessoa = Counter()

for linha in resultado.stdout.splitlines():
    partes = linha.split("|", maxsplit=3)

    if len(partes) != 4:
        continue

    nome, email, hash_commit, mensagem = partes

    pessoa = f"{nome} <{email}>"
    commits_por_pessoa[pessoa] += 1

print("Commits por pessoa:\n")

for pessoa, quantidade in commits_por_pessoa.most_common():
    print(f"{pessoa}: {quantidade} commit(s)")