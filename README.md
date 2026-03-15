<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f0c29,50:302b63,100:24243e&height=200&section=header&text=Sudokor&fontSize=55&fontColor=ffffff&fontAlignY=38&desc=Python%20%E2%80%A2%20OpenCV%20%E2%80%A2%20Tesseract%20%E2%80%A2%20PyAutoGUI&descAlignY=58&descSize=18&descColor=a78bfa" width="100%"/>

</div>

<div align="center">

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1000&color=A78BFA&center=true&vCenter=true&width=700&lines=Bot+que+resolve+Sudoku+automaticamente;Captura+de+tela+%2B+OCR+com+Tesseract;Solver+AC-3+%2B+Backtracking+com+MRV;Automa%C3%A7%C3%A3o+de+mouse+e+teclado)](https://git.io/typing-svg)

</div>

---

<div align="center">

<img src="https://img.shields.io/badge/Sobre-302b63?style=for-the-badge&logoColor=white" />

<br/><br/>

Auto-solver para **Microsoft Sudoku** no Windows. Captura a tela do jogo, detecta o grid com OpenCV, lê os dígitos com Tesseract OCR, resolve o puzzle com AC-3 + Backtracking e preenche automaticamente as células via mouse e teclado — com sistema de double-check por análise de pixels.

</div>

---

<div align="center">

<img src="https://img.shields.io/badge/Stack-302b63?style=for-the-badge&logo=codeigniter&logoColor=white" />

<br/><br/>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
<br/>
![Tesseract](https://img.shields.io/badge/Tesseract_OCR-333333?style=for-the-badge&logo=googlecloud&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-306998?style=for-the-badge&logo=python&logoColor=white)
![PyAutoGUI](https://img.shields.io/badge/PyAutoGUI-A78BFA?style=for-the-badge&logo=python&logoColor=white)

</div>

<br/>

<div align="center">

<img src="https://img.shields.io/badge/Como_Funciona-302b63?style=for-the-badge&logo=googlechat&logoColor=white" />

<br/><br/>

```text
Screenshot → OpenCV Grid Detection → Tesseract OCR
                        ↓
                 9×9 Board Array
                        ↓
   AC-3 Constraint Propagation → Backtracking (MRV)
                        ↓
                   Solved Board
                        ↓
       PyAutoGUI → Click + Type → Puzzle Solved ✓
                        ↓
         Double-check via pixel analysis
```

</div>

---

<div align="center">

<img src="https://img.shields.io/badge/Como_Rodar_Localmente-302b63?style=for-the-badge&logo=python&logoColor=white" />

</div>

<br/>

> **Pré-requisito:** instale o [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) e certifique-se de que o caminho `C:\Program Files\Tesseract-OCR\tesseract.exe` está correto.

```bash
# Clone o repositório
git clone https://github.com/Brrxis/Sudokor.git

# Entre na pasta
cd Sudokor/sudoku-bot

# Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute o bot (modo normal — 5s para focar o jogo)
python -m src.bot

# Ou em modo rápido
python -m src.bot --mode fast
```

---

<div align="center">

<img src="https://img.shields.io/badge/Features-302b63?style=for-the-badge&logo=googlechat&logoColor=white" />

<br/><br/>

✅ Captura automática da janela do Microsoft Sudoku  
✅ Detecção do grid com OpenCV + Canny  
✅ OCR multi-pass com Tesseract (4 tentativas de fallback)  
✅ Solver AC-3 + Backtracking com heurística MRV  
✅ Preenchimento automático via PyAutoGUI  
✅ Double-check com análise de pixels pós-preenchimento  
✅ Modo normal e modo rápido  
✅ Validação do board antes e depois da resolução  

</div>

---

<div align="center">

<img src="https://img.shields.io/badge/Contato-302b63?style=for-the-badge&logo=googlechat&logoColor=white" />

<br/><br/>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/enzopontonidev/)
[![Portfolio](https://img.shields.io/badge/Portf%C3%B3lio-A78BFA?style=for-the-badge&logo=vercel&logoColor=white)](https://www.enzopontoni.work/)
[![Email](https://img.shields.io/badge/Email-6D4AFF?style=for-the-badge&logo=protonmail&logoColor=white)](mailto:enzopontoni@proton.me)

</div>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:24243e,50:302b63,100:0f0c29&height=120&section=footer" width="100%"/>

## 💻 Requisitos do Sistema

- **Sistema Operacional:** Windows 10 ou 11
- **Linguagem:** Python 3.10+
- **Aplicação Alvo:** [Microsoft Sudoku](https://apps.microsoft.com/store/detail/microsoft-sudoku/9WZDNCRFHV60)
- **Tesseract OCR:** É necessário ter o Tesseract instalado no Windows e configurado no PATH do sistema.
  - Baixe o instalador aqui: [Tesseract OCR for Windows](https://github.com/UB-Mannheim/tesseract/wiki)

---

## 🚀 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/sudoku-bot
   cd sudoku-bot
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🎮 Como Usar

Abra o Microsoft Sudoku, inicie uma partida (deixe o tabuleiro visível) e execute o bot pelo terminal:

**Resolver apenas 1 puzzle (Velocidade Normal):**
```bash
python src/bot.py
```

**Modo Rápido (Preenchimento Turbo):**
```bash
python src/bot.py --mode fast
```

**Resolver N puzzles em sequência:**
```bash
python src/bot.py --loop 5
```

O bot aguardará 3 segundos para que você possa focar a janela do jogo antes de iniciar a captura e resolução.

---

## 📂 Estrutura do Projeto

```text
sudoku-bot/
├── src/
│   ├── __init__.py
│   ├── solver.py        ← Motor de IA (AC-3 + Backtracking + MRV)
│   ├── vision.py        ← Captura de tela + detecção de grid + OCR
│   ├── automator.py     ← Controle de mouse/teclado
│   └── bot.py           ← Orquestrador principal
├── tests/
│   ├── test_solver.py   ← Testes unitários do solver
│   └── test_vision.py   ← Testes com imagens mockadas
├── assets/
│   └── demo/            ← Demonstrações e screenshots
├── requirements.txt
├── setup.py
└── README.md
```

---

## 🔬 Algoritmo Explicado

O coração analítico deste bot reside no `src/solver.py`, que utiliza a clássica abordagem de Constraint Satisfaction Problem (CSP) em 2 etapas:

1. **AC-3 (Arc Consistency Algorithm #3):** Antes de testar possibilidades, o algoritmo propaga imediatamente as restrições ao longo do tabuleiro. Se uma célula tem apenas um valor possível, esse valor é removido dos domínios de todos os seus "vizinhos" (linha, coluna e quadrante 3x3 correspondente). Isso simplifica drasticamente a árvore de busca.
2. **Backtracking com MRV (Minimum Remaining Values):** Caso o AC-3 não consiga resolver completamente o tabuleiro (o que ocorre em puzzles mais difíceis, conhecidos como "Evil"), o bot utiliza busca não informada através de backtracking. A diferença? Ele sempre escolhe "chutar" na célula com o **menor número de candidatos restantes** (heurística MRV), garantindo ramificações curtas e rápidas.

---

## ⚠️ Troubleshooting

- **A tela inteira está sendo capturada em vez da janela.**
  *Causa:* O jogo pode estar minimizado no momento da execução inicial ou em tela cheia obscura.
  *Solução:* Certifique-se de que a janela "Microsoft Sudoku" está aberta no modo janela normal visível e selecionada.

- **Erros estranhos ou travamentos no OCR.**
  *Causa:* O executável do Tesseract não foi achado no path.
  *Solução:* Garanta a instalação através do [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) e configure a pasta de instalação nas Variáveis de Ambiente do seu Windows.

- **O mouse clica fora do lugar.**
  *Solução:* Tente não interagir com o mouse ou alterar a resolução/monitor da tela durante a execução do bot, pois as coordenadas são calculadas com base na captura efetuada em tempo real.

---

## 📜 License

Distribuído sob a licença [MIT](https://choosealicense.com/licenses/mit/). Veja `LICENSE` para mais informações.
