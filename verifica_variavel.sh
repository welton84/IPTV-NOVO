#!/bin/bash

# Nome do script: verifica_variavel.sh
# Autor: Seu Nome
# Descrição: Verifica se a variável está vazia ou não e imprime uma mensagem.

# Exemplo de variável (modifique conforme necessário)
VAR="$1"  # Valor passado como argumento

# Verifica se a variável está vazia
if [ -z "$VAR" ]; then
    echo "A variável está vazia."
else
    echo "A variável não está vazia: $VAR"
fi
