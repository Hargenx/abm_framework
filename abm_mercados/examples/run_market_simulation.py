from abm.simulation import Simulacao
from market_example import AgenteFinanceiro, MundoMercado

"""
Exemplo de uso do framework ABM para simulação de mercado financeiro.

Este script demonstra como utilizar o framework para criar uma simulação
de mercado financeiro com agentes que compram e vendem ativos.
"""

def main():
    # Criar o mundo de mercado
    mundo = MundoMercado(preco_inicial=100.0, volatilidade=0.05)
    
    # Adicionar agentes financeiros
    for i in range(50):
        mundo.adicionar_agente(AgenteFinanceiro(id_agente=i, saldo_inicial=1000))
    
    # Criar a simulação
    simulacao = Simulacao(mundo=mundo, ciclos=100, paralelo=True)
    
    print("Iniciando simulação de mercado financeiro...")
    print(f"Número de agentes: {len(mundo.agentes)}")
    print(f"Preço inicial: {mundo.preco_atual}")
    print(f"Ciclos de simulação: {simulacao.ciclos}")
    
    # Executar a simulação
    simulacao.executar()
    
    print("\nSimulação concluída!")
    print(f"Preço final: {mundo.preco_atual:.2f}")
    print("Resultados exportados para: resultados.json")

if __name__ == "__main__":
    main()
