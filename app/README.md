
# Voos Decolar CLI

Este programa consulta preços de voos no site da Decolar.com para um trecho específico (ida ou volta) e imprime os resultados de forma legível no terminal.

---

## Funcionalidades

- Consulta preços de voos em tempo real via API da Decolar.
- Recebe três argumentos: `from`, `to` e `date`.
- Imprime no terminal a melhor companhia e preço.
- Formato de saída amigável, com linhas separadoras para melhor leitura.
- Pode ser chamado quantas vezes quiser para diferentes trechos (ida/volta).

---

## Pré-requisitos

- Python 3.10 ou superior
- [requests](https://pypi.org/project/requests/)
- [PyInstaller](https://www.pyinstaller.org/) (para gerar o executável)

Instale os pacotes necessários com:

```bash
pip install requests pyinstaller
```

---

## Estrutura do projeto

```
.
├── main.py          # Código principal
└── README.md        # Este arquivo
```

---

## Como gerar o executável

Use o PyInstaller para criar um executável de uma única arquivo:

```bash
playwright install
#pyinstaller --onefile --name=voos main.py
pyinstaller --add-data "/Users/raimundo.botelho/Library/Caches/ms-playwright:ms-playwright" --name=voos main.py
```

Após a execução, o executável estará em:

```
./dist/voos   # Linux/macOS
.\dist/voos.exe # Windows
```

---

## Como chamar o executável

O programa deve ser chamado passando **três argumentos**:  

```
<from> <to> <date>
```

Exemplo de uso:

```bash
# Consulta ida
./dist/voos SAO BEL 2026-01-24

# Consulta volta
./dist/voos BEL SAO 2026-01-30
```

No Windows:

```cmd
dist\voos.exe SAO BEL 2026-01-24
dist\voos.exe BEL SAO 2026-01-30
```

---

### Saída esperada

```
---------------------------------------------------------------------------
✈️ SAO -> BEL | Data: 2026-01-24 | Companhia: LATAM | Melhor preço: R$ 1200
---------------------------------------------------------------------------
```

---

### Observações

- O programa faz apenas **uma consulta por execução**.  
- Para ida e volta, execute o programa duas vezes com os trechos correspondentes.  
- Certifique-se de ter conexão com a internet, pois ele acessa a API da Decolar em tempo real.
