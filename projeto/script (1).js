form.addEventListener('submit', async function(event) {
    event.preventDefault();

    const submitButton = form.querySelector('.submit-button');
    submitButton.disabled = true;
    submitButton.textContent = 'Enviando...';

    // 1. Cria um objeto FormData para empacotar os dados e a foto
    const formData = new FormData();
    
    // 2. Adiciona todos os campos de texto ao FormData
    formData.append('nome', document.getElementById('nome').value);
    formData.append('cpf', document.getElementById('cpf').value);
    formData.append('nascimento', document.getElementById('nascimento').value);
    formData.append('celular', document.getElementById('celular').value);
    formData.append('email', document.getElementById('email').value);
    formData.append('plano', document.getElementById('plano').value);
    formData.append('dataInicio', document.getElementById('inicio').value);

    // 3. Adiciona o arquivo da foto, se existir
    if (photoInput.files[0]) {
        formData.append('fotoAluno', photoInput.files[0]);
    }

    try {
        // Substitua pela URL da sua API de cadastro
        const response = await fetch('http://seu-backend.com/api/alunos/cadastrar', {
            method: 'POST',
            body: formData, // Envia o objeto FormData
            // IMPORTANTE: Não defina o header 'Content-Type'. O navegador fará isso automaticamente
            // com o 'boundary' correto para 'multipart/form-data'.
        });

        const result = await response.json(); // Espera a resposta do back-end

        if (response.ok) {
            // Supondo que seu back-end retorna a matrícula em: result.novaMatricula
            showFeedback(`Aluno cadastrado com sucesso! <br><strong>Matrícula: ${result.novaMatricula}</strong>`, 'success');
            form.reset();
            photoPreview.innerHTML = '<span class="upload-icon">+</span><span>Enviar Foto</span>';
        } else {
            // Supondo que seu back-end retorna a mensagem de erro em: result.message
            showFeedback(`Erro ao cadastrar: ${result.message}`, 'error');
        }

    } catch (error) {
        console.error("Erro de rede:", error);
        showFeedback('Não foi possível conectar ao servidor.', 'error');
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Cadastrar Aluno';
    }
});