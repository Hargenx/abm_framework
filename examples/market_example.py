from abm_framework.abm.agent import AgenteBase
from abm_framework.abm.world import MundoBase
from typing import TYPE_CHECKING, Dict, List, Any

class AgenteFinanceiro(AgenteBase):
    """
    Implementação de um agente financeiro para simulação de mercado.
    
    Este agente pode comprar e vender ativos com base em uma estratégia simples.
    """
    
    def __init__(self, id_agente: int, saldo_inicial: float = 1000.0) -> None:
        """
        Inicializa um agente financeiro com saldo inicial.
        
        Args:
            id_agente: Identificador único do agente
            saldo_inicial: Quantidade inicial de dinheiro disponível
        """
        super().__init__(id_agente)
        self.recursos = {
            'saldo': saldo_inicial,
            'ativos': {}
        }
        self.ultima_acao = None
    
    def decidir(self, ambiente: 'MundoMercado') -> None:
        """
        Decide se vai comprar, vender ou manter posição com base no estado do mercado.
        
        Implementa uma estratégia simples baseada na tendência de preços.
        
        Args:
            ambiente: O mundo de mercado onde o agente opera
        """
        # Estratégia simples: compra se preço está subindo, vende se está caindo
        if not ambiente.historico_precos:
            self.ultima_acao = 'esperar'
            return
            
        preco_atual = ambiente.preco_atual
        preco_anterior = ambiente.historico_precos[-1] if len(ambiente.historico_precos) > 1 else preco_atual
        
        # Verifica se tem saldo para comprar
        tem_saldo = self.recursos['saldo'] >= preco_atual
        
        # Verifica se tem ativos para vender
        tem_ativos = self.recursos['ativos'].get('acao', 0) > 0
        
        # Decide com base na tendência
        if preco_atual > preco_anterior and tem_saldo:
            self.ultima_acao = 'comprar'
        elif preco_atual < preco_anterior and tem_ativos:
            self.ultima_acao = 'vender'
        else:
            self.ultima_acao = 'esperar'
    
    def agir(self, ambiente: 'MundoMercado') -> None:
        """
        Executa a ação decidida anteriormente (comprar, vender ou esperar).
        
        Args:
            ambiente: O mundo de mercado onde o agente opera
        """
        if self.ultima_acao == 'comprar':
            # Tenta comprar uma unidade do ativo
            if self.recursos['saldo'] >= ambiente.preco_atual:
                self.recursos['saldo'] -= ambiente.preco_atual
                self.recursos['ativos']['acao'] = self.recursos['ativos'].get('acao', 0) + 1
                ambiente.registrar_compra()
                
        elif self.ultima_acao == 'vender':
            # Tenta vender uma unidade do ativo
            if self.recursos['ativos'].get('acao', 0) > 0:
                self.recursos['saldo'] += ambiente.preco_atual
                self.recursos['ativos']['acao'] = self.recursos['ativos'].get('acao', 0) - 1
                ambiente.registrar_venda()


class MundoMercado(MundoBase):
    """
    Implementação de um ambiente de mercado financeiro.
    
    Este mundo simula um mercado simples com um único ativo cujo preço
    varia com base na oferta e demanda dos agentes.
    """
    
    def __init__(self, preco_inicial: float = 100.0, volatilidade: float = 0.05) -> None:
        """
        Inicializa um mundo de mercado com preço inicial e volatilidade.
        
        Args:
            preco_inicial: Preço inicial do ativo
            volatilidade: Fator de volatilidade do preço (0.0 a 1.0)
        """
        super().__init__()
        self.preco_atual = preco_inicial
        self.volatilidade = volatilidade
        self.historico_precos: List[float] = []
        self.recursos = {
            'preco': preco_inicial,
            'compras': 0,
            'vendas': 0
        }
    
    def registrar_compra(self) -> None:
        """Registra uma compra e atualiza o contador no mundo."""
        self.recursos['compras'] += 1
    
    def registrar_venda(self) -> None:
        """Registra uma venda e atualiza o contador no mundo."""
        self.recursos['vendas'] += 1
    
    def atualizar(self) -> None:
        """
        Atualiza o estado do mercado após cada ciclo.
        
        Calcula o novo preço com base nas compras e vendas realizadas
        e na volatilidade do mercado.
        """
        # Guarda o preço atual no histórico
        self.historico_precos.append(self.preco_atual)
        
        # Calcula o novo preço com base na oferta e demanda
        compras = self.recursos['compras']
        vendas = self.recursos['vendas']
        
        # Fator de pressão de preço baseado em compras e vendas
        if compras + vendas > 0:
            pressao = (compras - vendas) / (compras + vendas)
        else:
            pressao = 0
            
        # Adiciona um componente aleatório (volatilidade)
        import random
        fator_aleatorio = random.uniform(-self.volatilidade, self.volatilidade)
        
        # Calcula a variação de preço
        variacao = self.preco_atual * (pressao * 0.1 + fator_aleatorio)
        
        # Atualiza o preço
        self.preco_atual += variacao
        self.recursos['preco'] = self.preco_atual
        
        # Reseta contadores para o próximo ciclo
        self.recursos['compras'] = 0
        self.recursos['vendas'] = 0
        
        # Incrementa o tempo
        self.tempo += 1
