import os
import subprocess
import glob
import sys
import time

def main():
    # Configurações
    input_dir = 'data/grafos_limpos'
    output_dir = 'resultados_analise_batch'
    script_path = 'analise_rede_trofica.py'
    
    # Verificar se o script de análise existe
    if not os.path.exists(script_path):
        print(f"Erro: Script '{script_path}' não encontrado.")
        return

    # Encontrar todos os arquivos .graphml
    padrao_busca = os.path.join(input_dir, '*.graphml')
    arquivos_grafo = sorted(glob.glob(padrao_busca))
    
    total_arquivos = len(arquivos_grafo)
    
    if total_arquivos == 0:
        print(f"Nenhum arquivo .graphml encontrado em '{input_dir}'.")
        return
        
    print(f"Encontrados {total_arquivos} arquivos para processar em '{input_dir}'.")
    print(f"Resultados serão salvos em '{output_dir}'.")
    print("-" * 50)
    
    # Criar diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    sucessos = 0
    erros = 0
    inicio_total = time.time()
    
    for i, arquivo in enumerate(arquivos_grafo, 1):
        nome_arquivo = os.path.basename(arquivo)
        print(f"\n[{i}/{total_arquivos}] Processando: {nome_arquivo}...")
        
        inicio_arquivo = time.time()
        
        # Construir o comando
        # Usar o mesmo interpretador python que está executando este script
        comando = [sys.executable, script_path, '--arquivo', arquivo, '--output', output_dir]
        
        try:
            # Executar o script e capturar saída
            resultado = subprocess.run(comando, capture_output=True, text=True)
            
            tempo_arquivo = time.time() - inicio_arquivo
            
            if resultado.returncode == 0:
                print(f"  -> Sucesso ({tempo_arquivo:.2f}s)")
                sucessos += 1
            else:
                print(f"  -> Erro ({tempo_arquivo:.2f}s)")
                print(f"  Mensagem de erro:\n{resultado.stderr}")
                erros += 1
                
        except Exception as e:
            print(f"  -> Falha na execução: {e}")
            erros += 1
            
    tempo_total = time.time() - inicio_total
    print("\n" + "=" * 50)
    print(f"Processamento concluído em {tempo_total:.2f}s")
    print(f"Sucessos: {sucessos}")
    print(f"Erros: {erros}")
    print(f"Resultados disponíveis em: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
