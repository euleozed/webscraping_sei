# Documentação do Script de Automalização com Selenium

Este projeto utiliza a biblioteca Selenium para automatizar a coleta de dados de processos administrativos no sistema SEI-RO. Os dados extraídos são armazenados em arquivos CSV.

## Requisitos do Sistema

- **Python 3.8 ou superior**
- **Bibliotecas Python**:
  - pandas
  - selenium
  - webdriver-manager
  - chromedriver-autoinstaller
- **Navegador Edge** e **WebDriver do Edge**
- **Ambiente Windows** com o seguinte diretório configurado para downloads:
  - `C:\Users\<seu_usuario>\OneDrive - Minha Empresa\Aplicativos\gecomp_datalake\downloads`

## Instalação

1. Clone este repositório:
   ```bash
   git clone <url-do-repositorio>
   cd <nome-do-repositorio>
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente no sistema:
   - `USUARIO`: Seu usuário do SEI.
   - `SENHA`: Sua senha do SEI.
   - `ORGAO`: Nome do órgão para seleção no login.

4. Atualize os caminhos do script caso necessário:
   - `csv_path`: Local do arquivo CSV com os números de processos.
   - `download_dir`: Local onde os arquivos serão salvos.

## Uso

### Estrutura do Arquivo CSV de Entrada
O arquivo `numeros_processos.csv` deve conter a coluna:
- `numero_processo`: Números dos processos a serem pesquisados.

Exemplo:
```csv
numero_processo
1234567890
0987654321
...
```

### Execução do Script
1. Execute o script com:
   ```bash
   python nome_do_script.py
   ```

2. O script:
   - Realiza login no SEI usando as credenciais configuradas.
   - Pesquisa os processos listados no arquivo CSV.
   - Extrai os dados da tabela "Consultar Andamento".
   - Salva os dados extraídos em arquivos CSV no diretório configurado.

### Funcionalidades Principais

#### Login Automático
- Preenche automaticamente os campos de login com as variáveis de ambiente configuradas.

#### Pesquisa de Processos
- Navega automaticamente até o campo de pesquisa rápida e realiza a busca pelo número do processo.

#### Extração de Dados da Tabela
- Coleta os dados das tabelas de andamento.
- Salva os resultados em arquivos CSV.
- Trata tabelas com múltiplas páginas.

#### Tratamento de Erros
- Lida com problemas como falta de botões, tempo limite excedido e elementos não encontrados.

### Arquivos Gerados
Os arquivos CSV são salvos no formato `processo_<numero_processo>.csv` no diretório de downloads configurado.

## Configuração do Selenium

### WebDriver
O script utiliza o WebDriver para o navegador Edge. Ele é automaticamente instalado com a biblioteca `webdriver-manager`.

### Configurações de Download
O diretório de downloads é configurado para evitar prompt de confirmação, garantindo que os arquivos sejam salvos automaticamente.

## Possíveis Problemas e Soluções

1. **Erro de Timeout ao Carregar Páginas**:
   - Verifique a estabilidade da conexão com a internet.
   - Aumente o tempo limite nas chamadas `WebDriverWait`.

2. **Login Falhando**:
   - Confirme que as variáveis de ambiente `USUARIO`, `SENHA` e `ORGAO` estão configuradas corretamente.

3. **Problemas com WebDriver**:
   - Certifique-se de que o navegador Edge está instalado e atualizado.
   - Reinstale o WebDriver executando:
     ```bash
     pip uninstall webdriver-manager
     pip install webdriver-manager
     ```

4. **Elementos Não Encontrados**:
   - Verifique se a interface do SEI foi alterada. Neste caso, atualize os seletores utilizados no script.

## Contribuição
Contribuições são bem-vindas! Para contribuir:
1. Fork este repositório.
2. Crie uma branch para suas modificações:
   ```bash
   git checkout -b minha-nova-feature
   ```
3. Submeta um Pull Request.

## Licença
Este projeto está licenciado sob a [Licença MIT](LICENSE).

---

### Contato
Em caso de dúvidas ou problemas, entre em contato com o mantenedor do projeto.

