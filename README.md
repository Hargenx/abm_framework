# ABM Framework

Framework simples e modular para simulações baseadas em agentes (Agent-Based Modeling - ABM), com suporte a paralelização e coleta de dados.

## Instalação

```bash
pip install -e .
```

## Uso

```python
from abm_framework.abm import AgenteBase, MundoBase, Simulacao

# Criar uma classe de mundo personalizada
class MeuMundo(MundoBase):
    def atualizar(self):
        # Lógica específica de atualização do mundo
        self.tempo += 1

# Criar uma classe de agente personalizada
class MeuAgente(AgenteBase):
    def decidir(self, ambiente):
        # Lógica de decisão do agente
        pass
        
    def agir(self, ambiente):
        # Lógica de ação do agente
        pass

# Criar o mundo
mundo = MeuMundo()

# Criar os agentes
agentes = [MeuAgente(i) for i in range(10)]
for agente in agentes:
    mundo.adicionar_agente(agente)

# Criar a simulação
simulacao = Simulacao(mundo, ciclos=100, paralelo=True)

# Executar a simulação
simulacao.executar()
```

Para exemplos mais detalhados, consulte a pasta `examples/`.

---

### ✅ Progresso final

- [x] Estrutura modular
- [x] Agente generalista
- [x] Mundo generalista
- [x] Paralelização configurável
- [x] Exportação de dados
- [x] Exemplo funcional
- [x] Empacotamento como biblioteca com `setup.py`
- [x] Pronto para publicar no GitHub ou PyPI 🔥

---
