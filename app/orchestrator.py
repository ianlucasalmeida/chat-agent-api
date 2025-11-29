import logging
from app.subprograms.agent_factory import create_agent_instance

logger = logging.getLogger("Orchestrator")

async def run_chat_pipeline(message: str) -> str:
    logger.info("--- Iniciando Pipeline de Chat (Strands Native) ---")
    
    try:
        # 1. Instancia Agente
        agent = create_agent_instance()
        
        # 2. Execução
        logger.info(f"Enviando para o Agente: {message}")
        
        # O SDK é chamado diretamente como uma função
        result = agent(message)
        
        # 3. Extração da Resposta
        # A documentação diz: print(result.message)
        # O objeto result contém todo o histórico, pegamos a última resposta do assistente.
        final_text = ""
        
        # Verifica se result tem o atributo message (Padrão Strands)
        if hasattr(result, "message"):
             # Dependendo da versão, pode ser result.message ou result.message.content
             # Vamos converter para string para garantir
             final_text = str(result.message)
             
             # Log de métricas (bônus da documentação que você mandou!)
             if hasattr(result, "metrics"):
                 summary = result.metrics.get_summary()
                 total_time = summary.get("total_duration", 0)
                 logger.info(f"📊 Métricas: Levou {total_time:.2f}s | Tokens usados: {summary.get('accumulated_usage', {}).get('totalTokens', 0)}")
        else:
            final_text = str(result)

        logger.info("Pipeline finalizado.")
        return final_text
        
    except Exception as e:
        logger.error(f"Falha crítica no Pipeline: {e}")
        raise e