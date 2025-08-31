import unittest
from abm.agent import AgenteBase
from abm.world import MundoBase
from abm.simulation import Simulacao
import os
import json

class TestAgenteBase(unittest.TestCase):
    """Testes para a classe AgenteBase."""
    
    def test_inicializacao(self):
        """Testa se o agente é inicializado corretamente."""
        agente = AgenteBase(id_agente=1)
        self.assertEqual(agente.id, 1)
        self.assertEqual(agente.recursos, {})
    
    def test_metodos_abstratos(self):
        """Testa se os métodos abstratos lançam NotImplementedError."""
        agente = AgenteBase(id_agente=1)
        mundo = MundoBase()
        
        with self.assertRaises(NotImplementedError):
            agente.decidir(mundo)
            
        with self.assertRaises(NotImplementedError):
            agente.agir(mundo)


class TestMundoBase(unittest.TestCase):
    """Testes para a classe MundoBase."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.mundo = MundoBase()
        
    def test_inicializacao(self):
        """Testa se o mundo é inicializado corretamente."""
        self.assertEqual(self.mundo.agentes, [])
        self.assertEqual(self.mundo.recursos, {})
        self.assertEqual(self.mundo.tempo, 0)
        self.assertEqual(self.mundo.coletor_dados, [])
    
    def test_adicionar_agente(self):
        """Testa se um agente é adicionado corretamente ao mundo."""
        agente = AgenteBase(id_agente=1)
        self.mundo.adicionar_agente(agente)
        self.assertEqual(len(self.mundo.agentes), 1)
        self.assertEqual(self.mundo.agentes[0], agente)
    
    def test_coletar_dados(self):
        """Testa se os dados são coletados corretamente."""
        agente = AgenteBase(id_agente=1)
        self.mundo.adicionar_agente(agente)
        self.mundo.coletar_dados()
        
        self.assertEqual(len(self.mundo.coletor_dados), 1)
        snapshot = self.mundo.coletor_dados[0]
        
        self.assertEqual(snapshot['tempo'], 0)
        self.assertEqual(snapshot['estado_mundo'], {})
        self.assertEqual(len(snapshot['estado_agentes']), 1)
        self.assertEqual(snapshot['estado_agentes'][0]['id'], 1)
    
    def test_exportar_resultados(self):
        """Testa se os resultados são exportados corretamente."""
        agente = AgenteBase(id_agente=1)
        self.mundo.adicionar_agente(agente)
        self.mundo.coletar_dados()
        
        # Arquivo temporário para teste
        arquivo_temp = "teste_resultados.json"
        self.mundo.exportar_resultados(arquivo_temp)
        
        # Verifica se o arquivo foi criado
        self.assertTrue(os.path.exists(arquivo_temp))
        
        # Verifica o conteúdo do arquivo
        with open(arquivo_temp, 'r') as f:
            dados = json.load(f)
            
        self.assertEqual(len(dados), 1)
        self.assertEqual(dados[0]['tempo'], 0)
        
        # Limpa o arquivo temporário
        os.remove(arquivo_temp)


class AgenteSimples(AgenteBase):
    """Implementação simples de agente para testes."""
    
    def __init__(self, id_agente):
        super().__init__(id_agente)
        self.decisao = None
        self.acao = None
    
    def decidir(self, ambiente):
        self.decisao = f"Decisão do agente {self.id}"
    
    def agir(self, ambiente):
        self.acao = f"Ação do agente {self.id}"
        ambiente.recursos[f'acao_agente_{self.id}'] = True


class TestSimulacao(unittest.TestCase):
    """Testes para a classe Simulacao."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.mundo = MundoBase()
        for i in range(5):
            self.mundo.adicionar_agente(AgenteSimples(i))
    
    def test_inicializacao(self):
        """Testa se a simulação é inicializada corretamente."""
        simulacao = Simulacao(self.mundo, ciclos=10, paralelo=True)
        self.assertEqual(simulacao.mundo, self.mundo)
        self.assertEqual(simulacao.ciclos, 10)
        self.assertTrue(simulacao.paralelo)
    
    def test_executar_ciclo_sequencial(self):
        """Testa a execução de um ciclo sequencial."""
        simulacao = Simulacao(self.mundo, ciclos=1, paralelo=False)
        simulacao.executar_ciclo()
        
        # Verifica se todos os agentes agiram
        for i, agente in enumerate(self.mundo.agentes):
            self.assertEqual(agente.decisao, f"Decisão do agente {i}")
            self.assertEqual(agente.acao, f"Ação do agente {i}")
            self.assertTrue(self.mundo.recursos.get(f'acao_agente_{i}', False))
        
        # Verifica se os dados foram coletados
        self.assertEqual(len(self.mundo.coletor_dados), 1)
    
    def test_executar_ciclo_paralelo(self):
        """Testa a execução de um ciclo paralelo."""
        simulacao = Simulacao(self.mundo, ciclos=1, paralelo=True)
        simulacao.executar_ciclo()
        
        # Verifica se todos os agentes agiram
        for i, agente in enumerate(self.mundo.agentes):
            self.assertEqual(agente.decisao, f"Decisão do agente {i}")
            self.assertEqual(agente.acao, f"Ação do agente {i}")
            self.assertTrue(self.mundo.recursos.get(f'acao_agente_{i}', False))
        
        # Verifica se os dados foram coletados
        self.assertEqual(len(self.mundo.coletor_dados), 1)
    
    def test_executar_simulacao_completa(self):
        """Testa a execução completa da simulação."""
        # Arquivo temporário para teste
        arquivo_temp = "teste_resultados.json"
        
        # Configura o mundo para usar o arquivo temporário
        original_exportar = self.mundo.exportar_resultados
        self.mundo.exportar_resultados = lambda caminho=arquivo_temp: original_exportar(caminho)
        
        # Executa a simulação
        simulacao = Simulacao(self.mundo, ciclos=3, paralelo=True)
        simulacao.executar()
        
        # Verifica se os dados foram coletados para todos os ciclos
        self.assertEqual(len(self.mundo.coletor_dados), 3)
        
        # Verifica se o arquivo de resultados foi criado
        self.assertTrue(os.path.exists(arquivo_temp))
        
        # Limpa o arquivo temporário se existir
        if os.path.exists(arquivo_temp):
            os.remove(arquivo_temp)


if __name__ == '__main__':
    unittest.main()
