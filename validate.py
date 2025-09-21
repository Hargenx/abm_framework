from examples.market_example import AgenteFinanceiro, MundoMercado
from abm_mercados.core.simulation import Simulacao
import unittest
import sys
import os

def executar_testes():
    """Executa os testes unitários do framework."""
    print("Executando testes unitários...")
    
    # Adiciona o diretório raiz ao path para importação dos testes
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Importa e executa os testes
    from tests.test_framework import TestAgenteBase, TestMundoBase, TestSimulacao
    
    # Cria um test suite com todos os testes
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAgenteBase))
    suite.addTest(unittest.makeSuite(TestMundoBase))
    suite.addTest(unittest.makeSuite(TestSimulacao))
    
    # Executa os testes
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    return resultado.wasSuccessful()

def executar_exemplo_mercado():
    """Executa o exemplo de simulação de mercado financeiro."""
    print("\nExecutando exemplo de simulação de mercado financeiro...")
    
    # Criar o mundo de mercado
    mundo = MundoMercado(preco_inicial=100.0, volatilidade=0.05)
    
    # Adicionar agentes financeiros
    for i in range(10):  # Reduzido para teste rápido
        mundo.adicionar_agente(AgenteFinanceiro(id_agente=i, saldo_inicial=1000))
    
    # Criar a simulação
    simulacao = Simulacao(mundo=mundo, ciclos=10, paralelo=True)  # Reduzido para teste rápido
    
    print(f"Número de agentes: {len(mundo.agentes)}")
    print(f"Preço inicial: {mundo.preco_atual}")
    print(f"Ciclos de simulação: {simulacao.ciclos}")
    
    # Executar a simulação
    simulacao.executar()
    
    print(f"Preço final: {mundo.preco_atual:.2f}")
    print("Resultados exportados para: resultados.json")
    
    # Verifica se o arquivo de resultados foi criado
    return os.path.exists("resultados.json")

if __name__ == "__main__":
    print("=== Validação do Framework ABM ===\n")
    
    # Executa os testes
    testes_ok = executar_testes()
    
    # Executa o exemplo
    exemplo_ok = executar_exemplo_mercado()
    
    # Verifica o resultado geral
    if testes_ok and exemplo_ok:
        print("\n✅ Validação concluída com sucesso! O framework está funcionando corretamente.")
    else:
        print("\n❌ Validação falhou. Verifique os erros acima.")
        
    print("\nResumo da validação:")
    print(f"- Testes unitários: {'✅ Passou' if testes_ok else '❌ Falhou'}")
    print(f"- Exemplo de mercado: {'✅ Executado' if exemplo_ok else '❌ Falhou'}")
