# Cartteira-de-Investimentos
Comandos python -m venv venv source venv/bin/activate pip install pandas python-bcb pip install --upgrade pip git status git add . git status git commit -m "primeiros arquivos" git push

Vou explicar o que cada um desses comandos faz:

python -m venv venv: Este comando cria um ambiente virtual Python na pasta atual. O ambiente virtual é um ambiente isolado que permite instalar pacotes e executar código Python sem afetar outros projetos ou o sistema operacional como um todo. venv é o nome do ambiente virtual que está sendo criado.

source venv/bin/activate: Este comando ativa o ambiente virtual que você criou anteriormente com o comando python -m venv venv. Ao ativar o ambiente virtual, qualquer pacote Python que você instalar usando pip será instalado dentro deste ambiente, e o Python que você executa será o Python do ambiente virtual.

pip install pandas python-bcb: pip é o gerenciador de pacotes para Python. Este comando instala os pacotes pandas e python-bcb no ambiente virtual ativo. pandas é uma biblioteca para manipulação e análise de dados, e python-bcb é uma biblioteca para acessar séries temporais do Banco Central do Brasil.

pip install --upgrade pip: Este comando atualiza o pip para a versão mais recente. --upgrade é a opção que diz ao pip para atualizar o pacote (neste caso, o próprio pip) para a última versão disponível.

git status: git é um sistema de controle de versão. O comando git status mostra o status do repositório Git atual. Ele lista quais arquivos foram alterados, quais estão preparados para commit (staged), e quais não estão sendo rastreados pelo Git.

git add .: Este comando adiciona todos os arquivos modificados no diretório atual (e subdiretórios) à área de staging do Git, preparando-os para o próximo commit. O ponto . representa o diretório atual.

git status (repetido): Novamente, este comando é usado para verificar o status do repositório Git após adicionar os arquivos com git add. Ele mostrará os arquivos que estão na área de staging e prontos para serem commitados.

git commit -m "primeiros arquivos": Este comando cria um commit, que é um registro das alterações feitas no repositório. O -m indica que uma mensagem de commit está sendo fornecida na linha de comando. "primeiros arquivos" é a mensagem de commit que descreve as alterações que estão sendo commitadas.

git push: Por fim, git push envia os commits locais para um repositório remoto, como o GitHub. Isso sincroniza o repositório local com o repositório remoto, compartilhando suas alterações com outros colaboradores do projeto.